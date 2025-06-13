from email.message import EmailMessage
from smtplib import SMTP, SMTPException

import pyotp
import requests
from dotenv import dotenv_values
from flask import Flask, request, jsonify, render_template
from sqlalchemy import desc

from models import SessionLocal, PostRecord, OTPRecord

config = dotenv_values('.env')

def generate_otp():
    totp = pyotp.TOTP(config['OTP_PRIVATE_KEY'])
    return int(totp.now())


def verify(task_id, code):
    session = SessionLocal()
    record = session.query(OTPRecord).filter_by(task_id=task_id).order_by(desc('timestamp')).order_by(
        desc('id')).first()
    print(f"OTP is {record.code}")
    if (not record) or (record.code != code):
        session.close()
        return False
    else:
        session.close()
        return True


def retrieve_post(task_id, full=False):
    session = SessionLocal()
    record = session.query(PostRecord).filter_by(id=int(task_id)).first()
    if not record:
        session.close()
        return {}

    return record.dict() if full else record.get_post()




def get_config_state(flag):
    return 'ENABLED' if flag == 'True' else 'DISABLED'



# noinspection PyBroadException
def queue_new_post(task_id):
    try:
        res = requests.post(f"{config['LLM_SERVICE']}/process-new-task", json={"task_id": task_id})
        if res.status_code != 200:
            print(f"Failed to queue new post: RES/{res.status_code}")
            return False
    except Exception as e:
        print(f"Failed to queue new post: EXP/{e}")
        return False
    return True


def send_mail(content, subject, to_addr, from_addr):
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr

    try:
        with SMTP(host=config['EMAIL_SERVER'], port=int(config['EMAIL_PORT'])) as s:
            s.starttls()
            s.login(config['EMAIL_USER'], config['EMAIL_PASSWORD'])
            s.sendmail(config['EMAIL_USER'], config['EMAIL_USER'], msg.as_string())
    except SMTPException as e:
        print("failed to send email: ", e)
        return False
    except Exception as e:
        print("failed to proceed: ", e)
        return False
    else:
        return True

def request_new_post(task_id):
    content = "New Post has been requested. Please approve to queue the post to Generation-Service"
    content += f"Click here to proceed: {config['APP_SERVICE'] + "/init-approve/" + str(task_id)}"
    subject = "New Post Request"
    to_addr = config['MARKETING_LEITER_EMAIL_ADDRESS']
    from_addr = config['EMAIL_USER']

    return send_mail(content, subject, to_addr, from_addr)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/config')
def hello_world():
    STATE = {
        'version': 'v4.19.0',
        'config': {
            'LLM': get_config_state(config['ENABLE_LLM_GENERATION']),
            'EMAIL': get_config_state(config['ENABLE_EMAIL']),
            'SCHEDULER': get_config_state(config['ENABLE_SCHEDULED_GENERATION']),
            'NEW_POST': get_config_state(config['ENABLE_NEW_POST']),
            'DEBUG': get_config_state(config['ENABLE_DEBUG']),
        }
    }
    return jsonify(STATE)


@app.route('/new-post')
def init_new_post():
    return render_template('new-post.html')

@app.route("/request-new-post", methods=["POST"])
def request_new_post_init():
    data = request.form

    if config['ENABLE_NEW_POST'] == 'False':
        print("New post not enabled")
        return jsonify({"status": "-2003"}), 200

    record = PostRecord(
        event_title=data["event_title"],
        date=data["date"],
        description=data["description"],
        good=data["good"],
        bad=data["bad"],
        goal=data["goal"],
        status="queued"
    )

    session = SessionLocal()
    session.add(record)
    session.commit()
    task_id = record.id
    session.close()

    ok = request_new_post(int(task_id))
    if not ok:
        return render_template('request-notification.html', title="Oopsie!", msg="Something went wrong. We will look into it.")

    print(f"Requested new post: {task_id}")
    return render_template('request-notification.html', msg="Your request has been notified to Marketing team.", title="Danke!")

@app.route('/mockup')
def mockup():
    return render_template('queue-new-post.html', post={})

@app.route("/init-approve/<int:task_id>")
def init_approve(task_id):
    # gen code / return html to input code
    code = generate_otp()
    record = OTPRecord(
        code=code,
        task_id=task_id,
    )
    session = SessionLocal()
    session.add(record)
    session.commit()
    session.close()

    ok = send_mail(
        f"Approval OTP: {code}",
        "Hier ist OTP",
        config["EMAIL_USER"],
        config["EMAIL_USER"],
    )
    if not ok:
        return jsonify({"status": "failed"}), 500

    return render_template('init-approve.html', task_id=task_id)


@app.route("/approve/<int:task_id>", methods=["POST"])
def approve(task_id):
    code = int(request.form['otp'])
    print(f"Approval request for {task_id}: {code}")
    ok = verify(task_id, code)
    if not ok:
        return jsonify({"status": "failed"}), 403

    post = retrieve_post(task_id, full=True)
    return render_template('queue-new-post.html', post=post, task_id=task_id)

@app.route("/queue-new-post", methods=['POST'])
def new_post():
    form = request.form
    print(f"new post form: {form}")
    task_id = form['id']
    session = SessionLocal()
    post = session.query(PostRecord).filter_by(id=task_id).first()

    if config['ENABLE_NEW_POST'] == 'False':
        print("New post not enabled")
        return jsonify({"status": "-2003"}), 200

    if post:
        post.event_title = form['event_title']
        post.date = form['date']
        post.description = form['description']
        post.good = form['good']
        post.bad = form['bad']
        post.goal = form['goal']
        post.instructions = form['instructions']
        post.status = "approved"

        session.commit()

    ok = queue_new_post(task_id)
    if not ok:
        return 'Something went wrong'

    print(f"Approved new post: {task_id}")
    return 'Queued. You will be notified once generation is completed.'

@app.route("/webhook/update-post-status", methods=['POST'])
def update_post_status():
    task_id = request.json['task_id']
    print("new post update: ", task_id)
    data = retrieve_post(task_id)
    if not data:
        print(f"Failed to retrieve task data: {task_id}")
        return jsonify({"status": "failed"}), 500

    if config['ENABLE_EMAIL'] == 'False':
        print("Email not enabled")
        print("Notification for task: ", task_id)
        return jsonify({"status": "success"}), 200

    msg_content = "Demo Text here due to LLM being disabled; otherwise you will receive the generated Text." \
        if data['post'] is None \
        else data['post']

    ok = send_mail(msg_content,
                   f"New Post Generated: {data['event_title']}",
                   "birnadin.anton-robert-clive@stud.th-deg.de",
                   f"LLM <birnadin.anton-robert-clive@stud.th-deg.de>",
                   )
    return jsonify({"status": "success"}) if ok else jsonify({"status": "failed"})

@app.route('/posts', methods=['GET'])
def get_posts():
    session = SessionLocal()
    posts = session.query(PostRecord).all()

    return render_template('posts.html', posts=posts)

if __name__ == '__main__':
    DEBUG = config['ENABLE_DEBUG'] == 'True'
    app.run(debug=DEBUG)

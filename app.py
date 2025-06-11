from email.message import EmailMessage
from smtplib import SMTP, SMTPException

import requests
from dotenv import dotenv_values
from flask import Flask, request, jsonify

from models import SessionLocal, PostRecord

config = dotenv_values('.env')

def retrieve_post(task_id):
    session = SessionLocal()
    record = session.query(PostRecord).filter_by(id=task_id).first()
    if not record or record.status != "done":
        session.close()
        return {}

    return record.get_post()


app = Flask(__name__)


def get_config_state(flag):
    return 'ENABLED' if flag == 'True' else 'DISABLED'

@app.route('/')
def hello_world():
    STATE = {
        'version': 'v4.19.0',
        'config': {
            'LLM': get_config_state(config['ENABLE_LLM_GENERATION']),
            'EMAIL': get_config_state(config['ENABLE_EMAIL']),
            'SCHEDULER': get_config_state(config['ENABLE_SCHEDULED_GENERATION']),
            'NEW_POST': get_config_state(config['ENABLE_NEW_POST']),
        }
    }
    return jsonify(STATE)


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


@app.route("/webhook/update-post-status", methods=['POST'])
def update_post_status():
    task_id = request.json['task_id']
    print("new post update: ", task_id)
    data = retrieve_post(task_id)
    if not data:
        print(f"Failed to retrieve task data: {task_id}")
        return jsonify({"status": "failed"}), 500

    if config['ENABLE_EMAIL']=='False':
        print("Email not enabled")
        print("Notification for task: ", task_id)
        return jsonify({"status": "success"}), 200

    msg = EmailMessage()
    msg.set_content(data['post'])
    msg['Subject'] = f"New Post Generated: {data['event_title']}"
    msg['From'] = f"LLM <birnadin.anton-robert-clive@stud.th-deg.de>"
    msg['To'] = "birnadin.anton-robert-clive@stud.th-deg.de"

    try:
        with SMTP(host=config['EMAIL_SERVER'], port=int(config['EMAIL_PORT'])) as s:
            s.starttls()
            s.login(config['EMAIL_USER'], config['EMAIL_PASSWORD'])
            s.sendmail(config['EMAIL_USER'], config['EMAIL_USER'], msg.as_string())

    except SMTPException as e:
        print("failed to send email: ", e)
        return jsonify({"status": "failed-email"})
    except Exception as e:
        print("failed to proceed: ", e)
        return jsonify({"status": "failed-common"})

    return jsonify({"status": "success"})


@app.route("/queue-new-post", methods=["POST"])
def generate():
    data = request.json

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
        instructions=data["instructions"],
        status="queued"
    )

    session = SessionLocal()
    session.add(record)
    session.commit()
    task_id = record.id
    session.close()

    ok = queue_new_post(task_id)
    if not ok:
        return jsonify({"queue-id": -2003})

    print(f"Queued new post: {task_id}")
    return jsonify({"queue-id": task_id})


if __name__ == '__main__':
    app.run()

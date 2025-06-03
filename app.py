import requests
from flask import Flask, request, jsonify

from models import SessionLocal, PostRecord

LLM_SERVICE = "http://localhost:5001"

app = Flask(__name__)

@app.route('/')
def hello_world():  # put application's code here
    return 'InecosysLLM v0.3.9'


# noinspection PyBroadException
def queue_new_post(task_id):
    try:
        res = requests.post(f"{LLM_SERVICE}/process-new-task", json={"task_id": task_id})
        if res.status_code != 200:
            print(f"Failed to queue new post: RES/{res.status_code}")
            return False
    except Exception as e:
        print(f"Failed to queue new post: EXP/{e}")
        return False
    return True


@app.route("/queue-new-post", methods=["POST"])
def generate():
    # prep data
    data = request.json
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

    # commit ds
    session = SessionLocal()
    session.add(record)
    session.commit()
    task_id = record.id
    session.close()

    # indicate LLM about new ds record
    ok = queue_new_post(task_id)
    if not ok:
        return jsonify({"queue-id": -2003})

    print(f"Queued new post: {task_id}")
    return jsonify({"queue-id": task_id})

if __name__ == '__main__':
    app.run()

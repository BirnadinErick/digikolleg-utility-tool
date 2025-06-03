import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

from models import SessionLocal, PostRecord

device = "cpu"
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model.to(device)

def notify_personal(task_id):
    return None

def make_prompt(event_title, date, description, good, bad, goal, instructions):
    return f"""
Write a LinkedIn post about my company Inecosys participation in an event.  And you are a 
social media manager in company called "Inecosys", do not mention anywhere in the post that you are the manager.
the Post SHOULD NOT exceed 200 words. Parameter called "Instructions" are extra comments from
a manager, follow it when constructing new Post as well. include 3 hashtags at the very bottom as well. Do not include
any placeholders. DO NOT include any other information that haven't been given explicitly in this prompt. Write the post
in "we" form or passive. Compare parameters "Today" & "Event Date" to determine whether the event has already
conducted or not. Following are parameters you should consider:

Today: {datetime.datetime.today()}
Title: {event_title}
Event Date: {date}
Description: {description}
Positive Impressions: {good}
Possible improvements: {bad}
Goal of Participation: {goal}

Instructions: {instructions}

Post:
"""

def generate_linkedin_post(task_id, inputs):
    prompt = make_prompt(**inputs)
    print(f"prompt: {prompt}")
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)

    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            max_new_tokens=700,
            temperature=0.5,
            top_p=0.9,
            do_sample=True,
            eos_token_id=tokenizer.eos_token_id
        )

    post = tokenizer.decode(output_ids[0], skip_special_tokens=True).split("Post:")[-1].strip()
    ok = save_post_to_database(task_id, post)

    if ok:
        notify_personal(task_id)
        print("Post saved for task_id: ", task_id)
    else:
        print("Post not saved for task_id: ", task_id)


def save_post_to_database(task_id, post):
    session = SessionLocal()
    record = session.query(PostRecord).filter_by(id=task_id).first()
    if not record or record.status != "processing":
        session.close()
        return False

    record.post = post
    record.status = "done"
    session.commit()

    return True


llm = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

def retrieve_task_data(task_id):
    session = SessionLocal()
    record = session.query(PostRecord).filter_by(id=task_id).first()
    if not record or record.status != "queued":
        session.close()
        return False

    record.status = "processing"
    session.commit()

    return record

@llm.route("/process-new-task", methods=["POST"])
def generate():
    task_id = request.json['task_id']
    data = retrieve_task_data(task_id)

    result = scheduler.add_job(func=generate_linkedin_post, args=[task_id,data], id=task_id, replace_existing=True)
    if result.id != task_id:
        return jsonify({"ok": False})

    return jsonify({"ok": True})

if __name__ == '__main__':
    llm.run(port=5001)

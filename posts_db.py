from flask import jsonify

from logger import logger
from models import SessionLocal, PostRecord

def create_post(request):
    data = request.json
    logger.debug(f"data: {data}")
    session = SessionLocal()
    post = PostRecord(**data)
    session.add(post)
    session.commit()
    logger.info('CREATE POST: ok.')
    return jsonify({'id': post.id}), 201

def get_all_posts():
    session = SessionLocal()
    posts = session.query(PostRecord).all()
    return jsonify([p.api_dict() for p in posts])

def get_post(id):
    session = SessionLocal()
    post = session.query(PostRecord).get(id)
    if not post:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(post.api_dict())

def update_post(request, id):
    session = SessionLocal()
    post = session.query(PostRecord).get(id)
    if not post:
        return jsonify({'error': 'Not found'}), 404

    data = request.json
    for key, value in data.items():
        if hasattr(post, key):
            setattr(post, key, value)

    session.commit()
    return jsonify(post.dict())

def delete_post(id):
    session = SessionLocal()
    post = session.query(PostRecord).get(id)
    if not post:
        return jsonify({'error': 'Not found'}), 404

    session.delete(post)
    session.commit()
    return jsonify({'message': 'Deleted'})
from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages')
def messages():
    messages = Message.query.order_by(Message.created_at.desc()).all()
    response = make_response(jsonify([message.to_dict() for message in messages]), 200)

    return response

@app.route('/messages/<int:id>')
def messages_by_id(id):
    messages = Message.query.filter_by(id = id).all()
    if messages:
        response = make_response(jsonify([message.to_dict() for message in messages]), 200)
        return response
    else:
        return make_response(jsonify({"error": "Message not found"}), 404)


@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    body = data.get('body')
    username = data.get('username')

    if not body or not username:
        return make_response(jsonify({"error": "Body and Username are required"}), 400)
    
    new_message = Message(body=body, username=username)
    db.session.add(new_message)
    db.session.commit()
    response = make_response(jsonify(new_message.to_dict()), 201)
    return response

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.filter_by(id = id).first()
    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)
    
    data = request.get_json()
    new_body = data.get('body')

    if new_body:
        message.body = new_body
        db.session.commit()

    response = make_response(jsonify(message.to_dict()), 200)
    return response

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.filter_by(id = id).first()
    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)
    
    db.session.delete(message)
    db.session.commit()
    return make_response(jsonify({"message": "Message deleted successfully"}), 204)

if __name__ == '__main__':
    app.run(port=5555)

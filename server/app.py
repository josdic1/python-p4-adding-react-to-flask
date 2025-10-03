from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message
import os

app = Flask(__name__)


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)
db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at).all()
        response = make_response(
            jsonify([message.to_dict() for message in messages]),
            200,
        )
    elif request.method == 'POST':
        data = request.get_json()
        message = Message(
            body=data['body'],
            username=data['username']
        )
        db.session.add(message)
        db.session.commit()
        response = make_response(
            jsonify(message.to_dict()),
            201,
        )
    return response

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()
    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)

    if request.method == 'PATCH':
        data = request.get_json()
        for attr in data:
            setattr(message, attr, data[attr])
        db.session.add(message)
        db.session.commit()
        response = make_response(jsonify(message.to_dict()), 200)

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        response = make_response(jsonify({'deleted': True}), 200)

    return response

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    print("Starting Flask server on http://127.0.0.1:5555")
    app.run(port=5555, debug=True)

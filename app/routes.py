from flask import Blueprint, request, jsonify
from app import db
from models import User, Message, VoiceMessage
from services import save_voice_message, transcribe_audio

bp = Blueprint('main', __name__)

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 409
    new_user = User(username=username)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"id": new_user.id, "username": new_user.username}), 201

@bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username} for user in users])

@bp.route('/messages', methods=['POST'])
def send_message():
    data = request.json
    sender_id = data.get('sender_id')
    recipient_id = data.get('recipient_id')
    content = data.get('content')
    print(len(content))
    if not sender_id or not recipient_id or not content:
        return jsonify({"error": "sender_id, recipient_id, and content are required"}), 400

    if len(content) > 500:
        return jsonify({"error": "Message content must be 500 characters or less"}), 400
    
    sender = User.query.get(sender_id)
    recipient = User.query.get(recipient_id)
    if not sender or not recipient:
        return jsonify({"error": "Sender or recipient not found"}), 404
    
    new_message = Message(content=content, sender_id=sender_id, recipient_id=recipient_id)
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({
        "id": new_message.id,
        "content": new_message.content,
        "timestamp": new_message.timestamp,
        "sender_id": new_message.sender_id,
        "recipient_id": new_message.recipient_id
    }), 201

@bp.route('/messages', methods=['GET'])
def get_messages():
    user1_id = request.args.get('user1_id')
    user2_id = request.args.get('user2_id')
    
    if not user1_id or not user2_id:
        return jsonify({"error": "Both user1_id and user2_id are required"}), 400
    
    messages = Message.query.filter(
        ((Message.sender_id == user1_id) & (Message.recipient_id == user2_id)) |
        ((Message.sender_id == user2_id) & (Message.recipient_id == user1_id))
    ).order_by(Message.timestamp).all()
    
    return jsonify([{
        "id": message.id,
        "content": message.content,
        "timestamp": message.timestamp,
        "sender_id": message.sender_id,
        "recipient_id": message.recipient_id
    } for message in messages])

@bp.route('/voice_messages', methods=['POST'])
def upload_voice_message():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    sender_id = request.form.get('sender_id')
    recipient_id = request.form.get('recipient_id')
    
    if not sender_id or not recipient_id:
        return jsonify({"error": "sender_id and recipient_id are required"}), 400
    
    result = save_voice_message(file, sender_id, recipient_id)
    if isinstance(result, str):
        return jsonify({"error": result}), 400
    
    return jsonify(result), 201

@bp.route('/voice_messages', methods=['GET'])
def get_voice_messages():
    user1_id = request.args.get('user1_id')
    user2_id = request.args.get('user2_id')
    
    if not user1_id or not user2_id:
        return jsonify({"error": "Both user1_id and user2_id are required"}), 400
    
    voice_messages = VoiceMessage.query.filter(
        ((VoiceMessage.sender_id == user1_id) & (VoiceMessage.recipient_id == user2_id)) |
        ((VoiceMessage.sender_id == user2_id) & (VoiceMessage.recipient_id == user1_id))
    ).order_by(VoiceMessage.timestamp).all()
    
    return jsonify([{
        "id": vm.id,
        "filename": vm.filename,
        "timestamp": vm.timestamp,
        "sender_id": vm.sender_id,
        "recipient_id": vm.recipient_id,
        "transcription": vm.transcription
    } for vm in voice_messages])

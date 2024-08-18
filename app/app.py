# app.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os
from werkzeug.utils import secure_filename
from openai import OpenAI
from database import db
from models import User, Message, VoiceMessage

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize OpenAI client
client = OpenAI()

with app.app_context():
    db.create_all()

@app.route('/users', methods=['POST'])
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

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username} for user in users])

@app.route('/messages', methods=['POST'])
def send_message():
    data = request.json
    sender_id = data.get('sender_id')
    recipient_id = data.get('recipient_id')
    content = data.get('content')
    
    if not sender_id or not recipient_id or not content:
        return jsonify({"error": "sender_id, recipient_id, and content are required"}), 400
    
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

@app.route('/messages', methods=['GET'])
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

@app.route('/voice_messages', methods=['POST'])
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
    
    if file and file.filename.rsplit('.', 1)[1].lower() in ['wav', 'mp3', 'ogg']:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            with open(file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
            transcription = transcript.text
        except Exception as e:
            transcription = f"Transcription failed: {str(e)}"
        
        new_voice_message = VoiceMessage(
            filename=filename, 
            sender_id=sender_id, 
            recipient_id=recipient_id,
            transcription=transcription
        )
        
        db.session.add(new_voice_message)
        db.session.commit()
        
        # Delete the audio file after transcription
        os.remove(file_path)
        
        return jsonify({
            "id": new_voice_message.id,
            "filename": new_voice_message.filename,
            "timestamp": new_voice_message.timestamp,
            "sender_id": new_voice_message.sender_id,
            "recipient_id": new_voice_message.recipient_id,
            "transcription": new_voice_message.transcription
        }), 201
    return jsonify({"error": "File type not allowed. Only WAV, MP3, and OGG files are accepted."}), 400

@app.route('/voice_messages', methods=['GET'])
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

if __name__ == '__main__':
    app.run(debug=True)
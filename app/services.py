# services.py

import os
from flask import current_app
from werkzeug.utils import secure_filename
from app import db
from models import VoiceMessage
from openai import OpenAI

client = OpenAI()

def save_voice_message(file, sender_id, recipient_id):
    if file and file.filename.rsplit('.', 1)[1].lower() in ['wav', 'mp3', 'ogg']:
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            transcription = transcribe_audio(file_path)
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
        
        return {
            "id": new_voice_message.id,
            "filename": new_voice_message.filename,
            "timestamp": new_voice_message.timestamp,
            "sender_id": new_voice_message.sender_id,
            "recipient_id": new_voice_message.recipient_id,
            "transcription": new_voice_message.transcription
        }
    return "File type not allowed. Only WAV, MP3, and OGG files are accepted."

def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    return transcript.text
import requests
import json
import os
import configparser
from prettytable import PrettyTable
import time
import pyaudio
import wave
import tempfile

def load_config(config_file='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_file)
    
    defaults = {
        'Username': 'DefaultUser',
        'ServerIP': '127.0.0.1',
        'ServerPort': '5000',
        'Debug': 'false'
    }
    
    if 'DEFAULT' in config:
        for key in defaults:
            if key in config['DEFAULT']:
                defaults[key] = config['DEFAULT'][key]
    
    defaults['Debug'] = defaults['Debug'].lower() == 'true'
    
    return defaults

CONFIG = load_config()
API_URL = f"http://{CONFIG['ServerIP']}:{CONFIG['ServerPort']}"
USERNAME = CONFIG['Username']
DEBUG = CONFIG['Debug']

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    print(f"\n--- Messaging App Menu (Logged in as {USERNAME}) ---")
    print("1. Send Text Message")
    print("2. Send Voice Message")
    print("3. View Messages")
    print("4. List Users")
    print("5. Exit")

def get_user_id(username):
    try:
        response = requests.get(f"{API_URL}/users")
        response.raise_for_status()
        users = response.json()
        for user in users:
            if user['username'] == username:
                return user['id']
    except requests.RequestException as e:
        print(f"Error retrieving users: {e}")
    return None

def create_user(username):
    try:
        response = requests.post(f"{API_URL}/users", json={"username": username})
        response.raise_for_status()
        return response.json()['id']
    except requests.RequestException as e:
        print(f"Error creating user: {e}")
    return None

def send_text_message(sender_id):
    recipient = input("Enter recipient's username: ")
    content = input("Enter your message: ")

    recipient_id = get_user_id(recipient)
    if not recipient_id:
        print("Recipient not found.")
        return

    data = {"sender_id": sender_id, "recipient_id": recipient_id, "content": content}

    try:
        if DEBUG:
            print(f"Sending payload: {json.dumps(data, indent=2)}")
        response = requests.post(f"{API_URL}/messages", json=data)
        response.raise_for_status()
        print("Message sent successfully!")
    except requests.RequestException as e:
        print(f"Error sending message: {e}")
        if DEBUG:
            print(f"Response content: {response.content}")

def record_audio(duration=5, output_file='temp_voice_message.wav'):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print(f"Recording for {duration} seconds...")

    frames = []

    for i in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(output_file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def send_voice_message(sender_id):
    recipient = input("Enter recipient's username: ")
    
    temp_file = 'temp_voice_message.wav'
    record_audio(duration=5, output_file=temp_file)

    recipient_id = get_user_id(recipient)
    if not recipient_id:
        print("Recipient not found.")
        return

    data = {"sender_id": sender_id, "recipient_id": recipient_id}

    try:
        with open(temp_file, 'rb') as file:
            files = {'file': ('voice_message.wav', file, 'audio/wav')}
            if DEBUG:
                print(f"Sending payload: {json.dumps(data, indent=2)}")
                print(f"Sending file: {temp_file}")
            response = requests.post(f"{API_URL}/voice_messages", data=data, files=files)
            response.raise_for_status()
        print("Voice message sent and transcribed successfully!")
        print(f"Transcription: {response.json()['transcription']}")
    except requests.RequestException as e:
        print(f"Error sending voice message: {e}")
        if DEBUG:
            print(f"Response content: {response.content}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def view_messages(user_id):
    other_user = input("Enter username to view messages with: ")
    other_id = get_user_id(other_user)

    if not other_id:
        print("User not found.")
        return

    try:
        response = requests.get(f"{API_URL}/messages?user1_id={user_id}&user2_id={other_id}")
        voice_response = requests.get(f"{API_URL}/voice_messages?user1_id={user_id}&user2_id={other_id}")
        
        response.raise_for_status()
        voice_response.raise_for_status()

        messages = response.json()
        voice_messages = voice_response.json()
        
        all_messages = messages + voice_messages
        all_messages.sort(key=lambda x: x['timestamp'])

        table = PrettyTable()
        table.field_names = ["Timestamp", "Sender", "Content"]
        
        users_response = requests.get(f"{API_URL}/users")
        users_response.raise_for_status()
        users = users_response.json()

        for msg in all_messages:
            sender = next((u['username'] for u in users if u['id'] == msg['sender_id']), "Unknown")
            content = msg.get('content') or msg.get('transcription', 'Voice Message')
            table.add_row([msg['timestamp'], sender, content])
        
        print(table)
    except requests.RequestException as e:
        print(f"Error retrieving messages: {e}")

def list_users():
    try:
        response = requests.get(f"{API_URL}/users")
        response.raise_for_status()
        users = response.json()
        table = PrettyTable()
        table.field_names = ["ID", "Username"]
        for user in users:
            table.add_row([user['id'], user['username']])
        print(table)
    except requests.RequestException as e:
        print(f"Error retrieving users: {e}")

def main():
    clear_screen()
    print("Welcome to the Messaging App!")
    print(f"Logged in as {USERNAME}")
    if DEBUG:
        print("Debug mode is ON")

    user_id = get_user_id(USERNAME)
    if not user_id:
        print("User not found. Creating new user.")
        user_id = create_user(USERNAME)
        if not user_id:
            print("Failed to create user. Exiting.")
            return

    while True:
        print_menu()
        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            send_text_message(user_id)
        elif choice == '2':
            send_voice_message(user_id)
        elif choice == '3':
            view_messages(user_id)
        elif choice == '4':
            list_users()
        elif choice == '5':
            print("Thank you for using the Messaging App. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

        input("\nPress Enter to continue...")
        clear_screen()

if __name__ == "__main__":
    main()
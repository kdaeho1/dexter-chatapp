# dexter-chatapp

## Design

The chatapp follows a typical server/client architecture. 

SQLite as the database is great and super fast as well as it running locally with minimal setup.

Only 3 Tables are used (Users, Messages and VoiceMessages). This helps keep things clean.

Server can be configured with config.py and the client with a config.ini. Users are created upon first login. 

Downside at the moment is that as any user can log is an any other and read the messages of other users.

## Overview

The ChatApp Clone is a simple messaging application that includes text messaging and voice messaging with transcription features. The application consists of two main parts:

1. **Server**: Built using Flask, SQLite (with SQLAlchemy), and OpenAI Whisper for audio transcription.
2. **Client**: A Python-based client using PyAudio for capturing audio.

### Features

- **Messaging**: Send and receive text messages between users.
- **Voice Messages with Transcriptions**: Send voice messages that are automatically transcribed into text.
- **Listing Users**: Retrieve a list of all registered users.
- **Efficient SQLite Database**: Optimized database operations using SQLAlchemy ORM.
- **Server-side Validation**: Basic validation checks, including message length and file size limitations.

### Features Not Implemented

- Group Chats
- Listening to Voice Messages
- Authentication
- Extensive Error Handling

## Installation

### Prerequisites

- Python
- Flask
- SQLAlchemy
- OpenAI Python Client
- PyAudio

### Requirements

Ensure all required Python packages are installed:

```bash
pip install -r requirements.txt
```

### Setting Up the OpenAI Environment Variable

To enable audio transcription with OpenAI's Whisper model, you need to set your OpenAI API key as an environment variable. You can do this by adding the following line to your `.zshrc` file (or `.bashrc`, depending on your shell):

```bash
export OPENAI_API_KEY='your-openai-api-key'
```

After adding this line, run:

```bash
source ~/.zshrc
```

### Configuration

#### `config.ini`

This file is used for additional configuration. It should be placed in the root of your project directory.

Example `config.ini`:

```ini
[DEFAULT]
Username = daeho
ServerIP = 127.0.0.1
ServerPort = 5000
Debug = false
```

### Quickstart

1. **Clone the Repository**

   ```bash
   git clone https://github.com/kdaeho1/dexter-chatapp.git
   cd dexter-chatapp
   ```

2. **Set Up the Database**

   The database will be created automatically when you run the server for the first time.

   If you are trying this locally, you need to open the client two times to mock 2 users.
   
   E.g. Once as Daeho and then as Bob (change the username in config.ini)

   That way both users are created and they can then talk to each other.

3. **Start the Server**

   ```bash
   python app.py
   ```

   The server will start running on `http://127.0.0.1:5000/`.

4. **Client Setup**

   The client script `client.py` can be used to interact with the server, especially for sending voice messages. Ensure PyAudio is installed and configured properly on your system.

   On Apple Silicon Macs you may need to install portaudio first:
   ```bash
   brew install portaudio
   ```

## API Endpoints

### Users

- **POST `/users`**: Create a new user.
- **GET `/users`**: List all users.

### Messages

- **POST `/messages`**: Send a text message between users.
- **GET `/messages`**: Retrieve messages between two users.

### Voice Messages

- **POST `/voice_messages`**: Upload and transcribe a voice message.
- **GET `/voice_messages`**: Retrieve voice messages between two users.

## Additional Notes

- **Database**: The SQLite database file is located in the `app/instance` directory.
- **Voice Messages**: Uploaded voice messages are temporarily stored in the `voice_messages` directory before being transcribed and then deleted.
- **Server Validation**: The server includes basic validation checks such as ensuring messages are under 500 characters and voice messages do not exceed 100MB.

## Troubleshooting

- **PyAudio Issues**: If you encounter issues with PyAudio, ensure that it is properly installed for your Python version and operating system. For Windows, you may need to install it via a `.whl` file.
- **Transcription Failures**: If transcription fails, ensure that the OpenAI API key is correctly set and that the Whisper model is accessible.
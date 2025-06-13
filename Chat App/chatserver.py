import socketio
import eventlet
from flask import Flask
from datetime import datetime
import logging

logging.basicConfig(filename='logs.log', level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')

flaskapp = Flask(__name__)  #CREATION OF FLASK APP AND THE SOCKETIO SERVER
sios = socketio.Server(cors_allowed_origins='*')

app = socketio.WSGIApp(sios, flaskapp)

clients = {}   #STORES CLIENTS USERNAMES
joinedusers = {}  #STORES CLIENTS THAT HAVE JOINED THE CHAT
presharedkey = b'DERBY'


def encrypt_message(message):  #CAESARS CIPHER ENCRYPTION
    key = 3  
    encrypted_message = ''.join(chr((ord(char) + key) % 128) for char in message)
    return encrypted_message

@sios.on('connect')
def connect(sid, environ):   #HANDLES CONNECTIONS TO THE SERVER
    print(f"Connected: {sid}")

@sios.on('join')
def join(sid, data):
    username = data['username']
    key = data['key'].encode('utf-8')   #HANDLES THE JOIN EVENT WHEN A USER JOINS THE CHAT AS WELL AS THE DATA FROM THE USER 

    if key == presharedkey and sid not in joinedusers:
        clients[sid] = username
        joinedusers[sid] = True  #VALIDATION FOR THE SECURITY KEY
        print(f"{username} joined the chat")
        sios.emit('chat_message', {'username': 'System', 'message': f"{username} joined the chat"})
        logging.info(f'{username} joined the chat')
    elif sid not in joinedusers:      #IF KEY IS INCORRECT
        print(f"{username} attempted to join with an incorrect key.")
        logging.error(f'{username} attempted to join with an incorrect key.')

@sios.on('chat_message')
def chat_message(sid, data):    #HANDLES THE CHAT MESSAGES AND THE MESSAGE INFORMATION SENT FROM THE CLIENT
    if sid in clients:     #CHECKS IF THE CLIENT IS ONE OF THE CONNECTED CLIENTS
        username = clients[sid]
        message = data['message']
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M")
        logging.info(f'Message sent by {username}: {message}')
        
        
        encrypted_message = encrypt_message(message)
        print(f"[{timestamp}] {username}: {encrypted_message}") #ENCRYPTING MESSAGES FOR THE SERVER TERMINAL

        for client_sid, client_username in clients.items():
            if client_sid != sid:
                sios.emit('chat_message', {'username': username, 'message': message, 'timestamp': timestamp}, room=client_sid)

@sios.on('disconnect')
def disconnect(sid):
    if sid in clients:
        username = clients[sid]
        print(f"{username} disconnected")   #HANDLES DISCONNECTIONS FROM THE SERVER
        logging.info(f'{username} disconnected!')
        del clients[sid]
        sios.emit('chat_message', {'username': 'System', 'message': f"{username} left the chat"})

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('localhost', 5000)), app)

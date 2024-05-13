from flask import Flask, render_template, jsonify, redirect
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import threading
import socket

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Enable CORS
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow cross-origin requests from all domains

connected_users = 0
video_users = 0


@socketio.on('signal')
def handle_signal(data):
    # Broadcast signal data to all other clients
    emit('signal', data, broadcast=True, include_self=False)

@socketio.on('ice_candidate')
def handle_ice_candidate(message):
    # Broadcast ICE candidate information to other clients
    emit('ice_candidate', message, broadcast=True, include_self=False)

@socketio.on('connect')
def handle_connect():
    global connected_users
    connected_users += 1
    emit('user_count', {'count': connected_users}, broadcast=True)  # Broadcast the count to all clients

@socketio.on('disconnect')
def handle_disconnect():
    global connected_users
    connected_users -= 1
    emit('user_count', {'count': connected_users}, broadcast=True)  # Broadcast the count to all clients

@app.route('/')
def start():
    # Render an HTML page
    return render_template('start.html')

@app.route('/media')
def index():
    # Render an HTML page
    return render_template('index.html')

@app.route('/other')
def other():
    return redirect("")





temperature = 0
humidity = 0
light = 0
sound = 0

def tcp_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()

    print("TCP Server listening on {}:{}".format(host, port))

    while True:
        client_socket, addr = server_socket.accept()
        print('Connected by', addr)
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.daemon = True
        thread.start()

def handle_client(client_socket):
    global temperature, humidity, light, sound
    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            data = json.loads(data)
            print(data)
            if 'temperature' in data:
                temperature = data['temperature']
            if 'humidity' in data:
                humidity = data['humidity']
            if 'light' in data:
                light = data['light']
            if 'sound' in data:
                sound = data['sound']
    finally:
        client_socket.close()

@app.route('/temperature-sensor')
def get_temperature():
    global temperature
    return jsonify({'temperature': temperature})

@app.route('/humidity-sensor')
def get_humidity():
    global humidity
    return jsonify({'humidity': humidity})

@app.route('/light-sensor')
def get_light():
    global light
    return jsonify({'light': light})

@app.route('/sound-sensor')
def get_sound():
    global sound
    return jsonify({'sound': sound})

if __name__ == '__main__':
    host = '0.0.0.0'  # Listen on all network interfaces
    port = 11111  # Port number where the server will be listening//传输数据

    thread = threading.Thread(target=tcp_server, args=(host, port))
    thread.daemon = True
    thread.start()

    socketio.run(app, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True)
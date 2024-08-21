#!/usr/bin/env python3

from flask import Flask, request, jsonify
import json
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(32)

def update_token(token, chat_id, family):
    with open('utils/token_list.json', 'r+') as f:
        token_list = json.load(f)
        token_list['bots'].append(
            {
                'token': token, 
                'chat_id': chat_id, 
                'status': 'False', 
                'family': family
            }
        )
        f.seek(0)
        f.write(json.dumps(token_list))
        f.truncate()    

@app.route('/api/update_token', methods=['POST'])
def update():
    data = request.json
    token = data['token']
    chat_id = data['chat_id']
    family = data['family']

    update_token(token, chat_id, family)

    return jsonify({'status': 'success'})

@app.route('/api/get_token', methods=['GET'])
def get():
    with open('utils/token_list.json', 'r') as f:
        token_list = json.load(f)

    return jsonify(token_list)

def start():
    HOST = '0.0.0.0'
    PORT = 5000

    app.run(HOST, PORT)
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
    try:
        token = data['token']
        chat_id = data['chat_id']
        family = data['family']

        update_token(token, chat_id, family)

        return jsonify({'status': 'success', 'message': 'Token updated successfully'})
    except KeyError:
        return jsonify({'status': 'failed', 'message': 'Invalid request'})

@app.route('/api/update_token_list', methods=['POST'])
def update_list():
    data = request.json
    try:
        token_list = data['bots']

        for bot in token_list:
            token = bot['token']
            chat_id = bot['chat_id']
            family = bot['family']

            update_token(token, chat_id, family)

        return jsonify({'status': 'success', 'message': 'Token list updated successfully'})
    except KeyError:
        return jsonify({'status': 'failed', 'message': 'Invalid request'})

@app.route('/api/delete_token', methods=['POST'])
def delete():
    data = request.json
    try:
        token = data['token']

        with open('utils/token_list.json', 'r+') as f:
            token_list = json.load(f)
            for i in range(len(token_list['bots'])):
                if token_list['bots'][i]['token'] == token:
                    token_list['bots'].pop(i)
                    break
            f.seek(0)
            f.write(json.dumps(token_list))
            f.truncate()

        return jsonify({'status': 'success', 'message': 'Token deleted successfully'})
    except KeyError:
        return jsonify({'status': 'failed', 'message': 'Invalid request'})

@app.route('/api/update_status', methods=['POST'])
def update_status():
    data = request.json
    try:
        token = data['token']
        status = data['status']

        with open('utils/token_list.json', 'r+') as f:
            token_list = json.load(f)
            for i in range(len(token_list['bots'])):
                if token_list['bots'][i]['token'] == token:
                    token_list['bots'][i]['status'] = status
                    break
            f.seek(0)
            f.write(json.dumps(token_list))
            f.truncate()

        return jsonify({'status': 'success', 'message': 'Status updated successfully'})
    except KeyError:
        return jsonify({'status': 'failed', 'message': 'Invalid request'})

@app.route('/api/get_token', methods=['GET'])
def get():
    with open('utils/token_list.json', 'r') as f:
        token_list = json.load(f)

    return jsonify(token_list)

def start():
    HOST = '0.0.0.0'
    PORT = 5000

    app.run(HOST, PORT)
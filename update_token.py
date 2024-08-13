#!/usr/bin/env python3

import argparse
import json

def update_token(token, chat_id):
    with open('utils/token_list.json', 'r+') as f:
        token_list = json.load(f)
        token_list['bots'].append({'token': token, 'chat_id': chat_id, 'status': 'False'})
        f.seek(0)
        f.write(json.dumps(token_list))
        f.truncate()    

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', type=str, help='Bot token')
    parser.add_argument('--chat_id', type=int, help='Chat ID')
    args = parser.parse_args()

    update_token(args.token, args.chat_id)
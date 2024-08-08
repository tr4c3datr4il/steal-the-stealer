from dotenv import load_dotenv
from multiprocessing import Process
import os
import asyncio
import time
import json

from utils import extractor
from utils import parser



if not load_dotenv():
    raise FileNotFoundError("No .env file found")
api_id = os.environ['api_id']
api_hash = os.environ['api_hash']


"""json format
{
    "bot": [
        {
            "token": "123456:AAAbbbCCCdddEEE",
            "chat_id": -123456789,
            "status": false      <- this will be updated to true after the bot is used
        }
    ]
}
"""
def update_json(token_list):
    with open('utils/token_list.json', 'wb') as f:
        f.write(json.dumps(token_list))

def load_json():
    with open('utils/token_list.json', 'rb') as f:
        return json.loads(f.read())

def main(token: str, chat_id: int):
    loop = asyncio.get_event_loop()
    extractor_obj = extractor.Extractor(api_id, api_hash, token, dump_path=dump_path)
    parser_obj = parser.Parser(extractor.dump_path)

    bot, username, bot_id, err = loop.run_until_complete(extractor_obj.getBot())
    if err:
        # handle this err
        print(err)
        exit(1)

    async def processing(chat_id):
        async for message, id in extractor_obj.getMessages(chat_id):
            if message:
                # need to handle exceptions
                file_path = await extractor_obj.handleMessage(message)
                if file_path.suffix == '.zip':
                    extracted_path = parser_obj.decompressFile(file_path)
                    for data in parser_obj.processData(extracted_path):
                        parser_obj.parseData(data)
                    parser_obj.delFolder(extracted_path)
                parser_obj.delFile(file_path)
                print(f"Message {id} processed")
            else:
                print(f"Message {id} not found!!!!!")

    loop.run_until_complete(processing(chat_id))

dump_path = 'DUMP/'
if __name__=='__main__':
    token_list = load_json()
    while True:
        for bot in token_list['bot']:
            token, chat_id, status = bot['token'], bot['chat_id'], bot['status']
            if status == 'False':
                main(token, chat_id)
                token_list[token] = 'true'
                update_json(token_list)
            else:
                print(f'Token used - {token}')

            token_list = load_json()
            time.sleep(10) # 10s is enough to check and update the status :) but i think i'll update this soon
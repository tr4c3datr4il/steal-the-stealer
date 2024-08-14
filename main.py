from dotenv import load_dotenv
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
    "bots": [
        {
            "token": "123456:AAAbbbCCCdddEEE",
            "chat_id": -123456789,
            "status": "False"      <- this will be updated to true after the bot is used
        }
    ]
}
"""
def update_json(token_list):
    with open('utils/token_list.json', 'w') as f:
        f.seek(0)
        f.write(json.dumps(token_list))
        f.truncate()

def load_json():
    with open('utils/token_list.json', 'rb') as f:
        return json.loads(f.read())

def main(token: str, chat_id: int, family: str, dump_path: str = 'DUMP/'):
    loop = asyncio.get_event_loop()
    extractor_ins = extractor.Extractor(api_id, api_hash, token, dump_path=dump_path)
    parser_ins = parser.ProfileParser(extractor_ins.dump_path)

    bot, username, bot_id, err = loop.run_until_complete(extractor_ins.getBot())
    if err:
        # handle this err
        print(err)
        exit(1)

    # need to handle exceptions in this function
    async def processing(chat_id):
        async for message, id in extractor_ins.getMessages(chat_id):
            if message:
                result = await extractor_ins.handleMessage(message)
                if result:
                    file_path = result
                    # Braodo
                    if file_path.suffix == '.zip':
                        extracted_path = parser_ins.decompressFile(file_path)
                        for data in parser_ins.processData(extracted_path, family):
                            parser_ins.parseData(data)
                        parser_ins.delFolder(extracted_path)
                    # Raw
                    elif 'passwords.txt' in file_path.name:
                        for data in parser_ins.processData(file_path, family):
                            parser_ins.parseData(data)
                    # delete the file after processing. We can keep the file if we want to (will be updated soon)
                    parser_ins.delFile(file_path)
                    print(f"Message {id} processed")

    loop.run_until_complete(processing(chat_id))
    bot.disconnect()

dump_path = 'DUMP/'
if __name__=='__main__':
    token_list = load_json()
    while True:
        for bot in token_list['bots']:
            token, chat_id, status = bot['token'], bot['chat_id'], bot['status']
            family = bot['family']
            
            if status == 'False':
                print(f'Processing bot - {token}')
                main(token, chat_id, family, dump_path)
                bot['status'] = 'True'
                update_json(token_list)
            else:
                print(f'Token used - {token}')
                time.sleep(10) # 10s is enough to check and update the status :) but i think i'll update this soon

        token_list = load_json()
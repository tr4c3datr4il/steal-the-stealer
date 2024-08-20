from dotenv import load_dotenv
import os
import asyncio
import time
import json
import argparse
import logging

from utils import extractor
from utils import parser
from utils import database

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.getLogger('telethon').setLevel(logging.WARNING)
logging.getLogger('telethon.network.mtproto').setLevel(logging.WARNING)
logging.getLogger('telethon.client').setLevel(logging.WARNING)


if not load_dotenv():
    raise FileNotFoundError("No .env file found")
api_id = os.environ['API_ID']
api_hash = os.environ['API_HASH']

def update_json(token_list):
    with open('utils/token_list.json', 'w') as f:
        f.seek(0)
        f.write(json.dumps(token_list))
        f.truncate()

def load_json():
    with open('utils/token_list.json', 'rb') as f:
        return json.loads(f.read())

def main(token: str, chat_id: int, family: str, db, dump_path: str = 'DUMP/'):
    loop = asyncio.get_event_loop()
    extractor_ins = extractor.Extractor(api_id, api_hash, token, dump_path=dump_path)
    parser_ins = parser.ProfileParser(extractor_ins.dump_path, db)

    logging.info("Connecting to Telegram...")
    bot, bot_name, bot_id, err = loop.run_until_complete(extractor_ins.getBot())
    if err:
        # handle this err
        logging.error(err)
        exit(1)
    logging.info(f"Connected to {bot_name} - {bot_id}")

    # need to handle exceptions in this function
    async def processing(chat_id):
        async for message, id in extractor_ins.getMessages(chat_id):
            if message:
                result = await extractor_ins.handleMessage(message)
                if result:
                    file_path = result
                    result, mime = parser_ins.isCompression(file_path)
                    if result:
                        extracted_path = parser_ins.decompressFile(file_path, mime)
                        for data in parser_ins.processData(extracted_path, family):
                            parser_ins.parseData(data)
                        parser_ins.delFolder(extracted_path)
                    elif parser_ins.isPasswordFile(file_path):
                        for data in parser_ins.processData(file_path, family):
                            parser_ins.parseData(data)
                    if not keep_flag:
                        parser_ins.delFile(file_path)
                    logging.info(f"Message {id} processed")

    loop.run_until_complete(processing(chat_id))
    bot.disconnect()

if __name__=='__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--keep', '-k', help='Keep extracted data', action='store_true')
    args = arg_parser.parse_args()
    keep_flag = args.keep
    dump_path = 'DUMP/'
    db = database.Database()

    token_list = load_json()
    while True:
        for bot in token_list['bots']:
            token, chat_id, status = bot['token'], bot['chat_id'], bot['status']
            family = bot['family']
            
            if status == 'False':
                logging.info(f'Processing BOT: {token} - CHAT_ID: {chat_id}')
                main(token, chat_id, family, db, dump_path)
                bot['status'] = 'True'
                update_json(token_list)
            else:
                logging.info(f'Token used - {token}')
                time.sleep(10) # 10s is enough to check and update the status :) but i think i'll update this soon

        token_list = load_json()
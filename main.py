from dotenv import load_dotenv
from multiprocessing import Process
import os
import asyncio

from utils import extractor
from utils import parser


# we need to keep track of the token and chat_id if there is a new bot added
with open('utils/token_list.csv', 'r') as f:
    """ Token format in the list:
    bot_token,available_chat_id
    """

    token_list = f.readlines()

if not load_dotenv():
    raise FileNotFoundError("No .env file found")
api_id = os.environ['api_id']
api_hash = os.environ['api_hash']

dump_path = 'DUMP/'
if __name__=='__main__':
    token = token_list[0].split(',')[0]
    chat_id = int(token_list[0].split(',')[1]) 
    
    loop = asyncio.get_event_loop()
    extractor = extractor.Extractor(api_id, api_hash, token, dump_path=dump_path)
    parser_obj = parser.Parser(extractor.dump_path)

    bot, username, bot_id, err = loop.run_until_complete(extractor.getBot())
    if err:
        # handle this
        print(err)
        exit(1)

    async def processing(extractor, chat_id):
        async for message, id in extractor.getMessages(chat_id):
            if message:
                # need to handle exceptions
                file_path = await extractor.handleMessage(message)
                if file_path.suffix == '.zip':
                    extracted_path = parser_obj.decompressFile(file_path)
                    for data in parser_obj.processData(extracted_path):
                        parser_obj.parseData(data)
                    parser_obj.delFolder(extracted_path)
                print(f"Message {id} processed")
            else:
                print(f"Message {id} not found!!!!!")

    loop.run_until_complete(processing(extractor, chat_id))
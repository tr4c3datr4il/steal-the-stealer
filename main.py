import os
import asyncio
from dotenv import load_dotenv
from utils import extractor

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

    bot, username, bot_id, err = loop.run_until_complete(extractor.getBot())
    if err:
        # handle this
        print(err)
        exit(1)

    async def process_messages(extractor, chat_id):
        async for message in extractor.getMessages(chat_id):
            if message:
                await extractor.handleMessage(message)

    loop.run_until_complete(process_messages(extractor, chat_id))
    
    # message = loop.run_until_complete(extractor.getMessage(bot, chat_id, 23))
    # loop.run_until_complete(extractor.handleMessage(message))
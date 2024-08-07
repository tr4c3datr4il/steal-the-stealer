import telethon
import asyncio
import zipfile
import os
import parser
import fnmatch
from dotenv import load_dotenv


_ = load_dotenv()

api_id = os.environ['api_id']
api_hash = os.environ['api_hash']
bot_token = os.environ['my_bot_token']
my_group_chat_id = os.environ['my_group_chat_id']

mybot = telethon.TelegramClient('BOT', api_id, api_hash)

async def main():
    await mybot.start(bot_token=bot_token)

    msg = await mybot.get_messages(my_group_chat_id, ids=14000)
    print(msg)
    forwarded_from_bot = msg.forward.sender_id
    print(forwarded_from_bot)
    bot_name = msg.forward.sender.first_name
    print(bot_name)
    attachment = msg.media
    print(attachment)

    raw_file = await mybot.download_media(attachment)
    file_format = attachment.document.mime_type
    print(file_format)
    if file_format == 'application/zip':
        with zipfile.ZipFile(raw_file, 'r') as zip_ref:
            zip_ref.extractall('extracted')
        os.remove(raw_file)
       
        # extract data recursive from all files and folders
        for dirpath, dirs, files in os.walk('extracted'): 
            for filename in fnmatch.filter(files, 'pass.txt'):
                parsed_data = parser.parse(dirpath + '/' + filename)
                print(parsed_data)

asyncio.run(main())
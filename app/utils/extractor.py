from telethon import TelegramClient
from telethon.errors.rpcerrorlist import AccessTokenExpiredError
from telethon.tl.functions.messages import GetMessagesRequest
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, MessageEmpty, MessageService
from telethon.helpers import TotalList
from telethon.tl.types import Photo
from .FastTelethon import download_file
from pathlib import Path
import time
import random


class Extractor:
    def __init__(self, api_id, api_hash, token, min_msg=0, max_msg=1000000, limit=350, dump_path='DUMP/'):
        self.api_id = api_id
        self.api_hash = api_hash
        self.token = token
        self.min_msg = min_msg
        self.max_msg = max_msg
        self.limit = limit
        self.dump_path = Path(dump_path)
        self.bot = None
        self.initDumpPath()

    async def getBot(self):
        err = None
        try:
            # create session file in the dump path
            session_file = self.dump_path / f"BOT_{self.token.replace(':', '_')}"

            bot = await TelegramClient(
                session_file, 
                self.api_id, 
                self.api_hash
            ).start(bot_token=self.token)
            
            info = await bot.get_me()
            bot_name = info.username
            bot_id = info.id

            self.dump_path = self.dump_path / f"{bot_name}_{bot_id}"
            self.initDumpPath()
            await self.extractInfo(bot_name, bot_id)
            self.bot = bot

            return bot, bot_name, bot_id, err
        # need proper error handling
        except AccessTokenExpiredError as e:
            err = e
            return None, None, None, err
        except Exception as e:
            err = e
            return None, None, None, err

    async def getMessages(self, chat_id):
        counter = 0 # we need to keep track of the number of failed messages which can't be more than the limit
        for id in range(self.min_msg, self.max_msg):
            message = await self.getMessage(chat_id, id)
            time.sleep(random.randint(1, 3))

            if not message:
                counter += 1
                if counter > self.limit:
                    break
                continue

            yield message, id

    async def getMessage(self, chat_id, message_id):
        return await self.bot.get_messages(chat_id, ids=message_id)

    async def handleMessage(self, message) -> Path:
        # Need to handle these cases properly
        if isinstance(message, TotalList):
            return None
        elif isinstance(message, MessageEmpty):
            return None
        elif isinstance(message, MessageService):
            return None
            
        if message.media:
            if isinstance(message.media, MessageMediaPhoto):
                return await self.extractPhoto(message.media.photo)
            elif isinstance(message.media, MessageMediaDocument):
                return await self.extractDocument(message.media.document)
        
        if message.message:
            return await self.extractText(message)
        
        return None

    async def extractPhoto(self, media):
        file_name = f"{media.id}_{media.date}.jpg"
        photo_path = self.dump_path / 'photo' / file_name
        photo_path.parent.mkdir(parents=True, exist_ok=True)
        await self.bot.download_file(media, photo_path)
        return photo_path

    async def extractDocument(self, media):
        file_name = media.attributes[0].file_name
        document_path = self.dump_path / 'document' / file_name
        document_path.parent.mkdir(parents=True, exist_ok=True)
        with open(document_path, 'wb') as f:
            await download_file(self.bot, media, f)
        return document_path

    async def extractText(self, message):
        text_path = self.dump_path / 'text' / f"msg_{message.id}.txt"
        text_path.parent.mkdir(parents=True, exist_ok=True)
        with open(text_path, 'wb') as f:
            # Need to handle the case when message.text is None
            f.write(message.text.encode()) if message.text is not None else f.write(b"")
        return text_path

    async def extractInfo(self, bot_name, bot_id, chat_id=None):
        info_path = self.dump_path / 'info.txt'
        with open(info_path, 'w') as f:
            f.write(f"Bot: {bot_name}\n")
            f.write(f"Bot ID: {bot_id}\n")
            f.write(f"Chat ID: {chat_id}\n")

    def initDumpPath(self):
        self.dump_path.mkdir(parents=True, exist_ok=True)
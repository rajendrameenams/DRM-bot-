import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Load variables from .env file if present
load_dotenv()

from pyrogram import Client as AFK, idle, filters
from pyromod import listen
from tglogging import TelegramLogHandler

# Config 
class Config(object):
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
    API_ID = int(os.environ.get("API_ID", "0").strip()) if os.environ.get("API_ID", "").strip().isdigit() else 0
    API_HASH = os.environ.get("API_HASH", "").strip()
    DOWNLOAD_LOCATION = os.environ.get("DOWNLOAD_LOCATION", "./DOWNLOADS")
    SESSIONS = os.environ.get("SESSIONS", "./SESSIONS")

    # Parse comma-separated AUTH_USERS safely
    raw_auth = os.environ.get('AUTH_USERS', '')
    AUTH_USERS = [
        int(x.strip()) for x in raw_auth.split(',')
        if x.strip() and (x.strip().isdigit() or (x.strip().startswith('-') and x.strip()[1:].isdigit()))
    ]

    # Parse comma-separated GROUPS safely
    raw_groups = os.environ.get('GROUPS', '')
    GROUPS = [
        int(x.strip()) for x in raw_groups.split(',')
        if x.strip() and (x.strip().isdigit() or (x.strip().startswith('-') and x.strip()[1:].isdigit()))
    ]

    # Combined chats allowed to use bot
    AUTH_CHATS = list(set(AUTH_USERS + GROUPS))

    # Log channel / group ID
    raw_log_ch = os.environ.get("LOG_CH", "")
    LOG_CH = int(raw_log_ch.strip()) if raw_log_ch.strip() and (raw_log_ch.strip().isdigit() or (raw_log_ch.strip().startswith('-') and raw_log_ch.strip()[1:].isdigit())) else None

# Filter for authorized chats
if Config.AUTH_CHATS:
    AUTH_FILTER = filters.chat(Config.AUTH_CHATS)
else:
    AUTH_FILTER = filters.all

# Setup logging
handlers = [logging.StreamHandler()]
if Config.BOT_TOKEN and Config.LOG_CH:
    try:
        tg_log_handler = TelegramLogHandler(
            token=Config.BOT_TOKEN, 
            log_chat_id=Config.LOG_CH, 
            update_interval=2, 
            minimum_lines=1, 
            pending_logs=200000
        )
        handlers.append(tg_log_handler)
    except Exception as e:
        print(f"Warning: Failed to setup TelegramLogHandler: {e}")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=handlers
)

LOGGER = logging.getLogger(__name__)

# Store
class Store(object):
    CPTOKEN = os.environ.get("CPTOKEN", "eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9.eyJpZCI6MzgzNjkyMTIsIm9yZ0lkIjoyNjA1LCJ0eXBlIjoxLCJtb2JpbGUiOiI5MTcwODI3NzQyODkiLCJuYW1lIjoiQWNlIiwiZW1haWwiOm51bGwsImlzRmlyc3RMb2dpbiI6dHJ1ZSwiZGVmYXVsdExhbmd1YWdlIjpudWxsLCJjb3VudHJ5Q29kZSI6IklOIiwiaXNJbnRlcm5hdGlvbmFsIjowLCJpYXQiOjE2NDMyODE4NzcsImV4cCI6MTY0Mzg4NjY3N30.hM33P2ai6ivdzxPPfm01LAd4JWv-vnrSxGXqvCirCSpUfhhofpeqyeHPxtstXwe0")
    SPROUT_URL = os.environ.get("SPROUT_URL", "https://discuss.oliveboard.in/")
    ADDA_TOKEN = os.environ.get("ADDA_TOKEN", "")
    THUMB_URL = os.environ.get("THUMB_URL", "https://telegra.ph/file/fd7a1e0e94a1f3e7d8b3a.jpg")

# Format
class Msg(object):
    START_MSG = "**/pro** - Batch Extractor and Downloader Bot is running!"

    TXT_MSG = "Hey <b>{user},"\
        "\n\n`I'm Multi-Talented Robot. I Can Download Many Types of Links.`"\
        "\n\nSend a TXT or HTML file :-</b>"

    ERROR_MSG = "<b>DL Failed ({no_of_files}) :-</b> "\
        "\n\n<b>Name: </b>{file_name},\n<b>Link:</b> `{file_link}`\n\n<b>Error:</b> {error}"

    SHOW_MSG = "<b>Downloading :- "\
        "\n`{file_name}`\n\nLink :- `{file_link}`</b>"

    CMD_MSG_1 = "`{txt}`\n\n**Total Links in File are :-** {no_of_links}\n\n**Send any Index From `[ 1 - {no_of_links} ]` :-**"
    CMD_MSG_2 = "<b>Uploading :- </b> `{file_name}`"
    RESTART_MSG = "✅ Bot Restarted!\n✅ Paths Cleared."

# Prefixes
prefixes = ["/", "~", "?", "!", "."]

# Client
plugins = dict(root="plugins")

if __name__ == "__main__":
    if not Config.BOT_TOKEN or not Config.API_ID or not Config.API_HASH:
        LOGGER.error("CRITICAL ERROR: BOT_TOKEN, API_ID, or API_HASH is missing!")
        LOGGER.error("Please create a .env file (or set environment variables) with:")
        LOGGER.error("  BOT_TOKEN=your_bot_token")
        LOGGER.error("  API_ID=your_api_id")
        LOGGER.error("  API_HASH=your_api_hash")
        sys.exit(1)

    if not os.path.isdir(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)
    if not os.path.isdir(Config.SESSIONS):
        os.makedirs(Config.SESSIONS, exist_ok=True)

    PRO = AFK(
        "AFK-DL",
        bot_token=Config.BOT_TOKEN,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        sleep_threshold=120,
        plugins=plugins,
        workdir=Config.SESSIONS,
        workers=2,
    )

    chat_id = Config.AUTH_CHATS

    async def main():
        await PRO.start()
        bot_info = await PRO.get_me()
        LOGGER.info(f"<--- @{bot_info.username} Started Successfully --->")
        
        for i in chat_id:
            try:
                await PRO.send_message(chat_id=i, text="**Bot Started! ♾ /pro **")
            except Exception as d:
                LOGGER.warning(f"Could not send start notification to {i}: {d}")
        
        await idle()
        await PRO.stop()

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        LOGGER.info("<---Bot Stopped--->")

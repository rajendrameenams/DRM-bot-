from main import LOGGER as LOGS, prefixes, Config, Msg
from pyrogram import Client as AFK
from pyrogram.types import Message
from handlers.html import parse_html
import os


class TgHandler:
    def __init__(self, bot: AFK, m: Message, path: str) -> None:
        self.bot = bot
        self.m = m
        self.path = path

    @staticmethod
    async def error_message(bot: AFK, m: Message, error: str):
        LOGS.error(error)
        if Config.LOG_CH:
            try:
                await bot.send_message(
                    chat_id=Config.LOG_CH,
                    text=f"<b>Error:</b> `{error}`"
                )
            except Exception as e:
                LOGS.warning(f"Failed to send error to LOG_CH: {e}")
    
    async def linkMsg2(self, List):
        a = ""
        try:
            for data in List:
                if len(f"{a}{data}") > 3500:
                    await self.bot.send_message(
                        chat_id=self.m.chat.id,
                        text=f'**Failed files are ({len(List)}) :-\n\n{a}',
                        disable_web_page_preview=True,
                    )
                    a = ""
                a += data
            if a:
                await self.bot.send_message(
                    chat_id=self.m.chat.id,
                    text=f'**Failed files are ({len(List)}) :-\n\n{a}',
                    disable_web_page_preview=True,
                )
            List.clear()
        except Exception:
            await self.m.reply_text("Done")
            List.clear()
            
    async def downloadMedia(self, msg):
        sPath = f"{Config.DOWNLOAD_LOCATION}/FILE/{self.m.chat.id}"
        os.makedirs(sPath, exist_ok=True)
        file = await self.bot.download_media(
            message=msg,
            file_name=f"{sPath}/{msg.id}"
        )
        return file

    async def readTxt(self, x):
        try:
            with open(x, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            content = content.split("\n")
            name_links = [i.split(":", 1) for i in content if i.strip() != '' and ":" in i]
            if os.path.exists(x):
                os.remove(x)
            print(len(name_links))
            return name_links
        except Exception as e:
            LOGS.error(e)
            await self.m.reply_text("**Invalid file Input.**")
            if os.path.exists(x):
                os.remove(x)
            return []

    @staticmethod
    def parse_name(rawName):
        name = (
            str(rawName).replace("/", "_")
            .replace("|", "_")
            .replace(":", "-")
            .replace("*", "")
            .replace("#", "")
            .replace("\t", "")
            .replace(";", "")
            .replace("'", "")
            .replace('"', '')
            .replace("{", "(")
            .replace("}", ")")
            .replace("`", "")
            .replace("__", "_")
            .strip()
        )
        return str(name)

    @staticmethod
    def short_name(name: str):
        if len(name) > 100:
            res_name = name[:70]
        else:
            res_name = name
        return res_name

    def user_(self):
        try:
            if self.m.from_user is None:
                user = self.m.chat.title or "User"
            else:
                user = self.m.from_user.first_name
            return user
        except Exception as e:
            print(e)
            user = "User"
            return user

    @staticmethod
    def index_(index: int):
        if int(index) <= 0:
            num = 0
        else:
            num = int(index) - 1
        return num

    @staticmethod
    def resolution_(resolution: str):
        res = str(resolution).strip()
        if res not in ['144', '180', '240', '360', '480', '720', '1080']:
            quality = '360'
        else:
            quality = res
        return quality


class TgClient(TgHandler):
    async def Ask_user(self):
        userr = TgClient.user_(self)
        await self.bot.send_message(
            self.m.chat.id,
            text=Msg.TXT_MSG.format(
                user=userr
            )
        )
        inputFile = await self.bot.listen(self.m.chat.id)
        if inputFile and inputFile.document:
            if inputFile.document.mime_type not in ["text/plain", "text/html"]:
                await self.m.reply_text("Please provide a valid .txt or .html file.")
                return None
            else:
                txt_name = (inputFile.document.file_name or "file").replace("_", " ")
                x = await TgClient.downloadMedia(
                    self,
                    inputFile
                )
                try:
                    await inputFile.delete(True)
                except Exception:
                    pass

            if inputFile.document.mime_type == "text/plain":
                nameLinks = await TgClient.readTxt(self, x)
                try:
                    Token = inputFile.caption
                except Exception:
                    Token = None

            elif inputFile.document.mime_type == "text/html":
                nameLinks = parse_html(x)
                Token = None
                if os.path.exists(x):
                    os.remove(x)

            if not nameLinks:
                await self.m.reply_text("No valid links found in the provided file.")
                return None

            await self.bot.send_message(
                self.m.chat.id,
                text=Msg.CMD_MSG_1.format(
                    txt=txt_name, no_of_links=len(nameLinks))
            )
            user_index = await self.bot.listen(self.m.chat.id)
            try:
                index = int(user_index.text.strip())
            except Exception:
                index = 1
            num = TgClient.index_(index=index)

            await self.bot.send_message(
                self.m.chat.id,
                text="**Send Caption :-**"
            )
            user_caption = await self.bot.listen(self.m.chat.id)
            caption = user_caption.text or ""

            await self.bot.send_message(
                self.m.chat.id,
                text="**Send Quality (Default is 360) :-**"
            )
            user_quality = await self.bot.listen(self.m.chat.id)
            resolution = user_quality.text or "360"
            quality = TgClient.resolution_(resolution=resolution)

            return nameLinks, num, caption, quality, Token, txt_name, userr
        else:
            await self.m.reply_text("No document received.")
            return None

    async def thumb(self):
        t = await self.bot.ask(
            self.m.chat.id,
            "**Send Thumb JPEG/PNG or Telegraph Link or type 'no' :-**"
        )
        thumb = "no"
        if t and t.text:
            thumb = t.text.strip()
        elif t and t.photo:
            thumb = await TgClient.downloadMedia(self, t)
        else:
            thumb = "no"
        return thumb

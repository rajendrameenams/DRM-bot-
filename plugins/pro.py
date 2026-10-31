from pyrogram import filters, Client as AFK
from main import LOGGER as LOGS, prefixes, Config, Msg, AUTH_FILTER
from pyrogram.types import Message
from handlers.tg import TgClient, TgHandler
import os
import sys
import shutil
import time
from handlers.downloader import download_handler, get_link_atributes
from handlers.uploader import Upload_to_Tg


@AFK.on_message(
    AUTH_FILTER & filters.incoming & filters.command("start", prefixes=prefixes)
)
async def start_msg(bot: AFK, m: Message):
    await bot.send_message(
        chat_id=m.chat.id,
        text=Msg.START_MSG
    )


@AFK.on_message(
    AUTH_FILTER & filters.incoming & filters.command("restart", prefixes=prefixes)
)
async def restart_handler(_, m: Message):
    if os.path.exists(Config.DOWNLOAD_LOCATION):
        shutil.rmtree(Config.DOWNLOAD_LOCATION, ignore_errors=True)
    os.makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)
    await m.reply_text(Msg.RESTART_MSG, quote=True)
    os.execl(sys.executable, sys.executable, *sys.argv)


@AFK.on_message(
    AUTH_FILTER & filters.incoming & filters.command("pro", prefixes=prefixes)
)
async def Pro(bot: AFK, m: Message):
    error_list = []
    sPath = f"{Config.DOWNLOAD_LOCATION}/{m.chat.id}"
    tPath = f"{Config.DOWNLOAD_LOCATION}/FILE/{m.chat.id}"
    os.makedirs(sPath, exist_ok=True)
    BOT = TgClient(bot, m, sPath)
    try:
        user_res = await BOT.Ask_user()
        if not user_res:
            return
        nameLinks, num, caption, quality, Token, txt_name, userr = user_res
        Thumb = await BOT.thumb()
    except Exception as e:
        LOGS.error(f"User input error: {e}")
        await m.reply_text("Wrong Input")
        return

    for i in range(num, len(nameLinks)):
        caption_name = ""
        url = ""
        Show = None
        try:
            raw_title = nameLinks[i][0]
            link = nameLinks[i][1].strip()
            name = BOT.parse_name(raw_title)

            # Resolution tag from user selection
            wxh = get_link_atributes().get_height_width(link=link, Q=quality)
            if wxh:
                wxh = f" {wxh}"

            caption_name = f"**{str(i+1).zfill(3)}.** - {name}{wxh}"
            clean_short_name = BOT.short_name(name)
            file_name = f"{str(i+1).zfill(3)}. - {clean_short_name}{wxh}".strip()
            print(f"Processing ({i+1}/{len(nameLinks)}): {caption_name} -> {link}")

            Show = await bot.send_message(
                chat_id=m.chat.id,
                text=Msg.SHOW_MSG.format(
                    file_name=file_name,
                    file_link=link,
                ),
                disable_web_page_preview=True
            )

            url = get_link_atributes().input_url(link=link, Q=quality)
            DL = download_handler(name=file_name, url=url,
                                  path=sPath, Token=Token, Quality=quality)
            dl_file = await DL.start_download()

            if dl_file and os.path.isfile(dl_file):
                if dl_file.endswith(".mp4"):
                    cap = f"{caption_name}.mp4\n\n<b>𝗕𝗮𝘁𝗰𝗵 𝗡𝗮𝗺𝗲 : </b>{caption}\n\n<b>𝗘𝘅𝘁𝗿𝗮𝗰𝘁𝗲𝗱 𝗯𝘆 ➤ </b> **{userr}**"
                    UL = Upload_to_Tg(bot=bot, m=m, file_path=dl_file, name=caption_name,
                                      Thumb=Thumb, path=sPath, show_msg=Show, caption=cap)
                    await UL.upload_video()
                else:
                    ext = dl_file.split(".")[-1]
                    cap = f"{caption_name}.{ext}\n\n<b>𝗕𝗮𝘁𝗰𝗵 𝗡𝗮𝗺𝗲 : </b>{caption}\n\n<b>𝗘𝘅𝘁𝗿𝗮𝗰𝘁𝗲𝗱 𝗯𝘆 ➤ </b> **{userr}**"
                    UL = Upload_to_Tg(bot=bot, m=m, file_path=dl_file, name=caption_name,
                                      Thumb=Thumb, path=sPath, show_msg=Show, caption=cap)
                    await UL.upload_doc()
            else:
                error_list.append(f"{caption_name} (Link 404 or Download Failed)\n")
                LOGS.warning(f"Download failed for {caption_name}: {url}")
                if Show:
                    try:
                        await Show.edit(f"⚠️ **Failed / Expired Link (HTTP 404):**\n`{file_name}`")
                    except Exception:
                        pass
        except Exception as r:
            LOGS.error(f"Download processing error: {r}")
            error_list.append(f"{caption_name} ({r})\n")
            if Show:
                try:
                    await Show.edit(f"⚠️ **Error:** `{r}`")
                except Exception:
                    pass
            continue

    if os.path.exists(sPath):
        shutil.rmtree(sPath, ignore_errors=True)
    if os.path.exists(tPath):
        if os.path.isfile(tPath):
            try:
                os.remove(tPath)
            except Exception:
                pass
        else:
            shutil.rmtree(tPath, ignore_errors=True)

    await BOT.linkMsg2(error_list)
    await m.reply_text("Done")

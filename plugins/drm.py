from pyrogram import filters, Client as ace
from main import LOGGER, prefixes, AUTH_FILTER, Config
from pyrogram.types import Message
import os
import shutil
from handlers.uploader import Upload_to_Tg
from handlers.tg import TgClient


@ace.on_message(
    AUTH_FILTER & filters.incoming & filters.command("drm", prefixes=prefixes)
)
async def drm(bot: ace, m: Message):
    path = f"{Config.DOWNLOAD_LOCATION}/{m.chat.id}"
    tPath = f"{Config.DOWNLOAD_LOCATION}/THUMB/{m.chat.id}"
    os.makedirs(path, exist_ok=True)

    inputData = await bot.ask(m.chat.id, "**Send in separate lines:**\n\nMPD\nNAME\nQUALITY\nCAPTION")
    if not inputData or not inputData.text:
        await m.reply_text("No input received.")
        return

    lines = [line.strip() for line in inputData.text.strip().split("\n") if line.strip()]
    if len(lines) < 4:
        await m.reply_text("Invalid format. Please send 4 lines:\n\nMPD\nNAME\nQUALITY\nCAPTION")
        return

    mpd = lines[0]
    raw_name = lines[1]
    Q = lines[2]
    CP = "\n".join(lines[3:])
    name = f"{TgClient.parse_name(raw_name)} ({Q}p)"
    print(mpd, name, Q)

    inputKeys = await bot.ask(m.chat.id, "**Send Kid:Key (one per line, e.g. 1:key or kid:key)**")
    if not inputKeys or not inputKeys.text:
        await m.reply_text("No keys received.")
        return

    keysData = [k.strip() for k in inputKeys.text.strip().split("\n") if k.strip()]
    keys = ""
    for k in keysData:
        if k.startswith("--key"):
            keys += f"{k} "
        else:
            keys += f"--key {k} "

    BOT = TgClient(bot, m, path)
    Thumb = await BOT.thumb()
    prog = await bot.send_message(m.chat.id, f"**Downloading DRM Video!** - [{name}]({mpd})", disable_web_page_preview=True)

    cmd1 = f'yt-dlp -o "{path}/fileName.%(ext)s" -f "bestvideo[height<={int(Q)}]+bestaudio" --allow-unplayable-format --external-downloader aria2c "{mpd}"'
    os.system(cmd1)
    avDir = os.listdir(path) if os.path.exists(path) else []
    print(avDir)
    print("Decrypting")
    
    try:
        for data in avDir:
            if data.endswith("mp4") and data != "video.mp4":
                cmd2 = f'mp4decrypt {keys} --show-progress "{path}/{data}" "{path}/video.mp4"'
                os.system(cmd2)
                if os.path.exists(f'{path}/{data}'):
                    try:
                        os.remove(f'{path}/{data}')
                    except Exception:
                        pass
            elif data.endswith("m4a") and data != "audio.m4a":
                cmd3 = f'mp4decrypt {keys} --show-progress "{path}/{data}" "{path}/audio.m4a"'
                os.system(cmd3)
                if os.path.exists(f'{path}/{data}'):
                    try:
                        os.remove(f'{path}/{data}')
                    except Exception:
                        pass

        cmd4 = f'ffmpeg -y -i "{path}/video.mp4" -i "{path}/audio.m4a" -c copy "{path}/{name}.mp4"'
        os.system(cmd4)
        if os.path.exists(f"{path}/video.mp4"):
            try:
                os.remove(f"{path}/video.mp4")
            except Exception:
                pass
        if os.path.exists(f"{path}/audio.m4a"):
            try:
                os.remove(f"{path}/audio.m4a")
            except Exception:
                pass
        final_file = f"{path}/{name}.mp4"
        if not os.path.isfile(final_file):
            raise Exception("Video decrypt/merge failed. Output file was not created.")

        cc = f"{name}.mp4\n\n**Description:-**\n{CP}"
        UL = Upload_to_Tg(bot=bot, m=m, file_path=final_file, name=name,
                          Thumb=Thumb, path=path, show_msg=prog, caption=cc)
        await UL.upload_video()
        print("Done")
    except Exception as e:
        try:
            await prog.delete(True)
        except Exception:
            pass
        await m.reply_text(f"**Error**\n\n`{str(e)}`")
    finally:
        if os.path.exists(tPath):
            shutil.rmtree(tPath, ignore_errors=True)
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
        await m.reply_text("Done")

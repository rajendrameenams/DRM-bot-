from pyrogram import filters, Client as ace
from main import LOGGER as LOGS, prefixes, AUTH_FILTER, Config
from pyrogram.types import Message
import os
import shutil
from handlers.uploader import Upload_to_Tg
import requests
import wget
import img2pdf


@ace.on_message(
    AUTH_FILTER & filters.incoming & filters.command("ytc", prefixes=prefixes)
)
async def drm(bot: ace, m: Message):
    path = f"{Config.DOWNLOAD_LOCATION}/{m.chat.id}"
    tPath = f"{Config.DOWNLOAD_LOCATION}/PHOTO/{m.chat.id}"
    os.makedirs(path, exist_ok=True)
    os.makedirs(tPath, exist_ok=True)

    pages_msg = await bot.ask(m.chat.id, "Send in separate lines:\n\nPages Range (e.g. 1:100)\nBook Name\nBookId")
    if not pages_msg or not pages_msg.text:
        await m.reply_text("No input received.")
        return

    parts = [p.strip() for p in str(pages_msg.text).strip().split("\n") if p.strip()]
    if len(parts) < 3:
        await m.reply_text("Invalid format. Please send:\nPages Range (e.g. 1:100)\nBook Name\nBookId")
        return

    pages, Book_Name, bid = parts[0], parts[1], parts[2]

    url = "http://yctpublication.com/master/api/MasterController/getPdfPage?book_id={bid}&page_no={pag}&user_id=14593&token=eyJhbGciOiJSUzI1NiIsImtpZCI6IjVkZjFmOTQ1ZmY5MDZhZWFlZmE5M2MyNzY5OGRiNDA2ZDYwNmIwZTgiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiIyMjkwMDE2MzYyNTQtZWZjcDlqYm4wMzJzbmpmc"
    page = pages.split(":")
    if len(page) < 2:
        await m.reply_text("Invalid page range format. Example format: 1:100")
        return

    try:
        page_1 = int(page[0])
        last_page = int(page[1]) + 1
    except ValueError:
        await m.reply_text("Page numbers must be integers.")
        return

    def down(image_link, file_name):
        dest = f"{tPath}/{file_name}.jpg"
        wget.download(image_link, dest)
        return dest

    def downloadPdf(title, imagelist):
        pdf_path = f"{path}/{title}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(img2pdf.convert(imagelist))
        return pdf_path

    Show = await bot.send_message(
        m.chat.id,
        "Downloading Pages..."
    )
    IMG_LIST = []

    for i in range(page_1, last_page):
        try:
            print(f"Downloading Page - {str(i).zfill(3)}")
            name = f"{str(i).zfill(3)}. page_no_{str(i)}"
            y = down(image_link=url.format(pag=i, bid=bid), file_name=name)
            if os.path.exists(y):
                IMG_LIST.append(y)
        except Exception as e:
            LOGS.warning(f"Failed to download page {i}: {e}")
            continue

    if not IMG_LIST:
        await m.reply_text("Failed to download any pages for this book.")
        if os.path.exists(tPath):
            shutil.rmtree(tPath, ignore_errors=True)
        return

    PDF = None
    try:
        PDF = downloadPdf(title=Book_Name, imagelist=IMG_LIST)
    except Exception as e1:
        await m.reply_text(f"PDF creation failed: {e1}")

    if PDF and os.path.exists(PDF):
        UL = Upload_to_Tg(bot=bot, m=m, file_path=PDF, name=Book_Name,
                          Thumb="no", path=path, show_msg=Show, caption=Book_Name)
        await UL.upload_doc()
        print("Done")

    if os.path.exists(tPath):
        shutil.rmtree(tPath, ignore_errors=True)
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)

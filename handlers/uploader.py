#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) AFK

import subprocess
import wget
import os
import time
from helpers.toolkit import Tools, Vidtools
from main import Config, Msg, LOGGER as LOGS
from helpers.prog_bar import progress_for_pyrogram
from pyrogram import Client as AFK
from pyrogram.types import Message


class Upload_to_Tg:
    def __init__(self, bot: AFK, m: Message, name: str, file_path, path, Thumb, show_msg: Message, caption: str) -> None:
        self.bot = bot
        self.m = m
        self.name = name
        self.file_path = file_path
        self.path = path
        self.thumb = Thumb
        self.temp_dir = f"{path}/{name}"
        self.show_msg = show_msg
        self.caption = caption

    async def get_thumb_duration(self):
        duration = 0
        try:
            duration = Vidtools.get_duration(self.file_path)
        except Exception:
            try:
                duration = int(Tools.duration(self.file_path))
            except Exception:
                duration = 0

        thumbnail = None
        if self.thumb and isinstance(self.thumb, str) and self.thumb.startswith(("http://", "https://")):
            try:
                wget.download(self.thumb, f"{self.temp_dir}.jpg")
                thumbnail = f"{self.temp_dir}.jpg"
            except Exception:
                thumbnail = None
        elif self.thumb and isinstance(self.thumb, str) and os.path.isfile(self.thumb):
            thumbnail = self.thumb
        else:
            try:
                ttl = (duration / 2) if duration else 1
                thumbnail = await Vidtools.take_screen_shot(self.file_path, self.name, self.path, ttl)
            except Exception:
                pass
            if not thumbnail or not os.path.isfile(thumbnail):
                try:
                    subprocess.run(
                        f'ffmpeg -y -i "{self.file_path}" -ss 00:00:01 -vframes 1 "{self.temp_dir}.jpg"', shell=True)
                    if os.path.isfile(f"{self.temp_dir}.jpg"):
                        thumbnail = f"{self.temp_dir}.jpg"
                except Exception:
                    thumbnail = None
        return duration, thumbnail

    async def get_doc_thumb(self):
        doc_thumbnail = None
        if self.thumb and isinstance(self.thumb, str) and self.thumb.startswith(("http://", "https://")):
            try:
                wget.download(self.thumb, f"{self.temp_dir}.jpg")
                doc_thumbnail = f"{self.temp_dir}.jpg"
            except Exception:
                doc_thumbnail = None
        elif self.thumb and isinstance(self.thumb, str) and os.path.isfile(self.thumb):
            doc_thumbnail = self.thumb
        return doc_thumbnail

    async def upload_video(self):
        duration, thumbnail = await self.get_thumb_duration()
        try:
            w, h = await Vidtools.get_width_height(self.file_path)
        except Exception:
            w, h = 1280, 720
        start_time = time.time()
        try:
            await self.bot.send_video(
                chat_id=self.m.chat.id,
                video=self.file_path,
                supports_streaming=True,
                caption=self.caption,
                duration=duration,
                thumb=thumbnail,
                width=w,
                height=h,
                progress=progress_for_pyrogram,
                progress_args=(
                    Msg.CMD_MSG_2.format(
                        file_name=f"{self.name}"), self.show_msg, start_time
                )
            )
        except Exception as e:
            LOGS.error(f"Video upload failed, attempting document upload: {e}")
            try:
                await self.bot.send_document(
                    chat_id=self.m.chat.id,
                    document=self.file_path,
                    caption=self.caption,
                    thumb=thumbnail,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Msg.CMD_MSG_2.format(
                            file_name=f"{self.name}"), self.show_msg, start_time
                    )
                )
            except Exception as e2:
                LOGS.error(f"Document upload also failed: {e2}")
        finally:
            if os.path.exists(self.file_path):
                try:
                    os.remove(self.file_path)
                except Exception:
                    pass
            if thumbnail and os.path.exists(thumbnail) and thumbnail != self.thumb:
                try:
                    os.remove(thumbnail)
                except Exception:
                    pass
            try:
                await self.show_msg.delete(True)
            except Exception:
                pass

    async def upload_doc(self):
        start_time = time.time()
        doc_thumb = await self.get_doc_thumb()
        try:
            await self.bot.send_document(
                chat_id=self.m.chat.id,
                document=self.file_path,
                caption=self.caption,
                thumb=doc_thumb,
                progress=progress_for_pyrogram,
                progress_args=(
                    Msg.CMD_MSG_2.format(
                        file_name=f"{self.name}"), self.show_msg, start_time
                )
            )
        except Exception as e:
            LOGS.info(f"Upload doc error: {e}")
        finally:
            if os.path.exists(self.file_path):
                try:
                    os.remove(self.file_path)
                except Exception:
                    pass
            if doc_thumb and os.path.exists(doc_thumb) and doc_thumb != self.thumb:
                try:
                    os.remove(doc_thumb)
                except Exception:
                    pass
            try:
                await self.show_msg.delete(True)
            except Exception:
                pass

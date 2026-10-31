#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) AFK

import os
import subprocess
import datetime
import asyncio
import wget
import requests
import time
import aiohttp
import aiofiles
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from main import Config


class Tools(object):
    @staticmethod
    def duration(filename):
        try:
            result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                    "format=duration", "-of",
                                     "default=noprint_wrappers=1:nokey=1", filename],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            return float(result.stdout.strip())
        except Exception:
            return 0.0

    @staticmethod
    async def aio(url, name, path):
        k = f"{path}/{name}.pdf"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(k, mode='wb') as f:
                        await f.write(await resp.read())
        return k

    @staticmethod
    def vid_info(info):
        info = info.strip().split("\n")
        new_info = dict()
        temp = []
        for i in info:
            i = str(i)
            if "[" not in i and '---' not in i:
                while "  " in i:
                    i = i.replace("  ", " ")
                i = i.strip().split("|")[0].split(" ", 3)
                try:
                    if len(i) > 2 and "RESOLUTION" not in i[2] and i[2] not in temp and "audio" not in i[2]:
                        temp.append(i[2])
                        new_info.update({f'{i[2]}': f'{i[0]}'})
                except Exception:
                    pass
        return new_info

    @staticmethod
    async def vrun(cmd):
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()
        if proc.returncode == 1:
            return False
        if stdout:
            return f'[stdout]\n{stdout.decode()}'
        if stderr:
            return f'[stderr]\n{stderr.decode()}'
        return None

    @staticmethod
    def old_download(url, file_name, chunk_size=1024 * 10):
        if os.path.exists(file_name):
            os.remove(file_name)
        r = requests.get(url, allow_redirects=True, stream=True)
        with open(file_name, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    fd.write(chunk)
        return file_name

    @staticmethod
    def human_readable_size(size, decimal_places=2):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if size < 1024.0 or unit == 'PB':
                break
            size /= 1024.0
        return f"{size:.{decimal_places}f} {unit}"

    @staticmethod
    def time_name():
        date = datetime.date.today()
        now = datetime.datetime.now()
        current_time = now.strftime("%H : %M : %S")
        return f"📅 **Date** ~ `{date}`\n🕰 **Time** ~ `{current_time}`"

    @staticmethod
    def convert(seconds):
        return time.strftime("%H:%M:%S", time.gmtime(seconds))

    @staticmethod
    async def pdf_thumb(Thumb, name, path):
        if Thumb and isinstance(Thumb, str) and Thumb.startswith(("http://", "https://")):
            try:
                wget.download(Thumb, f"{path}/{name}.jpg")
                return f"{path}/{name}.jpg"
            except Exception:
                pass
        return None


class Vidtools(object):
    @staticmethod
    async def take_screen_shot(video_file, name, path, ttl):
        out_put_file_name = f"{path}/{name}.jpg"
        if str(video_file).upper().endswith(("MKV", "MP4", "WEBM")):
            file_genertor_command = [
                "ffmpeg",
                "-y",
                "-ss",
                str(ttl),
                "-i",
                str(video_file),
                "-vframes",
                "1",
                out_put_file_name
            ]
            try:
                process = await asyncio.create_subprocess_exec(
                    *file_genertor_command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await process.communicate()
            except Exception:
                pass

        if os.path.exists(out_put_file_name):
            return out_put_file_name
        return None

    @staticmethod
    def get_duration(filepath):
        try:
            parser = createParser(filepath)
            if parser:
                with parser:
                    metadata = extractMetadata(parser)
                    if metadata and metadata.has("duration"):
                        return metadata.get('duration').seconds
        except Exception:
            pass
        return 0

    @staticmethod
    async def get_width_height(filepath):
        try:
            parser = createParser(filepath)
            if parser:
                with parser:
                    metadata = extractMetadata(parser)
                    if metadata and metadata.has("width") and metadata.has("height"):
                        return metadata.get("width"), metadata.get("height")
        except Exception:
            pass
        return 1280, 720

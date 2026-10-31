import subprocess
from subprocess import getoutput
from handlers.url_scripts import ParseLink
from main import LOGGER as LOGS
import asyncio
import requests
import aiohttp
import aiofiles
import os

cc = 0

EXTRA_LINKS = {
    "CP_VIMEO_TYPE": ("https://videos.classplusapp.com/", "https://api.edukemy.com/videodetails/", "https://tencdn.classplusapp.com", "https://covod.testbook.com/"),
    "GUIDELY_LINK": ("https://guidely.prepdesk.in/api/", "https://ibpsguide.prepdesk.in/api/"),
    "SET3": ("https://ply-404.herokuapp.com/"),
    "EDU_PDF": ("https://edukemy-v2-assets.s3.ap-south-1.amazonaws.com/course_content/"),
    "VISION_PDF": ("http://www.visionias.in/student/pt/video_student/handout", "http://www.visionias.in/student/3.php?"),
    "TOPRANKER": ("https://live.anytimelearning.in/", "https://onlinetest.sure60.com/"),
}


class get_link_atributes:
    @staticmethod
    def get_wxh(ytdlp):
        try:
            output = getoutput(f"{ytdlp} -e --get-filename -R 25")
            lines = str(output).split("\n")
            if len(lines) > 1:
                widthXheight = lines[1].strip()
            else:
                widthXheight = lines[0].strip() if lines else ".N.A"
            LOGS.info(widthXheight)
            return widthXheight
        except Exception as e1:
            LOGS.info(str(e1))
            widthXheight = ".N.A"
            return widthXheight

    @staticmethod
    def get_height_width(link: str, Q: str):
        url = get_link_atributes().input_url(link=link, Q=Q)
        YTF = f"bv[height<=?{Q}]+ba/[height<=?{Q}]+ba/[height>=?{Q}]+ba/[height<=?{Q}]/[height>=?{Q}]/b"
        if link.endswith("ankul60"):
            url = ParseLink.topranker_link(link)
            if "m3u8" in url:
                rout = ParseLink.rout(url=link, m3u8=url)
                os.system(f'curl "{rout}" -c "cooks.txt"')
                cook = "cooks.txt"
                YTDLP = f'yt-dlp -i --no-check-certificate -f "{YTF}" --no-warning "{url}" --cookies "{cook}" -o "%(resolution)s"'
                wXh = get_link_atributes().get_wxh(YTDLP)
                if os.path.exists(cook):
                    try:
                        os.remove(cook)
                    except Exception:
                        pass
                return wXh
            elif "youtu" in url:
                YTDLP = f'yt-dlp -i --no-check-certificate -f "{YTF}" --no-warning "{url}" --progress -o "%(resolution)s"'
                wXh = get_link_atributes().get_wxh(YTDLP)
                return wXh
        else:
            YTDLP = f'yt-dlp -i --no-check-certificate -f "{YTF}" --no-warning "{url}" --progress --remux-video mp4 -o "%(resolution)s"'
            wXh = get_link_atributes().get_wxh(YTDLP)
            return wXh

    @staticmethod
    def input_url(link: str, Q: str):
        if link.startswith("https://videos.classplusapp.com/"):
            if link.split("?")[-1].startswith("auth_key="):
                url = link
                return url
            else:
                url = ParseLink.classplus_link(link=link)
                return url
        elif link.startswith(("https://vod.visionias.in/player/index.php", "https://vod.visionias.in/player_v2/index.php")):
            url = ParseLink.vision_m3u8_link(link, Q)
            return url
        elif link.startswith(("https://covod.testbook.com/", "https://tencdn.classplusapp.com")):
            url = ParseLink.classplus_link(link=link)
            return url
        elif link.startswith("http://www.visionias.in/student/videoplayer_v2/?"):
            url = ParseLink.vision_mpd_link(link)
            return url
        elif link.startswith("https://d1d34p8vz63oiq.cloudfront.net/"):
            url = ParseLink.is_pw(link)
            return url
        elif "drive" in link:
            url = ParseLink.is_drive_pdf(url=link)
            return url
        elif link.startswith("https://videotest.adda247.com/"):
            parts = link.split("https://videotest.adda247.com/")
            if len(parts) > 1 and not link.startswith("https://videotest.adda247.com/demo/"):
                url = f'https://videotest.adda247.com/demo/{parts[1]}'
                return url
            else:
                return link
        elif not link.startswith("http"):
            if "*" in link:
                url = ParseLink.cw_url2(link.split("*")[0]) + link.split("*")[1]
            else:
                url = link
            print(url)
            return url
        else:
            url = link
            return url


class Download_Methods:
    def __init__(self, name: str, url: str, path, Token: str, Quality: str) -> None:
        self.url = url
        self.name = name
        self.Q = Quality
        self.path = path
        self.token = Token
        self.temp_dir = f"{path}/{name}"

    async def m3u82mp4(self, file):
        if not file or not os.path.exists(file):
            return None
        out_file = f"{self.temp_dir}.mp4"
        subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-protocol_whitelist", "file,http,https,tcp,tls,crypto",
                "-i", file, "-c", "copy", "-bsf:a", "aac_adtstoasc", out_file
            ]
        )
        if os.path.exists(file):
            try:
                os.remove(file)
            except Exception:
                pass
        if os.path.isfile(out_file):
            return out_file
        return None

    def addapdf(self):
        cookies = {
            'cp_token': f'{self.token}',
        }
        headers = {
            'Host': 'store.adda247.com',
            'user-agent': 'Mozilla/5.0 (Linux; Android 11; moto g(40) fusion Build/RRI31.Q1-42-51-8; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/97.0.4692.98 Mobile Safari/537.36',
            'accept': '*/*',
            'x-requested-with': 'com.adda247.app',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://store.adda247.com/build/pdf.worker.js',
            'accept-language': 'en-US,en;q=0.9',
        }
        response = requests.get(
            f'{self.url}', cookies=cookies, headers=headers)

        out_file = f'{self.temp_dir}.pdf'
        with open(out_file, 'wb') as f:
            f.write(response.content)
        return out_file

    async def aio(self):
        k = f"{self.temp_dir}.pdf"
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(k, mode='wb') as f:
                        await f.write(await resp.read())
        return k

    def cwpdf(self):
        headers = {
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; Redmi Note 5 Pro MIUI/V11.0.5.0.PEIMIXM)',
            'Host': 'elearn.crwilladmin.com',
            'Connection': 'Keep-Alive',
        }
        r_pdf = requests.get(self.url, headers=headers)
        out_file = f'{self.temp_dir}.pdf'
        with open(out_file, 'wb') as f:
            f.write(r_pdf.content)
        if os.path.isfile(out_file):
            return out_file
        return None

    def visionpdf(self):
        cookies = {
            'PHPSESSID': self.token,
        }
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }
        response = requests.get(self.url, cookies=cookies,
                                headers=headers, verify=False)
        out_file = f"{self.temp_dir}.pdf"
        with open(out_file, "wb") as f:
            f.write(response.content)
        if os.path.isfile(out_file):
            return out_file
        return None

    async def Guidely(self):
        try:
            res = requests.get(self.url).json()
            z = res['item']['data']['key']
            mpd = res['item']['data']['file']
        except Exception as e:
            LOGS.error(f"Guidely parsing failed: {e}")
            return None

        cmd1 = f'yt-dlp -o "{self.path}/Name.%(ext)s" -f "bestvideo[height<={self.Q}]+bestaudio" --allow-unplayable-format --external-downloader aria2c "{mpd}"'
        os.system(cmd1)
        AV = os.listdir(self.path) if os.path.exists(self.path) else []
        for d in AV:
            if d.endswith("mp4") and d != "video.mp4":
                cmd2 = f'mp4decrypt --key 1:{z} "{self.path}/{d}" "{self.path}/video.mp4"'
                os.system(cmd2)
                if os.path.exists(f"{self.path}/{d}"):
                    try:
                        os.remove(f"{self.path}/{d}")
                    except Exception:
                        pass
            elif d.endswith("m4a") and d != "audio.m4a":
                cmd3 = f'mp4decrypt --key 1:{z} "{self.path}/{d}" "{self.path}/audio.m4a"'
                os.system(cmd3)
                if os.path.exists(f"{self.path}/{d}"):
                    try:
                        os.remove(f"{self.path}/{d}")
                    except Exception:
                        pass
        cmd4 = f'ffmpeg -y -i "{self.path}/video.mp4" -i "{self.path}/audio.m4a" -c copy "{self.temp_dir}.mp4"'
        os.system(cmd4)
        if os.path.exists(f"{self.path}/video.mp4"):
            try:
                os.remove(f"{self.path}/video.mp4")
            except Exception:
                pass
        if os.path.exists(f"{self.path}/audio.m4a"):
            try:
                os.remove(f"{self.path}/audio.m4a")
            except Exception:
                pass
        out_file = f"{self.temp_dir}.mp4"
        if os.path.isfile(out_file):
            return out_file
        return None

    def get_drive_link_type(self):
        try:
            resp = requests.get(self.url, stream=True)
            c_type = resp.headers.get('Content-Type', '').lower()
            return c_type
        except Exception as e2:
            LOGS.error(str(e2))
            return ""

    def dot_ws_link(self):
        response = requests.get(self.url, stream=True)
        LOGS.info(response.status_code)
        out_file = f"{self.temp_dir}.html"
        with open(out_file, "wb") as f:
            f.write(response.content)
        if os.path.isfile(out_file):
            return out_file
        return None


class download_handler(Download_Methods):
    def run_cmd(self, cmd):
        LOGS.info(cmd)
        try:
            subprocess.run(cmd, shell=True)
        except Exception as e_:
            LOGS.info(str(e_))
        file_path = f"{self.temp_dir}.mp4"
        return file_path

    def recursive(self, cmd):
        LOGS.info(cmd)
        global cc
        if cc >= 5:
            return None
        dl = subprocess.run(cmd, shell=True)
        if dl.returncode != 0:
            cc += 1
            return download_handler.recursive(self, cmd=cmd)
        cc = 0
        file_path = f"{self.temp_dir}.mp4"
        LOGS.info(str(file_path))
        return file_path

    async def recursive_asyno(self, cmd):
        LOGS.info(cmd)
        global cc
        if cc >= 5:
            return None
        process = await asyncio.create_subprocess_shell(
            cmd=cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        print("Started:", cmd, "(pid = " + str(process.pid) + ")", flush=True)
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            cc += 1
            return await download_handler.recursive_asyno(self, cmd=cmd)
        cc = 0
        file_path = f"{self.temp_dir}.mp4"
        LOGS.info(str(file_path))
        return file_path

    async def start_download(self):
        YTF = f"bv[height<=?{self.Q}]+ba/[height<=?{self.Q}]+ba/[height>=?{self.Q}]+ba/[height<=?{self.Q}]/[height>=?{self.Q}]/b"
        YTDLP = f'yt-dlp -i --no-check-certificate -f "{YTF}" --no-warning "{self.url}" --merge-output-format mp4 --remux-video mp4 -o "{self.temp_dir}.%(ext)s"'
        CMD = f"{YTDLP} -R 25 --fragment-retries 25 --external-downloader aria2c --downloader-args 'aria2c: -x 16 -j 32'"

        if self.url.startswith('https://elearn.crwilladmin.com/') and self.url.endswith('.pdf'):
            file_name = download_handler.cwpdf(self)
            return file_name

        if self.url.endswith(".pdf") or ".pdf" in self.url or self.url.startswith(EXTRA_LINKS['EDU_PDF']):
            file_name = await download_handler.aio(self)
            return file_name

        if self.url.startswith("https://store.adda247.com/"):
            file_name = download_handler.addapdf(self)
            return file_name
        if self.url.startswith(EXTRA_LINKS['VISION_PDF']):
            file_name = download_handler.visionpdf(self)
            return file_name

        if self.url.startswith(EXTRA_LINKS['GUIDELY_LINK']):
            file_name = await download_handler.Guidely(self)
            return file_name

        if self.url.startswith("https://videos.sproutvideo.com/"):
            file = ParseLink.olive(self.Q, self.url, self.path)
            file_name = await download_handler.m3u82mp4(self, file)
            return file_name
        if "drive" in self.url:
            c_type = download_handler.get_drive_link_type(self)
            if c_type and "pdf" in c_type:
                file_name = await download_handler.aio(self)
                return file_name
            elif c_type and "video" in c_type:
                file_name = await download_handler.recursive_asyno(self, cmd=CMD)
                return file_name
            else:
                file_name = await download_handler.aio(self)
                return file_name

        if self.url.endswith("ankul60"):
            m3u8url = ParseLink.topranker_link(self.url)
            if "m3u8" in m3u8url:
                rout = ParseLink.rout(url=self.url, m3u8=m3u8url)
                os.system(f'curl "{rout}" -c "cooks.txt"')
                cook = "cooks.txt"
                YTDLP = f'yt-dlp -i --no-check-certificate -f "{YTF}" --no-warning "{m3u8url}" --cookies "{cook}" --remux-video mp4 -o "{self.temp_dir}.%(ext)s"'
                CMD = f"{YTDLP} -R 25 --fragment-retries 25 --external-downloader aria2c --downloader-args 'aria2c: -x 16 -j 32'"
                file_name = await download_handler.recursive_asyno(self, cmd=CMD)
                if os.path.exists(cook):
                    try:
                        os.remove(cook)
                    except Exception:
                        pass
                return file_name
            elif "youtu" in m3u8url:
                self.url = m3u8url
                file_name = await download_handler.recursive_asyno(self, cmd=CMD)
                return file_name
        if self.url.endswith(".ws"):
            file_name = download_handler.dot_ws_link(self)
            return file_name

        else:
            file_name = download_handler.recursive(self, cmd=CMD)
            return file_name

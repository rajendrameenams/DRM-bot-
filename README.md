# Telegram DRM & Batch Extractor Bot 🚀

Yeh ek multi-talented Telegram Bot hai jo batch links, DRM videos, encrypted streams, PDFs aur text files ko download karke Telegram par upload karta hai.

---

## 🛠 Features & Fixes Done
- ✅ **VPS Ready:** 100% optimized for Ubuntu/Debian VPS (Direct & Docker deployment).
- ✅ **Environment Variables (.env):** Sabhi credentials (`BOT_TOKEN`, `API_ID`, `API_HASH`, etc.) secure tareeqe se `.env` file se load hote hain.
- ✅ **Bug Fixes:**
  - Hardcoded tokens aur channel IDs hata diye gaye hain.
  - `asyncio` pip installation conflict fix kiya gaya.
  - Pyrogram v2 & Pyromod conversation handlers optimize kiye gaye.
  - Uploader crash (attribute error `self.filename` -> `self.file_path`) fix kiya gaya.
  - Invalid file checks (`os.path.isfile(dl_file) is not None`) fix kiye gaye.
  - Bento4 `mp4decrypt` aur FFmpeg merging command syntax safe banaya gaya.
  - Memory & temporary storage cleanup har task ke baad automatic ho gaya hai.

---

## ⚙️ Configuration (.env)

Apne VPS par project folder ke andar `.env` file banayein ya edit karein:

```env
# Required: Bot token from @BotFather
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Required: Telegram API credentials from https://my.telegram.org/apps
API_ID=12345678
API_HASH=0123456789abcdef0123456789abcdef

# Optional: User IDs allowed to use the bot (comma-separated)
AUTH_USERS=123456789,987654321

# Optional: Group IDs where bot can be used (comma-separated)
GROUPS=-1001234567890

# Optional: Log Channel ID (Bot must be Admin in channel)
LOG_CH=-1001234567890
```

---

## 🚀 VPS Deployment (2 Tarike)

### Tarika 1: Docker Compose (Sabse Aasan & Recommended)

Agar aapke VPS par Docker installed hai:

1. Repository clone karein:
   ```bash
   git clone <repo_url>
   cd DRM-bot-
   ```
2. `.env` file configure karein:
   ```bash
   cp .env.sample .env
   nano .env
   ```
   *(Apna `BOT_TOKEN`, `API_ID`, `API_HASH` daalkar `Ctrl+O` fir `Enter`, aur `Ctrl+X` se save karein)*

3. Docker se run karein:
   ```bash
   docker compose up --build -d
   ```
4. Logs dekhne ke liye:
   ```bash
   docker compose logs -f
   ```

---

### Tarika 2: Direct VPS Deployment (Setup Script ke sath)

1. Repository clone karein:
   ```bash
   git clone <repo_url>
   cd DRM-bot-
   ```

2. Automatic setup script run karein:
   ```bash
   chmod +x setup_vps.sh
   ./setup_vps.sh
   ```
   *Yeh script automatically `ffmpeg`, `aria2`, `Bento4 (mp4decrypt)`, `python3-venv` aur sabhi libraries install kar dega.*

3. `.env` file configure karein:
   ```bash
   nano .env
   ```

4. Bot test karne ke liye run karein:
   ```bash
   source venv/bin/activate
   python3 main.py
   ```

---

## 🔄 24/7 Background Running (Systemd Service)

Bot ko background mein continuous chalane aur VPS restart hone par automatically start hone ke liye:

1. Service file copy karein:
   ```bash
   sudo cp drmbot.service /etc/systemd/system/drmbot.service
   ```
   *(Note: Agar project path `/root/DRM-bot-` se alag hai toh `sudo nano /etc/systemd/system/drmbot.service` karke path update karein)*

2. Service start & enable karein:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable drmbot
   sudo systemctl start drmbot
   ```

3. Status & Logs check karein:
   ```bash
   sudo systemctl status drmbot
   sudo journalctl -u drmbot -f
   ```

---

## 🎮 Commands
- `/start` - Check bot status
- `/pro` - Text (.txt) ya HTML file se batch download start karein
- `/drm` - MPD URL, Keys (Kid:Key), Quality & Caption daalkar DRM video download & decrypt karein
- `/ytc` - Book PDF download karein
- `/restart` - Temporary downloads clear karein aur bot restart karein

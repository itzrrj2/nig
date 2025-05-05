import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("media_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🧠 Platform Detector
def detect_platform(url: str) -> str:
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "tiktok.com" in url:
        return "tiktok"
    elif "instagram.com" in url:
        return "instagram"
    elif "twitter.com" in url or "x.com" in url:
        return "twitter"
    elif "spotify.com" in url:
        return "spotify"
    elif "pinterest.com" in url:
        return "pinterest"
    return "unknown"

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("🎬 Send me a media link from YouTube, Instagram, TikTok, Spotify, Pinterest, or Twitter/X.")

@app.on_message(filters.text & ~filters.command("start"))
async def handle_url(client, message: Message):
    url = message.text.strip()
    platform = detect_platform(url)

    try:
        if platform == "youtube":
            api_url = f"https://ar-api-iauy.onrender.com/ythelper?url={url}"
            resp = requests.get(api_url).json()
            buttons = []
            for option in resp.get("videos", []):
                buttons.append([InlineKeyboardButton(f'{option["quality"]} ({option["ext"]})', url=option["url"])])
            if mp3 := resp.get("mp3"):
                buttons.append([InlineKeyboardButton("🎧 MP3", url=mp3)])
            await message.reply("📥 Choose a download option:", reply_markup=InlineKeyboardMarkup(buttons))

        elif platform == "instagram":
            api_url = f"https://ar-api-iauy.onrender.com/gramsaver?url={url}"
            resp = requests.get(api_url).json()
            media_url = resp["url"]
            await message.reply_video(media_url) if "video" in media_url else await message.reply_photo(media_url)

        elif platform == "tiktok":
            api_url = f"https://ar-api-iauy.onrender.com/ttdl?url={url}"
            resp = requests.get(api_url).json()
            await message.reply_video(resp["video"], caption="🎵 TikTok")

        elif platform == "twitter":
            api_url = f"https://ar-api-iauy.onrender.com/x?url={url}"
            resp = requests.get(api_url).json()
            await message.reply_video(resp["video"], caption="🐦 Twitter")

        elif platform == "spotify":
            api_url = f"https://ar-api-iauy.onrender.com/spotifydown?download={url}"
            resp = requests.get(api_url).json()
            await message.reply_audio(resp["audio"], title=resp.get("title", "Spotify Track"))

        elif platform == "pinterest":
            try:
                pin_id = url.split("/pin/")[1].split("/")[0]
                api_url = f"https://api.pinterest.com/v3/pidgets/pins/info/?pin_ids={pin_id}"
                resp = requests.get(api_url).json()
                image_url = resp["data"]["pins"][0]["images"]["orig"]["url"]
                await message.reply_photo(image_url)
            except Exception:
                await message.reply("❌ Failed to fetch Pinterest image.")
        else:
            await message.reply("❌ Unsupported or invalid URL.")

    except Exception as e:
        await message.reply(f"❌ An error occurred: {str(e)}")

app.run()

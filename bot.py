import os
import json
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Environment Setup
API_ID = int(os.getenv("API_ID", 123456))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")

app = Client("media_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Sample responses (replace with real API responses in production)
RESPONSES = {
    "youtube": {
        "status": 200,
        "data": [
            {"quality": "720p", "url": "https://example.com/video_720p.mp4"},
            {"quality": "480p", "url": "https://example.com/video_480p.mp4"}
        ]
    },
    "instagram": {
        "status": 200,
        "data": {
            "is_video": True,
            "video_url": "https://example.com/insta_video.mp4",
            "photo_url": "https://example.com/insta_photo.jpg"
        }
    },
    "tiktok": {
        "status": 200,
        "data": {
            "type": "video",
            "url": "https://cdn.example.com/tiktok/video123.mp4"
        }
    },
    "tiktok_audio": {
        "status": 200,
        "data": {
            "type": "audio",
            "url": "https://cdn.example.com/tiktok/audio123.mp3"
        }
    },
    "spotify": {
        "status": 200,
        "data": {
            "title": "Believer",
            "downloadUrl": "https://spotidownloader6-1.onrender.com/stream/IhP3J0j9JmY"
        }
    },
    "pinterest": {
        "status": 200,
        "data": {
            "video_url": "https://example.com/pin_video.mp4",
            "image_urls": [
                "https://example.com/image1.jpg",
                "https://example.com/image2.jpg"
            ]
        }
    }
}

def generate_buttons(platform, data):
    buttons = []

    if platform == "youtube":
        for item in data.get("data", []):
            if item.get("url"):
                buttons.append([InlineKeyboardButton(f"🎞 {item['quality']}", url=item["url"])])

    elif platform == "instagram":
        if data["data"].get("is_video"):
            buttons.append([InlineKeyboardButton("📽 Video", url=data["data"]["video_url"])])
        if data["data"].get("photo_url"):
            buttons.append([InlineKeyboardButton("🖼 Image", url=data["data"]["photo_url"])])

    elif platform == "tiktok":
        buttons.append([InlineKeyboardButton("🎬 TikTok Video", url=data["data"]["url"])])

    elif platform == "tiktok_audio":
        buttons.append([InlineKeyboardButton("🎧 TikTok Audio", url=data["data"]["url"])])

    elif platform == "spotify":
        buttons.append([InlineKeyboardButton(f"🎵 {data['data']['title']}", url=data["data"]["downloadUrl"])])

    elif platform == "pinterest":
        if data["data"].get("video_url"):
            buttons.append([InlineKeyboardButton("🎥 Pinterest Video", url=data["data"]["video_url"])])
        for idx, url in enumerate(data["data"].get("image_urls", []), 1):
            buttons.append([InlineKeyboardButton(f"🖼 Image {idx}", url=url)])

    return buttons


@app.on_message(filters.command(["start"]))
async def start(client, message: Message):
    await message.reply("Welcome! Use /youtube, /instagram, /tiktok, /tiktok_audio, /spotify, or /pinterest to test buttons.")


@app.on_message(filters.command(["youtube", "instagram", "tiktok", "tiktok_audio", "spotify", "pinterest"]))
async def media_handler(client, message: Message):
    cmd = message.command[0]
    response = RESPONSES.get(cmd)

    if response and response.get("status") == 200:
        buttons = generate_buttons(cmd, response)
        await message.reply("Available download options:", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply("❌ No media found or error in response.")


app.run()

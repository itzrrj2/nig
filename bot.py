import aiohttp
import tempfile
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client("downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def download_mp4_from_formats(formats):
    async with aiohttp.ClientSession() as session:
        for fmt in formats:
            url = fmt.get("url", "")
            if ".mp4" in url:
                tmp_fd, tmp_path = tempfile.mkstemp(suffix=".mp4")
                os.close(tmp_fd)
                try:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            continue
                        with open(tmp_path, 'wb') as f:
                            while True:
                                chunk = await resp.content.read(1024 * 1024)
                                if not chunk:
                                    break
                                f.write(chunk)
                    return tmp_path
                except Exception as e:
                    print(f"Download error: {e}")
    return None

@bot.on_message(filters.command("dl"))
async def downloader(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Usage: `/dl <url>`")

    url = message.command[1]
    api = f"https://ar-api-iauy.onrender.com/aio-dl?url={url}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api) as resp:
                if resp.status != 200:
                    return await message.reply("❌ API request failed.")
                json_data = await resp.json()
        except Exception as e:
            return await message.reply(f"⚠️ Error fetching data: {e}")

    if json_data.get("status") != 200 or json_data.get("successful") != "success":
        return await message.reply(f"❌ Error: {json_data.get('data')}")

    video_info = json_data.get("data", {})
    formats = video_info.get("formats", [])
    caption = f"🎬 {video_info.get('title', 'Downloaded Video')}\n🕒 {video_info.get('duration', '')}"

    video_path = await download_mp4_from_formats(formats)
    if not video_path:
        return await message.reply("❌ Could not find or download any valid video file.")

    try:
        await message.reply_video(video=video_path, caption=caption)
    except Exception as e:
        await message.reply(f"⚠️ Failed to send video: {e}")
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

bot.run()

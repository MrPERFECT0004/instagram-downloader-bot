import os
import asyncio
import logging
import re

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile

import yt_dlp

from database import add_user, get_users, get_users_count


# ==============================
# LOGGING
# ==============================

logging.basicConfig(level=logging.INFO)


# ==============================
# TOKEN VA ADMIN
# ==============================

TOKEN = "8797451668:AAGQfzttbEjvzLanRUEApiTorAuLRPOPiy4"
ADMIN_ID = 6279872589   # bu yerga o'zingizning telegram ID

DOWNLOAD_PATH = "downloads"

if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

bot = Bot(token=TOKEN)
dp = Dispatcher()


# ==============================
# INSTAGRAM REGEX
# ==============================

INSTAGRAM_RE = r'(https?://(?:www\.)?instagram\.com/(?:p|reels|reel)/([^/?#&]+))'


# ==============================
# VIDEO YUKLAB OLISH
# ==============================

async def download_instagram_video(url, message_id):

    output_filename = f"{DOWNLOAD_PATH}/{message_id}.mp4"

    ydl_opts = {
    'format': 'best[ext=mp4]',
    'outtmpl': output_filename,
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0'
    }
}

    try:

        loop = asyncio.get_event_loop()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await loop.run_in_executor(None, lambda: ydl.download([url]))

        return output_filename

    except Exception as e:

        logging.error(f"Xatolik: {e}")

        return None


# ==============================
# START COMMAND
# ==============================

@dp.message(Command("start"))
async def start_command(message: types.Message):

    add_user(message.from_user.id)

    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "Men Instagramdan video yuklab beruvchi botman.\n"
        "Menga video yoki reels link yuboring."
    )


# ==============================
# INSTAGRAM LINK QABUL QILISH
# ==============================

@dp.message(F.text.regexp(INSTAGRAM_RE))
async def handle_instagram_link(message: types.Message):

    url = re.search(INSTAGRAM_RE, message.text).group(0)

    status_msg = await message.answer("🔄 Video tahlil qilinmoqda...")

    try:

        video_path = await download_instagram_video(url, message.message_id)

        if video_path and os.path.exists(video_path):

            await status_msg.edit_text("📤 Video yuklanmoqda...")

            video_file = FSInputFile(video_path)

            await message.answer_video(
                video=video_file,
                caption="✅ Video yuklab olindi!",
                 supports_streaming=True
            )

            os.remove(video_path)

            await status_msg.delete()

        else:

            await status_msg.edit_text(
                "❌ Videoni yuklab bo'lmadi. Havola noto'g'ri yoki video yopiq profil bo'lishi mumkin."
            )

    except Exception as e:

        logging.error(e)

        await status_msg.edit_text("⚠️ Xatolik yuz berdi.")


# ==============================
# ADMIN PANEL
# ==============================

broadcast_mode = True


@dp.message(Command("admin"))
async def admin_panel(message: types.Message):

    if message.from_user.id != ADMIN_ID:
        return

    users = get_users_count()

    text = f"""
📊 BOT STATISTIKASI

👥 Users: {users}

Admin buyruqlari:
/broadcast - hammaga xabar yuborish
"""

    await message.answer(text)


# ==============================
# BROADCAST
# ==============================

@dp.message(Command("broadcast"))
async def broadcast_command(message: types.Message):

    global broadcast_mode

    if message.from_user.id != ADMIN_ID:
        return

    broadcast_mode = True

    await message.answer("📢 Barcha userlarga yuboriladigan xabarni yozing")


@dp.message()
async def broadcast_message(message: types.Message):

    global broadcast_mode

    if broadcast_mode and message.from_user.id == ADMIN_ID:

        users = get_users()

        count = 0

        for user in users:

            try:
                await bot.send_message(user[0], message.text)
                count += 1
            except:
                pass

        broadcast_mode = False

        await message.answer(f"✅ Xabar {count} ta userga yuborildi")


# ==============================
# MAIN
# ==============================

async def main():

    print("Bot ishga tushdi...")

    await dp.start_polling(bot)


if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print("Bot to'xtatildi")    
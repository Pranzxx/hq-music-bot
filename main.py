import os
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputStream, AudioPiped
from pyrogram.raw.functions.channels import CreateChannel

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

db = sqlite3.connect("music.db", check_same_thread=False)
cur = db.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS links(
    group_id INTEGER PRIMARY KEY,
    channel_id INTEGER
)
""")
db.commit()

# USER CLIENT
user = Client("user", api_id=API_ID, api_hash=API_HASH)

# BOT CLIENT
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# VOICE
pytgcalls = PyTgCalls(user)


async def create_channel(group_title):
    result = await user.invoke(CreateChannel(
        title=f"{group_title} — High Quality VC 🔥",
        about="Auto High Quality VC"
    ))
    return result.chats[0].id


async def get_or_create_channel(group):
    cur.execute("SELECT channel_id FROM links WHERE group_id=?", (group.id,))
    row = cur.fetchone()

    if row:
        return row[0]

    channel_id = await create_channel(group.title)
    cur.execute("INSERT INTO links VALUES (?, ?)", (group.id, channel_id))
    db.commit()
    return channel_id


@bot.on_message(filters.command("play") & filters.group)
async def play(_, message):
    await message.reply("⚙️ Setting up High Quality VC…")
    channel_id = await get_or_create_channel(message.chat)

    await pytgcalls.join_group_call(
        channel_id,
        InputStream(
            AudioPiped("https://cdnsongs.com/music/data/Hindi_Movies/2019/Arijit_Singh_Hits/128/Bekhayali.mp3")
        )
    )

    link = f"https://t.me/c/{str(channel_id)[4:]}"
    await message.reply(
        "🎧 Started High Quality VC",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Join VC 🔥", url=link)]]
        )
    )


@bot.on_message(filters.command("stop") & filters.group)
async def stop(_, message):
    cur.execute("SELECT channel_id FROM links WHERE group_id=?", (message.chat.id,))
    row = cur.fetchone()

    if not row:
        return await message.reply("No VC linked.")

    try:
        await pytgcalls.leave_group_call(row[0])
    except:
        pass

    await message.reply("🛑 Stopped.")


async def main():
    await user.start()
    await bot.start()
    await pytgcalls.start()
    print("🔥 HQ Music Bot Online")
    await bot.idle()


import asyncio
asyncio.run(main())

import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
import yt_dlp

API_ID = 123456      # ganti dengan API ID
API_HASH = "39251814"
BOT_TOKEN = "e0b10019a16da0cb32fd647a0ad01ba4"

app = Client("infinitymusbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

playlist = {}   # menyimpan antrean lagu untuk tiap grup


# ------------------ Fungsi Download YouTube ------------------
def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename


# ------------------ Command: Play ------------------
@app.on_message(filters.command("play") & filters.group)
async def play(app, message):
    chat_id = message.chat.id

    if len(message.command) < 2:
        return await message.reply("Kirim judul atau link YouTube.\nContoh: `/play aku bukan jodohnya`")

    query = message.text.split(" ", 1)[1]

    msg = await message.reply("Sedang mencari lagu... 🎵")

    try:
        file = download_audio(query)
    except Exception as e:
        return await msg.edit(f"Gagal download: {e}")

    # Tambah ke playlist
    if chat_id not in playlist:
        playlist[chat_id] = []

    playlist[chat_id].append(file)

    if len(playlist[chat_id]) == 1:
        await msg.edit("Memutar musik pertama...")
        await call.join_group_call(chat_id, AudioPiped(file))
    else:
        await msg.edit("Ditambahkan ke playlist.")

# ------------------ Command: Skip ------------------
@app.on_message(filters.command("skip") & filters.group)
async def skip(_, message):
    chat_id = message.chat.id

    if chat_id in playlist and len(playlist[chat_id]) > 1:
        playlist[chat_id].pop(0)
        next_song = playlist[chat_id][0]
        await call.change_stream(chat_id, AudioPiped(next_song))
        await message.reply("Lagu diskip.")
    else:
        await message.reply("Tidak ada lagu berikutnya.")


# ------------------ Command: Pause ------------------
@app.on_message(filters.command("pause") & filters.group)
async def pause(_, message):
    await call.pause_stream(message.chat.id)
    await message.reply("⏸ Musik dijeda.")


# ------------------ Command: Resume ------------------
@app.on_message(filters.command("resume") & filters.group)
async def resume(_, message):
    await call.resume_stream(message.chat.id)
    await message.reply("▶ Musik dilanjutkan.")


# ------------------ Command: Stop ------------------
@app.on_message(filters.command("stop") & filters.group)
async def stop(_, message):
    chat_id = message.chat.id
    playlist[chat_id] = []
    await call.leave_group_call(chat_id)
    await message.reply("⛔ Musik dihentikan.")


# ------------------ Command: Playlist ------------------
@app.on_message(filters.command("playlist") & filters.group)
async def show_playlist(_, message):
    chat_id = message.chat.id
    if chat_id not in playlist or len(playlist[chat_id]) == 0:
        return await message.reply("Playlist kosong.")

    text = "**Playlist saat ini:**\n\n"
    for i, song in enumerate(playlist[chat_id], start=1):
        text += f"{i}. {os.path.basename(song)}\n"

    await message.reply(text)


# ------------------ Start Bot ------------------
app.start()
call.start()
print("Bot music berjalan...")
app.idle()
=
import telebot
import os
from telebot import types
from moviepy import VideoFileClip
import uuid
import shutil
from dotenv import load_dotenv

from downloaders import (
    download_instagram_video,
    is_instagram_url,
    download_youtube_video,
    is_youtube_url,
    download_pinterest_video,
    is_pinterest_url,
    download_tiktok_video,
    is_tiktok_url,
    get_ffmpeg_path,
)

# Set up ffmpeg environment
os.environ["IMAGEIO_FFMPEG_EXE"] = get_ffmpeg_path()

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing. Set it in your .env file.")

bot = telebot.TeleBot(BOT_TOKEN)

# Global state for video and folder tracking
video_file = None
folder_name = None


def send_video_with_audio_button(chat_id, video_path):
    """Send video to user with a download audio button."""
    with open(video_path, "rb") as video:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Download audio", callback_data="get_audio")
        markup.add(btn1)
        bot.send_video(chat_id, video, reply_markup=markup)


def safe_edit_status(chat_id, message_id, text):
    try:
        bot.edit_message_text(text, chat_id, message_id)
    except Exception:
        # Ignore edit failures (same text, old message, temporary Telegram issues)
        pass


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hello! Send me a video link from YouTube, Instagram, TikTok, or Pinterest, and I'll download it for you. You can also download the audio separately!")


@bot.message_handler(func=lambda message: True)
def handle_video_request(message):
    """Handle video download requests for all supported platforms."""
    global video_file, folder_name
    url = message.text.strip()

    video_file = None
    folder_name = None

    # YouTube
    if is_youtube_url(url):
        folder_name = f"yt_{uuid.uuid4()}"
        loader_message = bot.send_message(message.chat.id, "Downloading YouTube video...")
        _download_and_send(message, loader_message, download_youtube_video, url, folder_name)
        return

    # Pinterest
    if is_pinterest_url(url):
        folder_name = f"pin_{uuid.uuid4()}"
        loader_message = bot.send_message(message.chat.id, "Downloading Pinterest video...")
        _download_and_send(message, loader_message, download_pinterest_video, url, folder_name)
        return

    # TikTok
    if is_tiktok_url(url):
        folder_name = f"tt_{uuid.uuid4()}"
        loader_message = bot.send_message(message.chat.id, "Downloading TikTok video...")
        _download_and_send(message, loader_message, download_tiktok_video, url, folder_name)
        return

    # Instagram
    if is_instagram_url(url):
        try:
            shortcode = url.split("/")[-2]
            folder_name = shortcode
        except IndexError:
            bot.reply_to(message, "Invalid link")
            return

        loader_message = bot.send_message(message.chat.id, "Downloading Instagram video...")
        _download_and_send(message, loader_message, download_instagram_video, url, folder_name)
        return

    # Unknown platform
    bot.reply_to(message, "Invalid link")


def _download_and_send(message, loader_message, downloader_func, url, download_path):
    """Helper function to download and send video."""
    global video_file, folder_name

    last_status_text = {"value": None}

    def progress_callback(percent, status):
        if percent is None:
            status_text = status
        else:
            status_text = f"{status} {int(percent)}%"

        if status_text != last_status_text["value"]:
            safe_edit_status(message.chat.id, loader_message.message_id, status_text)
            last_status_text["value"] = status_text

    try:
        video_file = downloader_func(url, download_path, progress_callback=progress_callback)

        if video_file:
            safe_edit_status(message.chat.id, loader_message.message_id, "Uploading video...")
            send_video_with_audio_button(message.chat.id, video_file)
            bot.delete_message(message.chat.id, loader_message.message_id)
        else:
            bot.delete_message(message.chat.id, loader_message.message_id)
            bot.reply_to(message, "Video not found")

    except Exception as e:
        bot.delete_message(message.chat.id, loader_message.message_id)
        bot.reply_to(message, f"Error: {e}")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global video_file, folder_name
    if call.data == "get_audio":
        try:
            bot.send_message(call.message.chat.id, "Downloading audio...")

            video = VideoFileClip(video_file)
            audio = video.audio
            audio_name = f"{uuid.uuid4()}.mp3"
            audio.write_audiofile(audio_name)
            video.close()

            with open(audio_name, "rb") as audio_:
                bot.send_audio(call.message.chat.id, audio_)
            os.remove(audio_name)

        except Exception as e:
            bot.reply_to(call.message, f"Error downloading audio: {e}")
        finally:
            if os.path.exists(folder_name):
                shutil.rmtree(folder_name, ignore_errors=True)


bot.infinity_polling()

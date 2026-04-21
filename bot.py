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
#     download_pinterest_video,
#     is_pinterest_url,
#     download_tiktok_video,
#     is_tiktok_url,
    get_ffmpeg_path,
)

# Set up ffmpeg environment
os.environ["IMAGEIO_FFMPEG_EXE"] = get_ffmpeg_path()

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing. Set it in your .env file.")

bot = telebot.TeleBot(BOT_TOKEN)


# Store one pending request per user until they choose audio or video.
pending_requests = {}


def send_video(chat_id, video_path):
    with open(video_path, "rb") as video:
        bot.send_video(chat_id, video)


def send_audio(chat_id, video_path):
    audio_name = f"{uuid.uuid4()}.mp3"
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_name)
    video.close()

    try:
        with open(audio_name, "rb") as audio_file:
            bot.send_audio(chat_id, audio_file)
    finally:
        if os.path.exists(audio_name):
            os.remove(audio_name)


def get_download_config(url):
    if is_youtube_url(url):
        return download_youtube_video, f"yt_{uuid.uuid4()}", "YouTube"

#     if is_pinterest_url(url):
#         return download_pinterest_video, f"pin_{uuid.uuid4()}", "Pinterest"

#     if is_tiktok_url(url):
#         return download_tiktok_video, f"tt_{uuid.uuid4()}", "TikTok"

    if is_instagram_url(url):
        try:
            shortcode = url.split("/")[-2]
            if not shortcode:
                return None
            return download_instagram_video, shortcode, "Instagram"
        except IndexError:
            return None

    return None


def safe_edit_status(chat_id, message_id, text):
    try:
        bot.edit_message_text(text, chat_id, message_id)
    except Exception:
        # Ignore edit failures (same text, old message, temporary Telegram issues)
        pass


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Hello! Send me a video link from YouTube, Instagram, TikTok, or Pinterest. "
        "I will ask whether you want video or audio."
    )


@bot.message_handler(func=lambda message: True)
def handle_video_request(message):
    """Handle incoming links and ask user for desired output format."""
    url = message.text.strip()

    config = get_download_config(url)
    if not config:
        bot.reply_to(message, "Invalid link")
        return

    downloader_func, download_path, platform_name = config
    pending_requests[message.from_user.id] = {
        "url": url,
        "downloader": downloader_func,
        "download_path": download_path,
        "platform": platform_name,
    }

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Video", callback_data="choose_video"),
        types.InlineKeyboardButton("Audio", callback_data="choose_audio")
    )
    bot.send_message(
        message.chat.id,
        f"{platform_name} link detected. Choose what you want to download:",
        reply_markup=markup,
    )

def _download_and_send(call, output_type):
    request = pending_requests.pop(call.from_user.id, None)
    if not request:
        bot.send_message(call.message.chat.id, "Request expired. Please send the link again.")
        return

    downloader_func = request["downloader"]
    url = request["url"]
    download_path = request["download_path"]
    platform_name = request["platform"]

    loader_message = bot.send_message(
        call.message.chat.id,
        f"Downloading {platform_name} {output_type}..."
    )

    last_status_text = {"value": None}

    def progress_callback(percent, status):
        if percent is None:
            status_text = status
        else:
            status_text = f"{status} {int(percent)}%"

        if status_text != last_status_text["value"]:
            safe_edit_status(call.message.chat.id, loader_message.message_id, status_text)
            last_status_text["value"] = status_text

    downloaded_video_path = None
    try:
        downloaded_video_path = downloader_func(url, download_path, progress_callback=progress_callback)

        if downloaded_video_path:
            if output_type == "video":
                safe_edit_status(call.message.chat.id, loader_message.message_id, "Uploading video...")
                send_video(call.message.chat.id, downloaded_video_path)
            else:
                safe_edit_status(call.message.chat.id, loader_message.message_id, "Converting to audio...")
                send_audio(call.message.chat.id, downloaded_video_path)

            bot.delete_message(call.message.chat.id, loader_message.message_id)
        else:
            bot.delete_message(call.message.chat.id, loader_message.message_id)
            bot.send_message(call.message.chat.id, "Video not found")

    except Exception as e:
        bot.delete_message(call.message.chat.id, loader_message.message_id)
        bot.send_message(call.message.chat.id, f"Error: {e}")
    finally:
        if os.path.exists(download_path):
            shutil.rmtree(download_path, ignore_errors=True)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.answer_callback_query(call.id)

    if call.data == "choose_video":
        _download_and_send(call, "video")
    elif call.data == "choose_audio":
        _download_and_send(call, "audio")


bot.infinity_polling()

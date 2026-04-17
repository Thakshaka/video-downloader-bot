from urllib.parse import urlparse
import os
import yt_dlp
from .common import find_video_file, get_ffmpeg_path, get_js_runtime_config


def is_pinterest_url(url):
    """Check if URL is a Pinterest link."""
    parsed_url = urlparse(url)
    hostname = parsed_url.netloc.lower()
    return "pinterest.com" in hostname or hostname == "pin.it"


def _build_progress_hook(progress_callback):
    def hook(data):
        if not progress_callback:
            return

        status = data.get("status")
        if status == "downloading":
            total_bytes = data.get("total_bytes") or data.get("total_bytes_estimate")
            downloaded_bytes = data.get("downloaded_bytes", 0)
            percent = (downloaded_bytes / total_bytes) * 100 if total_bytes else None
            progress_callback(percent, "Downloading Pinterest video...")
        elif status == "finished":
            progress_callback(100, "Processing Pinterest video...")

    return hook


def download_pinterest_video(url, download_path, progress_callback=None):
    """Download video from Pinterest using yt-dlp."""
    os.makedirs(download_path, exist_ok=True)
    
    js_runtimes = get_js_runtime_config()
    ffmpeg_path = get_ffmpeg_path()
    
    ydl_options = {
        "outtmpl": os.path.join(download_path, "%(id)s.%(ext)s"),
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "ffmpeg_location": ffmpeg_path,
        "noplaylist": True,
        "quiet": True,
        "progress_hooks": [_build_progress_hook(progress_callback)],
    }

    if js_runtimes:
        ydl_options["js_runtimes"] = js_runtimes

    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        ydl.extract_info(url, download=True)

    return find_video_file(download_path)

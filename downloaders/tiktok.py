from urllib.parse import urlparse
import os
import yt_dlp
from .common import find_video_file, get_ffmpeg_path, get_js_runtime_config


class TikTokYDLLogger:
	"""Filter non-fatal impersonation warnings that are noisy in some environments."""

	@staticmethod
	def debug(msg):
		return

	@staticmethod
	def warning(msg):
		if "attempting impersonation, but no impersonate target is available" in msg:
			return
		print(msg)

	@staticmethod
	def error(msg):
		print(msg)


def is_tiktok_url(url):
	"""Check if URL is a TikTok link."""
	parsed_url = urlparse(url)
	hostname = parsed_url.netloc.lower()
	return "tiktok.com" in hostname or hostname == "vm.tiktok.com" or hostname == "vt.tiktok.com"


def _build_progress_hook(progress_callback):
	def hook(data):
		if not progress_callback:
			return

		status = data.get("status")
		if status == "downloading":
			total_bytes = data.get("total_bytes") or data.get("total_bytes_estimate")
			downloaded_bytes = data.get("downloaded_bytes", 0)
			percent = (downloaded_bytes / total_bytes) * 100 if total_bytes else None
			progress_callback(percent, "Downloading TikTok video...")
		elif status == "finished":
			progress_callback(100, "Processing TikTok video...")

	return hook


def download_tiktok_video(url, download_path, progress_callback=None):
	"""Download video from TikTok using yt-dlp."""
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
		"logger": TikTokYDLLogger(),
		"progress_hooks": [_build_progress_hook(progress_callback)],
	}

	if js_runtimes:
		ydl_options["js_runtimes"] = js_runtimes

	with yt_dlp.YoutubeDL(ydl_options) as ydl:
		ydl.extract_info(url, download=True)

	return find_video_file(download_path)

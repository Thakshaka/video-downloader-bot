import os
import shutil
import imageio_ffmpeg


def get_ffmpeg_path():
	"""Get the path to the bundled ffmpeg executable from imageio-ffmpeg."""
	return imageio_ffmpeg.get_ffmpeg_exe()


def find_video_file(download_path):
	"""Find the first video file in the download directory."""
	for file_name in os.listdir(download_path):
		if file_name.lower().endswith((".mp4", ".mkv", ".webm", ".mov", ".m4v")):
			return os.path.join(download_path, file_name)
	return None


def get_js_runtime_config():
	"""Get the JavaScript runtime configuration for yt-dlp."""
	node_path = shutil.which("node")
	return {"node": {"path": node_path}} if node_path else None

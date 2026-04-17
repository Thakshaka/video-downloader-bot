from urllib.parse import urlparse
import instaloader
import os
from .common import find_video_file

# Initialize Instagram loader with minimal options
loader = instaloader.Instaloader(
    download_comments=False,
    download_geotags=False,
    download_pictures=False,
    download_video_thumbnails=False,
    save_metadata=False
)


def is_instagram_url(url):
    """Check if URL is an Instagram link."""
    parsed_url = urlparse(url)
    return "instagram.com" in parsed_url.netloc.lower()


def download_instagram_video(url, download_path, progress_callback=None):
    """Download video from Instagram using instaloader."""
    os.makedirs(download_path, exist_ok=True)

    try:
        if progress_callback:
            progress_callback(10, "Preparing Instagram download...")

        shortcode = url.split("/")[-2]
        if progress_callback:
            progress_callback(30, "Fetching Instagram post...")

        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target=download_path)
        if progress_callback:
            progress_callback(90, "Finalizing Instagram video...")

        return find_video_file(download_path)
    except Exception as e:
        raise Exception(f"Instagram download failed: {e}")

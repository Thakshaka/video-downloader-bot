# Video Downloader Bot

A Telegram bot that downloads videos from multiple social media platforms and can extract audio from them.

## Supported Platforms

- **Instagram** - Downloads videos from Instagram posts
- **YouTube** - Downloads videos from YouTube (shorts and full videos)
- **Pinterest** - Downloads videos from Pinterest pins
- **TikTok** - Downloads videos from TikTok

## Project Structure

```
Video Downloader Bot/
├── bot.py                    # Main bot entry point with Telegram handlers
├── requirements.txt          # Python dependencies
├── downloaders/              # Modular downloader package
│   ├── __init__.py          # Package initialization with public exports
│   ├── common.py            # Shared utilities (ffmpeg, file finding)
│   ├── instagram.py         # Instagram downloader (uses instaloader)
│   ├── youtube.py           # YouTube downloader (uses yt-dlp)
│   ├── pinterest.py         # Pinterest downloader (uses yt-dlp)
│   └── tiktok.py            # TikTok downloader (uses yt-dlp)
└── venv/                     # Python virtual environment
```

## Module Descriptions

### bot.py
Main entry point that initializes the Telegram bot and handles:
- `/start` command
- URL detection and routing to appropriate downloader
- Video sending with audio extraction button
- Audio extraction from downloaded videos

### downloaders/common.py
Shared utilities:
- `get_ffmpeg_path()` - Returns path to bundled ffmpeg executable
- `find_video_file()` - Locates downloaded video file
- `get_js_runtime_config()` - Configures Node.js runtime for yt-dlp

### downloaders/instagram.py
Instagram-specific logic:
- `is_instagram_url()` - Detects Instagram links
- `download_instagram_video()` - Downloads using instaloader

### downloaders/youtube.py
YouTube-specific logic:
- `is_youtube_url()` - Detects YouTube links (youtube.com, youtu.be)
- `download_youtube_video()` - Downloads using yt-dlp with JS challenge solver

### downloaders/pinterest.py
Pinterest-specific logic:
- `is_pinterest_url()` - Detects Pinterest links (pinterest.com, pin.it)
- `download_pinterest_video()` - Downloads using yt-dlp

### downloaders/tiktok.py
TikTok-specific logic:
- `is_tiktok_url()` - Detects TikTok links (tiktok.com, vm.tiktok.com, vt.tiktok.com)
- `download_tiktok_video()` - Downloads using yt-dlp with browser impersonation

## Dependencies

See `requirements.txt`:
- `pyTelegramBotAPI` - Telegram bot framework
- `instaloader` - Instagram downloader
- `yt-dlp` - Universal video downloader
- `moviepy` - Audio extraction from videos
- `imageio-ffmpeg` - Bundled ffmpeg for video processing

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your Telegram bot token in `bot.py` (currently hardcoded)

3. Run the bot:
   ```bash
   python bot.py
   ```

4. In Telegram, use the bot by sending video URLs from supported platforms

## Features

- **Multi-platform support** - Handles Instagram, YouTube, Pinterest, and TikTok
- **Audio extraction** - Extract audio from downloaded videos
- **Browser impersonation** - TikTok support with browser impersonation
- **JS challenge solving** - YouTube support with automated JS challenge resolution
- **Clean modular architecture** - Each platform has its own module

## Future Enhancements

- Add support for more platforms (Twitter, Reddit, etc.)
- Environment-based token configuration
- Logging system
- Video size limitations and optimization
- User authentication and rate limiting

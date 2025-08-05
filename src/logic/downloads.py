import typing, logging
from logging import Logger
from pathlib import Path
import yt_dlp


def download_yt_audio(logger: Logger, url: str, output_path: Path) -> None:
    if output_path.exists():
        logger.error(f"Output path already exists {output_path}")
        raise Exception("Output path already exists {output_path}")

    logger.debug(f"Starting download for: {url}")

    # Ensure output folder exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    disabled_yt_logger = logging.getLogger("ytmusicapi")
    disabled_yt_logger.disabled = True
    ydl_opts: dict[str, typing.Any] = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": str(output_path.with_suffix("")),
        "quiet": False,
        "no_warnings": False,
        "logger": disabled_yt_logger,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # @TODO: review it, make path be exactly
            info_dict = ydl.extract_info(url, download=True)
            downloaded_file = (
                ydl.prepare_filename(info_dict)
                .replace(".webm", output_path.suffix)
                .replace(".m4a", output_path.suffix)
            )
            logger.debug(f"\nSuccessfully downloaded: {downloaded_file}")
            return
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        return

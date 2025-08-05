from pathlib import Path
from logging import Logger
from mutagen.mp3 import MP3
from mutagen.id3 import (
    ID3,
    TIT2,  # type: ignore
    TPE1,  # type: ignore
    TALB,  # type: ignore
    TDRC,  # type: ignore
    TRCK,  # type: ignore
    TCON,  # type: ignore
    TCOM,  # type: ignore
    COMM,  # type: ignore
    USLT,  # type: ignore
    TPE2,  # type: ignore
)


def update_mp3_tags(logger: Logger, file_path: Path, tags: dict[str, str]):
    """
    Updates the ID3 tags of an MP3 file.

    Args:
        logger (Logger): The logger to use for logging.
        file_path (Path): The path to the MP3 file.
        tags (dict[str, str]): A dictionary of tags to update.
            Supported tags: title, artist, album, album_artist, year, track_number, genre, composer, comment, lyrics.
    """
    try:
        # Load the MP3 file with ID3 tags
        audio = MP3(file_path, ID3=ID3)

        # Initialize ID3 tag if it doesn't exist
        if not audio.tags:
            audio.add_tags()

        audio_tags: ID3 = audio.tags  # type: ignore

        # Standard tags
        if "title" in tags:
            audio_tags.add(TIT2(encoding=3, text=tags["title"]))
        if "artist" in tags:
            audio_tags.add(TPE1(encoding=3, text=tags["artist"]))
        if "album" in tags:
            audio_tags.add(TALB(encoding=3, text=tags["album"]))
        if "album_artist" in tags:
            audio_tags.add(TPE2(encoding=3, text=tags["album_artist"]))
        if "year" in tags:
            audio_tags.add(TDRC(encoding=3, text=str(tags["year"])))
        if "track_number" in tags:
            audio_tags.add(TRCK(encoding=3, text=str(tags["track_number"])))
        if "genre" in tags:
            audio_tags.add(TCON(encoding=3, text=tags["genre"]))
        if "composer" in tags:
            audio_tags.add(TCOM(encoding=3, text=tags["composer"]))
        if "comment" in tags:
            audio_tags.add(COMM(encoding=3, lang="eng", desc="", text=tags["comment"]))
        if "lyrics" in tags:
            audio_tags.add(USLT(encoding=3, lang="eng", desc="", text=tags["lyrics"]))

        # Save changes
        audio.save(v2_version=3)  # Save as ID3v2.3 for maximum compatibility
        logger.debug(f"Successfully updated tags for {file_path}")

    except Exception as e:
        logger.error(f"Error updating {file_path}: {str(e)}")

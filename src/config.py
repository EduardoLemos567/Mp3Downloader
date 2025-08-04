import typing
from pathlib import Path
from constants import AppMeta


class Config:
    # Define the configuration for the application.
    # Where to save the downloaded files.
    DOWNLOAD_FOLDER: typing.Final[str] = "./downloads"
    # Temporary folder for processing files.
    TEMP_FOLDER: typing.Final[str] = "./temp"
    LOG_FILE: typing.Final[str] = f"{AppMeta.NAME}.log"
    LOG_FILE_PATH: typing.Final[Path] = Path(TEMP_FOLDER, LOG_FILE)
    # Temporary files
    # Save which files were downloaded from which links.
    CONTROL_FILE: typing.Final[str] = "control.json"
    CONTROL_FILE_PATH: typing.Final[Path] = Path(TEMP_FOLDER, CONTROL_FILE)
    # Save links extracted from the playlist.html
    PLAYLIST_JSON: typing.Final[str] = "playlist.json"
    PLAYLIST_JSON_PATH: typing.Final[Path] = Path(TEMP_FOLDER, PLAYLIST_JSON)

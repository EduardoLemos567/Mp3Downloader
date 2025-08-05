import typing, json
from pathlib import Path
from logging import Logger
from ytmusicapi import YTMusic
from data.mp3 import Mp3


def scrap_playlist(
    playlist_id: str, logger: Logger | None, playlist_path: Path
) -> typing.List[Mp3]:
    """
    Scrapes a YouTube Music playlist to extract song information.

    It first checks if the playlist data is already cached locally. If not, or if the
    playlist ID has changed, it fetches the data from YouTube Music and caches it.

    Args:
        playlist_id (str): The ID of the YouTube Music playlist.
        logger (Logger | None): The logger to use for logging.
        playlist_path (Path): The path to the cached playlist data.

    Returns:
        typing.List[Mp3]: A list of Mp3 objects representing the songs in the playlist.
    """
    need_download = True
    js = {}
    if playlist_path.exists():
        try:
            with playlist_path.open("r", encoding="utf-8") as f:
                js = json.load(f)
                if js["id"] == playlist_id:
                    need_download = False
        except:
            playlist_path.unlink(missing_ok=True)
            need_download = True
    if need_download:
        ytmusic = YTMusic()
        js = ytmusic.get_playlist(playlist_id)
        with playlist_path.open("w", encoding="utf-8") as f:
            json.dump(js, f, indent=2)
    mp3s = []
    if "tracks" not in js:
        return mp3s
    for item in js["tracks"]:
        mp3 = Mp3(item["videoId"], item["title"])
        mp3.artist = item["artists"][0]["name"]
        if item["album"] is not None:
            mp3.album = item["album"]["name"]
        mp3s.append(mp3)
    return mp3s

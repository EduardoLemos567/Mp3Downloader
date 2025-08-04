from enum import Enum
from pathlib import Path


class Mp3:
    class State(Enum):
        CREATED = 0
        DOWNLOADED = 1
        DONE = 2

    def __init__(self, url_id: str, title: str):
        self.url_id: str = url_id
        self.title: str = title
        self.artist: str = ""
        self.album: str | None = None
        self.file_path: Path | None = None
        self.state: Mp3.State = Mp3.State.CREATED

    def __str__(self) -> str:
        return f"Mp3(url_id={self.url_id}, file_path={self.file_path}, artist={self.artist}, title={self.title}, album={self.album}, state={self.state})"

    __repr__ = __str__

    def to_json(self) -> dict[str, str]:
        return {
            "url_id": self.url_id,
            "file_path": str(self.file_path) if self.file_path is not None else "",
            "artist": self.artist,
            "title": self.title,
            "album": str(self.album) if self.album is not None else "",
            "state": self.state.name,
        }

    @staticmethod
    def from_json(data: dict[str, str]) -> Mp3:
        mp3 = Mp3(data["url_id"], data["title"])
        file_path = data.get("file_path", "")
        mp3.file_path = Path(file_path) if len(file_path) > 0 else None
        mp3.artist = data.get("artist", "")
        mp3.album = data.get("album", None)
        mp3.state = Mp3.State[data.get("state", Mp3.State.CREATED.name)]
        return mp3

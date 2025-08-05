from enum import Enum
from pathlib import Path


class Mp3:
    """
    Represents an MP3 file, containing its metadata and state.
    """

    class State(Enum):
        """
        Represents the state of the MP3 file in the download process.
        """

        CREATED = 0
        DOWNLOADED = 1
        DONE = 2

    def __init__(self, url_id: str, title: str):
        """
        Initializes the Mp3 object.

        Args:
            url_id (str): The YouTube video ID.
            title (str): The title of the song.
        """
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
        """
        Converts the Mp3 object to a JSON serializable dictionary.

        Returns:
            dict[str, str]: The JSON representation of the Mp3 object.
        """
        return {
            "url_id": self.url_id,
            "file_path": str(self.file_path) if self.file_path is not None else "",
            "artist": self.artist,
            "title": self.title,
            "album": str(self.album) if self.album is not None else "",
            "state": self.state.name,
        }

    @staticmethod
    def from_json(data: dict[str, str]) -> "Mp3":
        """
        Creates an Mp3 object from a JSON dictionary.

        Args:
            data (dict[str, str]): The JSON dictionary.

        Returns:
            Mp3: The created Mp3 object.
        """
        mp3 = Mp3(data["url_id"], data["title"])
        file_path = data.get("file_path", "")
        mp3.file_path = Path(file_path) if len(file_path) > 0 else None
        mp3.artist = data.get("artist", "")
        mp3.album = data.get("album", None)
        mp3.state = Mp3.State[data.get("state", Mp3.State.CREATED.name)]
        return mp3

import typing
from pathlib import Path
from data.mp3 import Mp3


class State:
    """
    Represents the application state.

    This class holds all the data that needs to be persisted between application runs,
    such as the list of MP3 files, their states.
    """

    def __init__(self):
        """
        Initializes the State object.
        """
        self.playlist_url_id: str = ""
        self.mp3s: list[Mp3] = []
        self.by_urls: dict[str, Mp3] = {}
        self.by_file_paths: dict[Path, Mp3] = {}

    def add(self, mp3: Mp3) -> None:
        """
        Adds an Mp3 object to the state.

        Args:
            mp3 (Mp3): The Mp3 object to add.
        """
        self.mp3s.append(mp3)
        self.by_urls[mp3.url_id] = mp3
        if mp3.state in (Mp3.State.DOWNLOADED, Mp3.State.DONE):
            assert mp3.file_path is not None
            path: Path = mp3.file_path
            self.by_file_paths[path] = mp3

    def remove(self, mp3: Mp3) -> None:
        """
        Removes an Mp3 object from the state.

        Args:
            mp3 (Mp3): The Mp3 object to remove.
        """
        for index, item in enumerate(self.mp3s):
            if item.url_id == mp3.url_id:
                del self.mp3s[index]
                break

        self.by_urls.pop(mp3.url_id, None)

        if mp3.state in (Mp3.State.DOWNLOADED, Mp3.State.DONE):
            assert mp3.file_path is not None
            self.by_file_paths.pop(mp3.file_path, None)

    def to_json(self) -> dict[str, typing.Any]:
        """
        Converts the State object to a JSON serializable dictionary.

        Returns:
            dict[str, typing.Any]: The JSON representation of the State object.
        """
        return {
            "playlist_url": self.playlist_url_id,
            "mp3s": [mp3.to_json() for mp3 in self.mp3s],
        }

    @staticmethod
    def from_json(json_data: dict[str, typing.Any]) -> "State":
        """
        Creates a State object from a JSON dictionary.

        Args:
            json_data (dict[str, typing.Any]): The JSON dictionary.

        Returns:
            State: The created State object.
        """
        state = State()
        state.playlist_url_id = json_data.get("playlist_url", "")
        mp3s_json_data = json_data.get("mp3s", [])
        for mp3_json_data in mp3s_json_data:
            mp3 = Mp3.from_json(mp3_json_data)
            state.add(mp3)
        return state

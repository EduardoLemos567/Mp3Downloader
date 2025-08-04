from collections import deque
import typing
from pathlib import Path
from data.mp3 import Mp3


class State:
    def __init__(self):
        self.playlist_url_id: str = ""
        self.mp3s: list[Mp3] = []
        self.urls: dict[str, Mp3] = {}
        self.paths: dict[Path, Mp3] = {}
        self.work_queue: deque[Mp3] = deque()

    def add(self, mp3: Mp3) -> None:
        self.mp3s.append(mp3)
        self.urls[mp3.url_id] = mp3
        if mp3.state in (Mp3.State.DOWNLOADED, Mp3.State.DONE):
            assert mp3.file_path is not None
            path: Path = mp3.file_path
            self.paths[path] = mp3
        if mp3.state is not Mp3.State.DONE:
            self.work_queue.append(mp3)

    def remove(self, mp3: Mp3) -> None:
        for index, item in enumerate(self.mp3s):
            if item.url_id == mp3.url_id:
                del self.mp3s[index]
                break

        self.urls.pop(mp3.url_id, None)

        if mp3.state in (Mp3.State.DOWNLOADED, Mp3.State.DONE):
            assert mp3.file_path is not None
            self.paths.pop(mp3.file_path, None)

        if mp3.state is not Mp3.State.DONE:
            self.work_queue.remove(mp3)

    def to_json(self) -> dict[str, typing.Any]:
        return {
            "playlist_url": self.playlist_url_id,
            "mp3s": [mp3.to_json() for mp3 in self.mp3s],
        }

    @staticmethod
    def from_json(json_data: dict[str, typing.Any]) -> State:
        state = State()
        state.playlist_url_id = json_data.get("playlist_url", "")
        mp3s_json_data = json_data.get("mp3s", [])
        for mp3_json_data in mp3s_json_data:
            mp3 = Mp3.from_json(mp3_json_data)
            state.add(mp3)
        return state

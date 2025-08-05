import sys, logging, utils
from pathlib import Path
from logic import update_tags
from data.state import State
from data.mp3 import Mp3
import logic.playlist as playlist
import logic.downloads as downloads
import logic.update_tags as update_tags
import logic.progress_bar as progress_bar
from constants import AppMeta
from config import Config


class App:
    def __init__(
        self,
        playlist_url: str,
        console_log_level: int = logging.INFO,
        file_log_level: int = logging.WARNING,
    ):
        self._setup_logger(console_log_level, file_log_level)
        self.progress_bar = progress_bar.ProgressBar(total=1000)
        self._setup_state()
        playlist_url_id = utils.grab_id_from_url(playlist_url)
        # Check if id change from previous run and remove json file to redownload.
        if playlist_url_id != self.state.playlist_url_id:
            self.state.playlist_url_id = playlist_url_id
            Config.PLAYLIST_JSON_PATH.unlink(missing_ok=True)
        self._remove_missing_files()

    def _setup_logger(self, console_log_level, file_log_level):
        try:
            self.logger = utils.setup_logger(
                AppMeta.NAME, Config.LOG_FILE_PATH, file_log_level, console_log_level
            )
        except Exception as e:
            print(f"Failed to set up logger: '{e}'. Exiting.")
            self._quit(1)

    def _setup_state(self):
        if Config.CONTROL_FILE_PATH.exists():
            try:
                self.state = self._load_state()
                self.logger.debug(f"Loaded state from '{Config.CONTROL_FILE_PATH}'")
            except Exception as e:
                self.logger.error(
                    f"Failed to load state from '{Config.CONTROL_FILE_PATH}': '{e}'. Exiting."
                )
                self._quit(1)
        else:
            self.state = State()

    def _remove_missing_files(self):
        # Remove Mp3 that were DOWNLOADED, if they are missing.
        i = len(self.state.mp3s)
        while i > 0:
            i -= 1
            mp3 = self.state.mp3s[i]
            if mp3.state in (Mp3.State.DOWNLOADED, Mp3.State.DONE):
                print(mp3)
                assert mp3.file_path is not None
                if not mp3.file_path.exists():
                    self.state.remove(mp3)
                    self.logger.debug(
                        f"Removed control entry for missing file '{mp3.file_path.name}'"
                    )

    def run(self):
        try:
            self.progress_bar.update(0, prefix="Extracting playlist")
            self.logger.debug(
                f"Starting application with playlist URL: {self.state.playlist_url_id}"
            )
            self._extract_playlist()

            if len(self.state.work_queue) > 0:
                self.progress_bar.update(100, prefix="Downloading files")
                self._process_files()

                self.logger.debug("All files processed successfully.")
            else:
                self.logger.debug("No files to process.")

            self.progress_bar.done("Done")

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            self._quit(1)

        self._quit(0)

    @staticmethod
    def _load_state() -> State:
        json_data = utils.read_json_file(Config.CONTROL_FILE_PATH)
        return State.from_json(json_data)

    def _save_state(self, state: State) -> None:
        utils.write_json_file(Config.CONTROL_FILE_PATH, state.to_json())
        self.logger.debug(f"State saved to {Config.CONTROL_FILE_PATH}")

    def _quit(self, exit_code: int = 0) -> None:
        if hasattr(self, "state"):
            self._save_state(self.state)
            self.logger.debug("Application is exiting, state saved.")
        else:
            self.logger.debug("Application is exiting, no state found, not saving.")

        if exit_code == 0:
            self.logger.debug(f"Exiting application with code {exit_code}.")
        else:
            self.logger.warning(f"Exiting application with code {exit_code}.")
        sys.exit(exit_code)

    def _extract_playlist(self) -> None:
        mp3s = playlist.scrap_playlist(
            self.state.playlist_url_id, self.logger, Config.PLAYLIST_JSON_PATH
        )
        total = 0
        for mp3 in mp3s:
            if mp3.url_id in self.state.urls:
                continue
            self.state.add(mp3)
            total += 1
        self.logger.debug(f"Found {total} new files to download.")

    def _process_files(self) -> None:
        progress_left = 900
        increment = progress_left / len(self.state.work_queue)
        actual = 0
        total = len(self.state.work_queue)
        self.progress_bar.update(0, prefix=f"Processing {actual}/{total} files")
        while len(self.state.work_queue) > 0:
            mp3 = self.state.work_queue[0]
            match mp3.state:
                case Mp3.State.CREATED:
                    self._download_file(mp3)
                case Mp3.State.DOWNLOADED:
                    self._update_tags(mp3)
                case Mp3.State.DONE:
                    self.state.work_queue.popleft()
                    actual += 1
                    self.progress_bar.update(
                        increment, prefix=f"Processing {actual}/{total} files"
                    )

    def _download_file(self, mp3):
        file_name = Path(
            Config.FILE_NAME_TEMPLATE.format(
                artist=mp3.artist,
                title=mp3.title,
                album=mp3.album if mp3.album is not None else "",
            )
            + ".mp3"
        )
        file_name = utils.fix_file_name(file_name)
        mp3.file_path = Config.DOWNLOAD_FOLDER_PATH / file_name

        downloads.download_yt_audio(self.logger, mp3.url_id, mp3.file_path)
        mp3.state = Mp3.State.DOWNLOADED

    def _update_tags(self, mp3):
        tags = {"artist": mp3.artist, "title": mp3.title}
        if mp3.album is not None:
            tags["album"] = mp3.album
        update_tags.update_mp3_tags(self.logger, mp3.file_path, tags)  # type: ignore
        mp3.state = Mp3.State.DONE

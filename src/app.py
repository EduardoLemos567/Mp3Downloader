import sys, logging, utils
from collections import deque
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
    """
    Main application class for Mp3Downloader.

    This class orchestrates the entire process of downloading MP3 files from a YouTube playlist.
    It handles state management, logging, playlist extraction, file downloading, and tag updates.
    """

    def __init__(
        self,
        playlist_url: str,
        console_log_level: int = logging.INFO,
        file_log_level: int = logging.WARNING,
    ):
        """
        Initializes the application.

        Args:
            playlist_url (str): The URL of the YouTube playlist to download.
            console_log_level (int): The logging level for console output.
            file_log_level (int): The logging level for file output.
        """
        self._setup_logger(console_log_level, file_log_level)
        self._progress_bar = progress_bar.ProgressBar(total=1000)
        self._setup_state()
        playlist_url_id = utils.grab_id_from_url(playlist_url)
        # Check if id change from previous run and remove json file to redownload.
        if playlist_url_id != self._state.playlist_url_id:
            self._state.playlist_url_id = playlist_url_id
            Config.PLAYLIST_JSON_PATH.unlink(missing_ok=True)
        self._remove_missing_files()
        self._process_queue: deque[Mp3] = deque()

    def _setup_logger(self, console_log_level, file_log_level):
        """
        Sets up the logger for the application.

        Args:
            console_log_level (int): The logging level for the console.
            file_log_level (int): The logging level for the log file.
        """
        try:
            self._logger = utils.setup_logger(
                AppMeta.NAME, Config.LOG_FILE_PATH, file_log_level, console_log_level
            )
        except Exception as e:
            print(f"Failed to set up logger: '{e}'. Exiting.")
            self._quit(1)

    def _setup_state(self):
        """
        Loads the application state from the control file, or creates a new state if not found.
        """
        if Config.CONTROL_FILE_PATH.exists():
            try:
                self._state = self._load_state()
                self._logger.debug(f"Loaded state from '{Config.CONTROL_FILE_PATH}'")
                # add pending work to the queue
                for mp3 in self._state.mp3s:
                    if mp3.state is not Mp3.State.DONE:
                        self._process_queue.append(mp3)
            except Exception as e:
                self._logger.error(
                    f"Failed to load state from '{Config.CONTROL_FILE_PATH}': '{e}'. Exiting."
                )
                self._quit(1)
        else:
            self._state = State()

    def _remove_missing_files(self):
        """
        Removes entries for downloaded files that are no longer present in the filesystem.
        """
        i = len(self._state.mp3s)
        while i > 0:
            i -= 1
            mp3 = self._state.mp3s[i]
            if mp3.state in (Mp3.State.DOWNLOADED, Mp3.State.DONE):
                assert mp3.file_path is not None
                if not mp3.file_path.exists():
                    self._state.remove(mp3)
                    self._logger.debug(
                        f"Removed control entry for missing file '{mp3.file_path.name}'"
                    )

    def run(self):
        """
        Runs the main application logic.
        """
        try:
            self._progress_bar.update(0, prefix="Extracting playlist")
            self._logger.debug(
                f"Starting application with playlist URL: {self._state.playlist_url_id}"
            )
            self._extract_playlist()

            if len(self._process_queue) > 0:
                self._progress_bar.update(100, prefix="Downloading files")
                self._process_files()

                self._logger.debug("All files processed successfully.")
            else:
                self._logger.debug("No files to process.")

            self._progress_bar.done("Done")

        except Exception as e:
            self._logger.error(f"An error occurred: {e}")
            self._quit(1)

        self._quit(0)

    def _load_state(self) -> State:
        """
        Loads the application state from the control file.

        Returns:
            State: The application state.
        """
        json_data = utils.read_json_file(Config.CONTROL_FILE_PATH)
        return State.from_json(json_data)

    def _save_state(self, state: State) -> None:
        """
        Saves the application state to the control file.

        Args:
            state (State): The application state to save.
        """
        utils.write_json_file(Config.CONTROL_FILE_PATH, state.to_json())
        self._logger.debug(f"State saved to {Config.CONTROL_FILE_PATH}")

    def _quit(self, exit_code: int = 0) -> None:
        """
        Saves the state and exits the application.

        Args:
            exit_code (int): The exit code to use.
        """
        if hasattr(self, "state"):
            self._save_state(self._state)
            self._logger.debug("Application is exiting, state saved.")
        else:
            self._logger.debug("Application is exiting, no state found, not saving.")

        if exit_code == 0:
            self._logger.debug(f"Exiting application with code {exit_code}.")
        else:
            self._logger.warning(f"Exiting application with code {exit_code}.")
        sys.exit(exit_code)

    def _extract_playlist(self) -> None:
        """
        Extracts the playlist information and adds new songs to the state.
        """
        new_mp3s = playlist.scrap_playlist(
            self._state.playlist_url_id, self._logger, Config.PLAYLIST_JSON_PATH
        )
        by_urls = dict([(mp3.url_id, mp3) for mp3 in new_mp3s])
        del new_mp3s

        new_urls = by_urls.keys() - self._state.by_urls.keys()
        for url in new_urls:
            mp3 = by_urls[url]
            self._state.add(mp3)
            self._process_queue.append(mp3)
        self._logger.debug(f"Found {len(new_urls)} new files to download.")

    def _process_files(self) -> None:
        """
        Processes the files in the work queue, downloading and updating tags as needed.
        """
        progress_left = 900
        increment = progress_left / len(self._process_queue)
        actual = 0
        total = len(self._process_queue)
        self._progress_bar.update(0, prefix=f"Processing {actual}/{total} files")
        while len(self._process_queue) > 0:
            mp3 = self._process_queue[0]
            match mp3.state:
                case Mp3.State.CREATED:
                    self._download_file(mp3)
                case Mp3.State.DOWNLOADED:
                    self._update_tags(mp3)
                case Mp3.State.DONE:
                    self._process_queue.popleft()
                    actual += 1
                    self._progress_bar.update(
                        increment, prefix=f"Processing {actual}/{total} files"
                    )

    def _download_file(self, mp3: Mp3) -> None:
        """
        Downloads a single mp3 file.

        Args:
            mp3 (Mp3): The Mp3 object representing the file to download.
        """
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

        downloads.download_yt_audio(self._logger, mp3.url_id, mp3.file_path)
        mp3.state = Mp3.State.DOWNLOADED

    def _update_tags(self, mp3: Mp3) -> None:
        """
        Updates the tags of a downloaded mp3 file.

        Args:
            mp3 (Mp3): The Mp3 object representing the file to update.
        """
        tags = {"artist": mp3.artist, "title": mp3.title}
        if mp3.album is not None:
            tags["album"] = mp3.album
        update_tags.update_mp3_tags(self._logger, mp3.file_path, tags)  # type: ignore
        mp3.state = Mp3.State.DONE

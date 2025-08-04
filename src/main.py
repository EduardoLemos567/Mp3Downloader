from app import App

YOUR_PLAYLIST_LINK = "https://music.youtube.com/playlist?list=PL01A6QrFoyxPl3Ih-zbwfGWnrB1zUk6VP&si=OnxnbKSn7V8GGfu2"

import logging

if __name__ == "__main__":
    app = App(YOUR_PLAYLIST_LINK, logging.DEBUG)
    app.run()

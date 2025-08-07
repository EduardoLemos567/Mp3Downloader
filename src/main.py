import logging
from app import App

if __name__ == "__main__":
    """
    Main entry point of the application.
    """
    app = App(logging.DEBUG)
    app.run()

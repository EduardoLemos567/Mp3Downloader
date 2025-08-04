import logging, json, sys, typing, re, unicodedata, os
from pathlib import Path


def setup_logger(
    name: str,
    file_path: Path,
    file_level: int = logging.WARNING,
    console_level: int = logging.INFO,
) -> logging.Logger:
    """Set up a logger that outputs to both console and file"""
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s [%(module)s:%(funcName)s:%(lineno)d]"
    )

    # Create file handler
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(file_path, mode="a")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)

    # Create console handler (acts like print)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(console_level)

    # Add both handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.debug(f"Logger '{name}' set up with file '{file_path}'")
    return logger


def read_json_file(file_path: Path) -> dict[str, typing.Any]:
    """Read a JSON file and return its content"""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json_file(file_path: Path, data: dict[str, typing.Any]) -> None:
    """Write data to a JSON file"""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def progress_bar(
    current: float, total: float, bar_length: int = 50, prefix: str = ""
) -> None:
    """Display a progress bar in the console"""
    percent = (current / total) * 100
    filled_length = int(bar_length * current // total)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)

    print(
        f"\r{prefix[:20].rjust(20)} |{bar}| {f"{percent:.2f}".rjust(6)}% Complete",
        end="\r",
    )

    if current == total:
        print()


class ProgressBar:
    def __init__(self, total: float, bar_length: int = 50):
        self.total = total
        self.bar_length = bar_length
        self.current: float = 0

    def update(self, increment: float, prefix: str) -> None:
        self.current += increment
        progress_bar(self.current, self.total, self.bar_length, prefix)

    def done(self, prefix: str):
        progress_bar(self.total, self.total, self.bar_length, prefix)


def grab_id_from_url(playlist_url: str) -> str:
    del1 = "list="
    del2 = "&"
    a = playlist_url.find(del1)
    if a >= 0:
        a += len(del1)
        url2 = playlist_url[a:]
        b = url2.find(del2)
        if b >= 0:
            return url2[:b]
        return url2
    return playlist_url


def fix_file_name(file_name: str, replacement: str = "_") -> str:
    """
    Sanitize a filename to make it valid across different operating systems.

    Args:
        filename: The original filename to sanitize
        replacement: Character to replace invalid characters with (default: "_")

    Returns:
        A sanitized filename that should work across Windows, Linux, and macOS
    """
    # Normalize unicode characters (convert accents to ASCII equivalents where possible)
    file_name = (
        unicodedata.normalize("NFKD", file_name)
        .encode("ascii", "ignore")
        .decode("ascii")
    )

    # Define invalid characters for different OSes
    # Windows has the most restrictions, so we'll use that as our base
    invalid_chars = r'<>:"/\|?*'
    invalid_chars += "".join(chr(i) for i in range(32))  # ASCII control characters
    invalid_chars += "\x7f"  # DEL character

    # Replace invalid characters
    for char in invalid_chars:
        file_name = file_name.replace(char, replacement)

    # Remove leading/trailing spaces and dots (Windows doesn't like these)
    file_name = file_name.strip(". ")

    # Replace consecutive replacement characters with a single one
    file_name = re.sub(f"[{re.escape(replacement)}]+", replacement, file_name)

    # Truncate long filenames (255 chars is a safe limit for most filesystems)
    max_length = 255
    if len(file_name) > max_length:
        # Keep the file extension if possible
        name, ext = os.path.splitext(file_name)
        name = name[: max_length - len(ext)]
        file_name = name + ext

    # Handle special cases (like reserved names on Windows)
    if os.name == "nt":
        reserved_names = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        }
        root, ext = os.path.splitext(file_name)
        if root.upper() in reserved_names:
            file_name = f"{root}{replacement}.{ext}"

    return file_name

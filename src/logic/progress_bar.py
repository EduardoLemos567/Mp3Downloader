class ProgressBar:
    """
    A simple progress bar for console applications.
    """

    def __init__(self, total: float, bar_length: int = 50):
        """
        Initializes the ProgressBar.

        Args:
            total (float): The total value for the progress bar.
            bar_length (int): The length of the progress bar in characters.
        """
        self.total = total
        self.bar_length = bar_length
        self.current: float = 0

    def update(self, increment: float, prefix: str) -> None:
        """
        Updates the progress bar with a given increment.

        Args:
            increment (float): The value to increment the progress bar by.
            prefix (str): A prefix to display before the progress bar.
        """
        self.current += increment
        self._update_progress_bar(self.current, self.total, self.bar_length, prefix)

    def done(self, prefix: str):
        """
        Marks the progress bar as done.

        Args:
            prefix (str): A prefix to display before the progress bar.
        """
        self._update_progress_bar(self.total, self.total, self.bar_length, prefix)

    def _update_progress_bar(
        self, current: float, total: float, bar_length: int = 50, prefix: str = ""
    ) -> None:
        """Display a progress bar in the console"""
        current = min(current, total)
        percent = (current / total) * 100
        filled_length = int(round(bar_length * current // total))
        bar = "█" * filled_length + "-" * (bar_length - filled_length)

        print(
            f"\r{prefix[:20].rjust(20)} |{bar}| {f'{percent:.2f}'.rjust(6)}% Complete",
            end="\r",
        )

        if current == total:
            print()

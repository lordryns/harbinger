import time

class Logger:
    def __init__(self) -> None:
        self.log_count = 0
        self.max_level_len = max(len(level) for level in ["success", "info", "warning", "error"])

    def success(self, log: str, show_time=False) -> None:
        self._log(log, "success", show_time)

    def info(self, log: str, show_time=False) -> None:
        self._log(log, "info", show_time)

    def warning(self, log: str, show_time=False) -> None:
        self._log(log, "warning", show_time)

    def error(self, log: str, show_time=False) -> None:
        self._log(log, "error", show_time)

    def _log(self, message: str, level: str, show_time: bool) -> None:
        time_str = f"({time.ctime()}) " if show_time else ""
        padded_level = level.upper().ljust(self.max_level_len)
        print(f"{time_str}[ {padded_level} ] - {message}")

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from services.application_paths import ApplicationPaths


class LoggingService:
    """Configure and expose Scriptolator application logging."""

    LOGGER_NAME = "scriptolator"
    LOG_FILE_NAME = "scriptolator.log"
    MAX_LOG_BYTES = 1_000_000
    BACKUP_COUNT = 3

    def __init__(
        self,
        paths: ApplicationPaths | Path,
    ) -> None:
        if isinstance(paths, ApplicationPaths):
            self.log_folder = paths.logs
        else:
            self.log_folder = Path(paths) / "logs"

        self.log_path = self.log_folder / self.LOG_FILE_NAME

        self.logger = logging.getLogger(self.LOGGER_NAME)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        self._configure_handler()

    def _configure_handler(self) -> None:
        """Create one rotating UTF-8 log handler."""

        resolved_log_path = self.log_path.resolve()

        for handler in self.logger.handlers:
            if not isinstance(handler, RotatingFileHandler):
                continue

            if Path(handler.baseFilename) == resolved_log_path:
                return

        self.log_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        handler = RotatingFileHandler(
            filename=self.log_path,
            maxBytes=self.MAX_LOG_BYTES,
            backupCount=self.BACKUP_COUNT,
            encoding="utf-8",
        )

        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

        self.logger.addHandler(handler)

    def info(self, message: str) -> None:
        """Write an informational log entry."""

        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Write a warning log entry."""

        self.logger.warning(message)

    def error(
        self,
        message: str,
        *,
        include_traceback: bool = False,
    ) -> None:
        """Write an error log entry."""

        self.logger.error(
            message,
            exc_info=include_traceback,
        )

    def exception(self, message: str) -> None:
        """Write an error entry with the current traceback."""

        self.logger.exception(message)
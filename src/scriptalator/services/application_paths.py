import os
import sys
from dataclasses import dataclass
from pathlib import Path

from version import APP_NAME


@dataclass(frozen=True)
class ApplicationPaths:
    """Provide stable resource and writable-data locations."""

    application_root: Path
    data_root: Path
    output: Path
    profiles: Path
    projects: Path
    logs: Path
    recovery: Path
    settings: Path

    @classmethod
    def create(cls) -> "ApplicationPaths":
        """Create and initialize Scriptolator application paths."""

        application_root = cls._application_root()
        data_root = cls._data_root()

        paths = cls(
            application_root=application_root,
            data_root=data_root,
            output=data_root / "Output",
            profiles=data_root / "Profiles",
            projects=data_root / "Projects",
            logs=data_root / "Logs",
            recovery=data_root / "Recovery",
            settings=data_root / "Settings",
        )

        paths.ensure_directories()
        return paths

    def ensure_directories(self) -> None:
        """Create all writable application directories."""

        for folder in (
            self.data_root,
            self.output,
            self.profiles,
            self.projects,
            self.logs,
            self.recovery,
            self.settings,
        ):
            try:
                folder.mkdir(parents=True, exist_ok=True)
            except OSError as error:
                raise RuntimeError(
                    (
                        "Scriptolator could not create its data "
                        f"folder:\n{folder}\n\n{error}"
                    )
                ) from error

    @staticmethod
    def _application_root() -> Path:
        """Return the source-project or executable directory."""

        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent

        return Path(__file__).resolve().parents[3]

    @staticmethod
    def _data_root() -> Path:
        """Return the per-user writable Scriptolator folder."""

        if sys.platform == "win32":
            local_app_data = os.environ.get(
                "LOCALAPPDATA",
                "",
            ).strip()

            if local_app_data:
                return Path(local_app_data) / APP_NAME

        return Path.home() / f".{APP_NAME.casefold()}"
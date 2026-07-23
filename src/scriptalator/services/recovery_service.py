import json
from pathlib import Path
from typing import Any

from services.application_paths import ApplicationPaths
from services.project_service import ProjectService


class RecoveryService:
    """Save and restore one automatic Scriptolator recovery project."""

    RECOVERY_FILE_NAME = "unsaved-recovery.scriptolator"
    RECOVERY_FORMAT_NAME = "Scriptolator Recovery"
    RECOVERY_FORMAT_VERSION = 1

    def __init__(
        self,
        paths: ApplicationPaths | Path,
    ) -> None:
        if isinstance(paths, ApplicationPaths):
            self.recovery_folder = paths.recovery
        else:
            self.recovery_folder = Path(paths) / "recovery"

        self.recovery_path = (
            self.recovery_folder / self.RECOVERY_FILE_NAME
        )

    def has_recovery(self) -> bool:
        """Return whether a recovery file currently exists."""

        return self.recovery_path.is_file()

    def save_recovery(
        self,
        project_data: dict[str, Any],
        current_project_path: Path | None,
    ) -> Path:
        """Write current unsaved work to the recovery file."""

        validated_project = ProjectService.validate_project_data(
            project_data
        )

        file_data = {
            "format": self.RECOVERY_FORMAT_NAME,
            "format_version": self.RECOVERY_FORMAT_VERSION,
            "current_project_path": (
                str(current_project_path)
                if current_project_path is not None
                else ""
            ),
            "project": validated_project,
        }

        temporary_path = self.recovery_path.with_suffix(
            self.recovery_path.suffix + ".tmp"
        )

        try:
            self.recovery_folder.mkdir(
                parents=True,
                exist_ok=True,
            )

            temporary_path.write_text(
                json.dumps(
                    file_data,
                    indent=4,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            temporary_path.replace(self.recovery_path)
        except OSError as error:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass

            raise RuntimeError(
                f"Unable to save recovery data:\n{error}"
            ) from error

        return self.recovery_path

    def load_recovery(
        self,
    ) -> tuple[dict[str, Any], Path | None]:
        """Load and validate the recovery project."""

        if not self.recovery_path.is_file():
            raise FileNotFoundError(
                f"Recovery file not found:\n{self.recovery_path}"
            )

        try:
            file_text = self.recovery_path.read_text(
                encoding="utf-8"
            )
        except OSError as error:
            raise RuntimeError(
                f"Unable to read recovery data:\n{error}"
            ) from error

        try:
            file_data = json.loads(file_text)
        except json.JSONDecodeError as error:
            raise ValueError(
                "The recovery file is not valid JSON."
            ) from error

        if not isinstance(file_data, dict):
            raise ValueError(
                "The recovery file is not valid."
            )

        if (
            file_data.get("format")
            != self.RECOVERY_FORMAT_NAME
        ):
            raise ValueError(
                "The file is not a Scriptolator recovery file."
            )

        if (
            file_data.get("format_version")
            != self.RECOVERY_FORMAT_VERSION
        ):
            raise ValueError(
                "The recovery file uses an unsupported version."
            )

        project_data = file_data.get("project")

        if not isinstance(project_data, dict):
            raise ValueError(
                "The recovery project data is missing or invalid."
            )

        validated_project = (
            ProjectService.validate_project_data(
                project_data
            )
        )

        saved_project_path = str(
            file_data.get("current_project_path", "")
        ).strip()

        current_project_path = (
            Path(saved_project_path)
            if saved_project_path
            else None
        )

        return validated_project, current_project_path

    def discard_recovery(self) -> None:
        """Delete the current recovery file."""

        try:
            self.recovery_path.unlink(missing_ok=True)
        except OSError as error:
            raise RuntimeError(
                f"Unable to remove recovery data:\n{error}"
            ) from error

        try:
            self.recovery_folder.rmdir()
        except OSError:
            pass
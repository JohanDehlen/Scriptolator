import json
from pathlib import Path
from typing import Any


class ProjectService:
    """Save and load Scriptolator project files."""

    FILE_EXTENSION = ".scriptolator"
    LEGACY_FILE_EXTENSION = ".scriptalator"

    FORMAT_NAME = "Scriptolator Project"
    LEGACY_FORMAT_NAME = "Scriptalator Project"
    FORMAT_VERSION = 1

    REQUIRED_FIELDS = {
        "script",
        "language",
        "voice",
        "speed",
        "pitch",
        "volume",
        "output_folder",
        "output_filename",
    }

    @classmethod
    def save_project(
        cls,
        project_path: Path,
        project_data: dict[str, Any],
    ) -> Path:
        """Write project data to a Scriptolator project file."""

        normalized_path = cls.normalize_project_path(project_path)
        validated_data = cls.validate_project_data(project_data)

        file_data = {
            "format": cls.FORMAT_NAME,
            "format_version": cls.FORMAT_VERSION,
            "project": validated_data,
        }

        temporary_path = normalized_path.with_suffix(
            normalized_path.suffix + ".tmp"
        )
        backup_path = normalized_path.with_suffix(
            normalized_path.suffix + ".bak"
        )

        try:
            normalized_path.parent.mkdir(
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

            if normalized_path.is_file():
                backup_path.write_bytes(
                    normalized_path.read_bytes()
                )

            temporary_path.replace(normalized_path)
        except OSError as error:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass

            raise RuntimeError(
                f"Unable to save the project:\n{error}"
            ) from error

        if not normalized_path.is_file():
            raise RuntimeError(
                "The project file was not created."
            )

        return normalized_path.resolve()

    @classmethod
    def get_backup_path(
        cls,
        project_path: Path,
    ) -> Path:
        """Return the automatic backup path for a project."""

        normalized_path = cls.normalize_project_path(project_path)

        return normalized_path.with_suffix(
            normalized_path.suffix + ".bak"
        )

    @classmethod
    def load_project(
        cls,
        project_path: Path,
    ) -> dict[str, Any]:
        """Read and validate a Scriptolator or legacy project file."""

        normalized_path = Path(project_path).expanduser()

        if not normalized_path.is_file():
            raise FileNotFoundError(
                f"Project file not found:\n{normalized_path}"
            )

        try:
            file_text = normalized_path.read_text(
                encoding="utf-8"
            )
        except OSError as error:
            raise RuntimeError(
                f"Unable to read the project:\n{error}"
            ) from error

        try:
            file_data = json.loads(file_text)
        except json.JSONDecodeError as error:
            raise ValueError(
                "The selected file is not valid JSON."
            ) from error

        if not isinstance(file_data, dict):
            raise ValueError(
                "The selected file is not a valid Scriptolator project."
            )

        format_name = file_data.get("format")

        if format_name not in {
            cls.FORMAT_NAME,
            cls.LEGACY_FORMAT_NAME,
        }:
            raise ValueError(
                "The selected file is not a Scriptolator project."
            )

        format_version = file_data.get("format_version")

        if format_version != cls.FORMAT_VERSION:
            raise ValueError(
                "This project uses an unsupported format version."
            )

        project_data = file_data.get("project")

        if not isinstance(project_data, dict):
            raise ValueError(
                "The project data is missing or invalid."
            )

        return cls.validate_project_data(project_data)

    @classmethod
    def normalize_project_path(
        cls,
        project_path: Path,
    ) -> Path:
        """Return a project path using the Scriptolator extension."""

        normalized_path = Path(project_path).expanduser()
        lower_name = normalized_path.name.lower()

        if lower_name.endswith(cls.FILE_EXTENSION):
            return normalized_path

        if lower_name.endswith(cls.LEGACY_FILE_EXTENSION):
            return normalized_path.with_suffix(
                cls.FILE_EXTENSION
            )

        return normalized_path.with_name(
            normalized_path.name + cls.FILE_EXTENSION
        )

    @classmethod
    def is_supported_project_path(
        cls,
        project_path: Path,
    ) -> bool:
        """Return whether a path uses a supported project extension."""

        suffix = Path(project_path).suffix.lower()

        return suffix in {
            cls.FILE_EXTENSION,
            cls.LEGACY_FILE_EXTENSION,
        }

    @classmethod
    def validate_project_data(
        cls,
        project_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate and normalize project values."""

        if not isinstance(project_data, dict):
            raise TypeError(
                "Project data must be provided as a dictionary."
            )

        missing_fields = (
            cls.REQUIRED_FIELDS - project_data.keys()
        )

        if missing_fields:
            missing_list = ", ".join(
                sorted(missing_fields)
            )

            raise ValueError(
                f"Project data is missing: {missing_list}"
            )

        script = cls._require_string(
            project_data,
            "script",
        )
        language = cls._require_string(
            project_data,
            "language",
        )
        voice = cls._require_string(
            project_data,
            "voice",
        )
        output_folder = cls._require_string(
            project_data,
            "output_folder",
        )
        output_filename = cls._require_string(
            project_data,
            "output_filename",
        )

        speed = cls._require_integer(
            project_data,
            "speed",
            minimum=-100,
            maximum=100,
        )
        pitch = cls._require_integer(
            project_data,
            "pitch",
            minimum=-100,
            maximum=100,
        )
        volume = cls._require_integer(
            project_data,
            "volume",
            minimum=0,
            maximum=100,
        )

        return {
            "script": script,
            "language": language,
            "voice": voice,
            "speed": speed,
            "pitch": pitch,
            "volume": volume,
            "output_folder": output_folder,
            "output_filename": output_filename,
        }

    @staticmethod
    def _require_string(
        project_data: dict[str, Any],
        field_name: str,
    ) -> str:
        """Return a string project value or raise an error."""

        value = project_data.get(field_name)

        if not isinstance(value, str):
            raise ValueError(
                f"Project field '{field_name}' must be text."
            )

        return value

    @staticmethod
    def _require_integer(
        project_data: dict[str, Any],
        field_name: str,
        minimum: int,
        maximum: int,
    ) -> int:
        """Return an integer within the accepted range."""

        value = project_data.get(field_name)

        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(
                f"Project field '{field_name}' must be an integer."
            )

        if not minimum <= value <= maximum:
            raise ValueError(
                (
                    f"Project field '{field_name}' must be between "
                    f"{minimum} and {maximum}."
                )
            )

        return value
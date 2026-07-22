import json
from pathlib import Path
from typing import Any


class ProjectService:
    """Save and load Scriptalator project files."""

    FILE_EXTENSION = ".scriptalator"
    FORMAT_NAME = "Scriptalator Project"
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
        """Write project data to a Scriptalator project file."""

        normalized_path = cls.normalize_project_path(project_path)
        validated_data = cls.validate_project_data(project_data)

        file_data = {
            "format": cls.FORMAT_NAME,
            "format_version": cls.FORMAT_VERSION,
            "project": validated_data,
        }

        try:
            normalized_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            normalized_path.write_text(
                json.dumps(
                    file_data,
                    indent=4,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        except OSError as error:
            raise RuntimeError(
                f"Unable to save the project:\n{error}"
            ) from error

        if not normalized_path.is_file():
            raise RuntimeError(
                "The project file was not created."
            )

        return normalized_path

    @classmethod
    def load_project(
        cls,
        project_path: Path,
    ) -> dict[str, Any]:
        """Read and validate a Scriptalator project file."""

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
                "The selected file is not a valid Scriptalator project."
            )

        if file_data.get("format") != cls.FORMAT_NAME:
            raise ValueError(
                "The selected file is not a Scriptalator project."
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
        """Add the Scriptalator extension when it is missing."""

        normalized_path = Path(project_path).expanduser()

        if normalized_path.name.lower().endswith(
            cls.FILE_EXTENSION
        ):
            return normalized_path

        return normalized_path.with_name(
            normalized_path.name + cls.FILE_EXTENSION
        )

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
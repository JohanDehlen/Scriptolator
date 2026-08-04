from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Final


@dataclass(frozen=True, slots=True)
class SpeechVoice:
    """Normalized metadata shared by every speech engine."""

    short_name: str
    locale: str
    gender: str
    friendly_name: str

    def as_dict(self) -> dict[str, str]:
        """Return the legacy dictionary shape used by the current UI."""

        return {
            "short_name": self.short_name,
            "locale": self.locale,
            "gender": self.gender,
            "friendly_name": self.friendly_name,
        }


class SpeechEngine(ABC):
    """Define the common contract implemented by narration engines."""

    engine_id: Final[str]
    display_name: Final[str]

    @abstractmethod
    def get_voice_details(self) -> list[dict[str, str]]:
        """Return normalized voice metadata for the engine."""

    def get_voices(self) -> list[str]:
        """Return the available voice short names."""

        return [
            voice["short_name"]
            for voice in self.get_voice_details()
        ]

    @abstractmethod
    def generate_mp3(
        self,
        text: str,
        voice: str,
        output_path: str | Path,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
    ) -> Path:
        """Generate an MP3 narration and return its resolved path."""

    @staticmethod
    def validate_generation_request(
        text: str,
        voice: str,
        output_path: str | Path,
    ) -> tuple[str, str, Path]:
        """Validate and normalize common synthesis inputs."""

        normalized_text = text.strip()
        normalized_voice = voice.strip()

        if not normalized_text:
            raise ValueError("Narration text cannot be empty.")

        if not normalized_voice:
            raise ValueError(
                "A narration voice must be selected."
            )

        destination = Path(output_path).expanduser()

        if destination.suffix.lower() != ".mp3":
            raise ValueError(
                "The output filename must end with .mp3."
            )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        return (
            normalized_text,
            normalized_voice,
            destination,
        )

    @staticmethod
    def validate_generated_audio(
        destination: Path,
    ) -> Path:
        """Ensure synthesis produced a usable output file."""

        if (
            not destination.is_file()
            or destination.stat().st_size == 0
        ):
            raise RuntimeError(
                "Narration generation completed without "
                "producing audio."
            )

        return destination.resolve()
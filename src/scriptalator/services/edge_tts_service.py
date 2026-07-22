import asyncio
from pathlib import Path
from typing import Any

import edge_tts


class EdgeTTSService:
    """Provide Microsoft Edge voice discovery and speech synthesis."""

    @staticmethod
    def get_voices() -> list[str]:
        """Return the available Microsoft Edge voice short names."""

        return [
            voice["short_name"]
            for voice in EdgeTTSService.get_voice_details()
        ]

    @staticmethod
    def get_voice_details() -> list[dict[str, str]]:
        """Return normalized metadata for available Microsoft Edge voices."""

        return asyncio.run(
            EdgeTTSService._load_voice_details()
        )

    @staticmethod
    async def _load_voice_details() -> list[dict[str, str]]:
        """Retrieve and normalize voice metadata from Microsoft Edge TTS."""

        manager = await edge_tts.VoicesManager.create()

        voice_details = [
            EdgeTTSService._normalize_voice_metadata(voice)
            for voice in manager.voices
        ]

        return sorted(
            voice_details,
            key=lambda voice: (
                voice["locale"].lower(),
                voice["friendly_name"].lower(),
                voice["short_name"].lower(),
            ),
        )

    @staticmethod
    def _normalize_voice_metadata(
        voice: dict[str, Any],
    ) -> dict[str, str]:
        """Convert Microsoft voice metadata into a stable structure."""

        short_name = str(
            voice.get("ShortName", "")
        ).strip()

        locale = str(
            voice.get("Locale", "")
        ).strip()

        gender = str(
            voice.get("Gender", "")
        ).strip()

        friendly_name = str(
            voice.get("FriendlyName", "")
        ).strip()

        if not friendly_name:
            friendly_name = EdgeTTSService._name_from_short_name(
                short_name
            )

        return {
            "short_name": short_name,
            "locale": locale,
            "gender": gender,
            "friendly_name": friendly_name,
        }

    @staticmethod
    def _name_from_short_name(short_name: str) -> str:
        """Derive a readable voice name from a Microsoft short name."""

        if not short_name:
            return "Unknown Voice"

        name_part = short_name.rsplit("-", 1)[-1]

        if name_part.lower().endswith("neural"):
            name_part = name_part[:-6]

        return name_part or short_name

    @staticmethod
    def generate_mp3(
        text: str,
        voice: str,
        output_path: str | Path,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
    ) -> Path:
        """
        Generate an MP3 narration file.

        Args:
            text: Narration text to synthesize.
            voice: Microsoft Edge voice short name.
            output_path: Destination path for the MP3 file.
            rate: Speaking-rate adjustment, such as ``+0%`` or ``-10%``.
            pitch: Pitch adjustment, such as ``+0Hz`` or ``-5Hz``.
            volume: Volume adjustment, such as ``+0%`` or ``-10%``.

        Returns:
            The resolved path of the generated MP3 file.

        Raises:
            ValueError: If required input is missing or the output is not MP3.
            RuntimeError: If synthesis completes without creating usable audio.
        """

        normalized_text = text.strip()
        normalized_voice = voice.strip()

        if not normalized_text:
            raise ValueError("Narration text cannot be empty.")

        if not normalized_voice:
            raise ValueError("A narration voice must be selected.")

        destination = Path(output_path).expanduser()

        if destination.suffix.lower() != ".mp3":
            raise ValueError(
                "The output filename must end with .mp3."
            )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        asyncio.run(
            EdgeTTSService._generate_mp3(
                text=normalized_text,
                voice=normalized_voice,
                output_path=destination,
                rate=rate,
                pitch=pitch,
                volume=volume,
            )
        )

        if (
            not destination.is_file()
            or destination.stat().st_size == 0
        ):
            raise RuntimeError(
                "Narration generation completed without producing audio."
            )

        return destination.resolve()

    @staticmethod
    async def _generate_mp3(
        text: str,
        voice: str,
        output_path: Path,
        rate: str,
        pitch: str,
        volume: str,
    ) -> None:
        """Generate and save narration through Microsoft Edge TTS."""

        communicator = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            pitch=pitch,
            volume=volume,
        )

        await communicator.save(str(output_path))
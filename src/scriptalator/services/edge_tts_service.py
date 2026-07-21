import asyncio
from pathlib import Path
from typing import List

import edge_tts


class EdgeTTSService:
    """Provide Microsoft Edge voice discovery and speech synthesis."""

    @staticmethod
    def get_voices() -> List[str]:
        """Return the available Microsoft Edge voice short names."""

        return asyncio.run(EdgeTTSService._load_voices())

    @staticmethod
    async def _load_voices() -> List[str]:
        """Retrieve voice information from Microsoft Edge TTS."""

        manager = await edge_tts.VoicesManager.create()

        return sorted(
            voice["ShortName"]
            for voice in manager.voices
        )

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
            raise ValueError("The output filename must end with .mp3.")

        destination.parent.mkdir(parents=True, exist_ok=True)

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

        if not destination.is_file() or destination.stat().st_size == 0:
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
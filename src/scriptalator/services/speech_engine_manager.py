from __future__ import annotations

from pathlib import Path
from typing import Final

from services.azure_tts_service import AzureTTSService
from services.edge_tts_service import EdgeTTSService


class SpeechEngineManager:
    """Manage and delegate to Scriptolator's active speech engine."""

    EDGE_ENGINE_ID: Final[str] = "edge"
    AZURE_ENGINE_ID: Final[str] = "azure"

    EDGE_DISPLAY_NAME: Final[str] = "Microsoft Edge"
    AZURE_DISPLAY_NAME: Final[str] = "Microsoft Azure AI Speech"

    def __init__(self) -> None:
        """Create the manager with Microsoft Edge selected."""

        self._engine_id = self.EDGE_ENGINE_ID
        self._engine: EdgeTTSService | AzureTTSService = (
            EdgeTTSService()
        )

    @classmethod
    def available_engines(cls) -> dict[str, str]:
        """Return supported engine IDs and display names."""

        return {
            cls.EDGE_ENGINE_ID: cls.EDGE_DISPLAY_NAME,
            cls.AZURE_ENGINE_ID: cls.AZURE_DISPLAY_NAME,
        }

    @property
    def current_engine_id(self) -> str:
        """Return the active engine identifier."""

        return self._engine_id

    @property
    def current_engine_name(self) -> str:
        """Return the active engine's display name."""

        return self.available_engines()[self._engine_id]

    @property
    def current_engine(
        self,
    ) -> EdgeTTSService | AzureTTSService:
        """Return the active engine instance."""

        return self._engine

    def use_edge(self) -> None:
        """Select Microsoft Edge speech synthesis."""

        self._engine = EdgeTTSService()
        self._engine_id = self.EDGE_ENGINE_ID

    def use_azure(
        self,
        subscription_key: str,
        region: str,
    ) -> None:
        """Select Microsoft Azure AI Speech."""

        self._engine = AzureTTSService(
            subscription_key=subscription_key,
            region=region,
        )
        self._engine_id = self.AZURE_ENGINE_ID

    def select_engine(
        self,
        engine_id: str,
        *,
        azure_subscription_key: str = "",
        azure_region: str = "",
    ) -> None:
        """Select an engine by its stable identifier."""

        normalized_engine_id = engine_id.strip().lower()

        if normalized_engine_id == self.EDGE_ENGINE_ID:
            self.use_edge()
            return

        if normalized_engine_id == self.AZURE_ENGINE_ID:
            self.use_azure(
                subscription_key=azure_subscription_key,
                region=azure_region,
            )
            return

        supported = ", ".join(
            sorted(self.available_engines())
        )

        raise ValueError(
            "Unsupported speech engine: "
            f"{engine_id!r}. Supported engines: {supported}."
        )

    def get_voice_details(self) -> list[dict[str, str]]:
        """Return normalized voices from the active engine."""

        return self._engine.get_voice_details()

    def get_voices(self) -> list[str]:
        """Return voice short names from the active engine."""

        return self._engine.get_voices()

    def generate_mp3(
        self,
        text: str,
        voice: str,
        output_path: str | Path,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
    ) -> Path:
        """Generate narration through the active engine."""

        return self._engine.generate_mp3(
            text=text,
            voice=voice,
            output_path=output_path,
            rate=rate,
            pitch=pitch,
            volume=volume,
        )
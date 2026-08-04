from __future__ import annotations

import os
from html import escape
from pathlib import Path
from typing import Any, Final

import azure.cognitiveservices.speech as speechsdk

from services.speech_engine import SpeechEngine, SpeechVoice


class AzureTTSService(SpeechEngine):
    """Provide Azure AI Speech voice discovery and synthesis."""

    engine_id: Final[str] = "azure"
    display_name: Final[str] = "Microsoft Azure AI Speech"

    KEY_ENVIRONMENT_VARIABLE: Final[str] = "AZURE_SPEECH_KEY"
    REGION_ENVIRONMENT_VARIABLE: Final[str] = "AZURE_SPEECH_REGION"

    def __init__(
        self,
        subscription_key: str | None = None,
        region: str | None = None,
    ) -> None:
        """
        Create an Azure AI Speech service.

        Credentials may be provided directly or through the
        ``AZURE_SPEECH_KEY`` and ``AZURE_SPEECH_REGION`` environment
        variables. Direct values take precedence.
        """

        self.subscription_key = (
            subscription_key
            or os.getenv(self.KEY_ENVIRONMENT_VARIABLE, "")
        ).strip()
        self.region = (
            region
            or os.getenv(self.REGION_ENVIRONMENT_VARIABLE, "")
        ).strip()

    def is_configured(self) -> bool:
        """Return whether both required Azure credentials are present."""

        return bool(self.subscription_key and self.region)

    def get_voice_details(self) -> list[dict[str, str]]:
        """Return normalized metadata for available Azure voices."""

        speech_config = self._create_speech_config()
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=None,
        )

        result = synthesizer.get_voices_async().get()

        if (
            result.reason
            != speechsdk.ResultReason.VoicesListRetrieved
        ):
            error_details = str(
                getattr(
                    result,
                    "error_details",
                    "Azure did not return a voice list.",
                )
            ).strip()

            raise RuntimeError(
                "Azure voice discovery failed. "
                f"{error_details}"
            )

        voices = [
            self._normalize_voice_metadata(voice)
            for voice in result.voices
        ]

        return sorted(
            voices,
            key=lambda voice: (
                voice["locale"].lower(),
                voice["friendly_name"].lower(),
                voice["short_name"].lower(),
            ),
        )

    def generate_mp3(
        self,
        text: str,
        voice: str,
        output_path: str | Path,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
    ) -> Path:
        """
        Generate an Azure AI Speech MP3 narration.

        Args:
            text: Narration text to synthesize.
            voice: Azure voice short name.
            output_path: Destination path ending in ``.mp3``.
            rate: SSML speaking-rate adjustment such as ``+0%``.
            pitch: SSML pitch adjustment such as ``+0Hz``.
            volume: SSML volume adjustment such as ``+0%``.

        Returns:
            The resolved output path.

        Raises:
            ValueError: If required input or adjustment syntax is invalid.
            RuntimeError: If Azure configuration or synthesis fails.
        """

        (
            normalized_text,
            normalized_voice,
            destination,
        ) = self.validate_generation_request(
            text=text,
            voice=voice,
            output_path=output_path,
        )

        normalized_rate = self._validate_percentage(
            rate,
            "rate",
        )
        normalized_pitch = self._validate_pitch(pitch)
        normalized_volume = self._validate_percentage(
            volume,
            "volume",
        )

        speech_config = self._create_speech_config()
        speech_config.speech_synthesis_voice_name = (
            normalized_voice
        )
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat
            .Audio24Khz96KBitRateMonoMp3
        )

        audio_config = speechsdk.audio.AudioOutputConfig(
            filename=str(destination)
        )
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )

        ssml = self._build_ssml(
            text=normalized_text,
            voice=normalized_voice,
            rate=normalized_rate,
            pitch=normalized_pitch,
            volume=normalized_volume,
        )

        result = synthesizer.speak_ssml_async(ssml).get()

        if (
            result.reason
            == speechsdk.ResultReason.SynthesizingAudioCompleted
        ):
            return self.validate_generated_audio(destination)

        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details

            if cancellation is None:
                raise RuntimeError(
                    "Azure speech synthesis was canceled "
                    "without additional details."
                )

            details = str(
                cancellation.error_details or ""
            ).strip()

            message = (
                "Azure speech synthesis was canceled. "
                f"Reason: {cancellation.reason}."
            )

            if details:
                message = f"{message} Details: {details}"

            raise RuntimeError(message)

        raise RuntimeError(
            "Azure speech synthesis returned an unexpected "
            f"result: {result.reason}."
        )

    def _create_speech_config(
        self,
    ) -> speechsdk.SpeechConfig:
        """Create an authenticated Azure Speech configuration."""

        if not self.subscription_key:
            raise RuntimeError(
                "Azure Speech is not configured. "
                f"Set {self.KEY_ENVIRONMENT_VARIABLE} or provide "
                "a subscription key."
            )

        if not self.region:
            raise RuntimeError(
                "Azure Speech is not configured. "
                f"Set {self.REGION_ENVIRONMENT_VARIABLE} or provide "
                "a region."
            )

        return speechsdk.SpeechConfig(
            subscription=self.subscription_key,
            region=self.region,
        )

    @classmethod
    def _normalize_voice_metadata(
        cls,
        voice: Any,
    ) -> dict[str, str]:
        """Convert Azure voice metadata into Scriptolator's format."""

        short_name = str(
            getattr(voice, "short_name", "")
        ).strip()
        locale = str(
            getattr(voice, "locale", "")
        ).strip()
        gender = cls._normalize_gender(
            getattr(voice, "gender", "")
        )

        friendly_name = str(
            getattr(voice, "local_name", "")
            or getattr(voice, "display_name", "")
            or getattr(voice, "name", "")
        ).strip()

        if not friendly_name:
            friendly_name = cls._name_from_short_name(
                short_name
            )

        return SpeechVoice(
            short_name=short_name,
            locale=locale,
            gender=gender,
            friendly_name=friendly_name,
        ).as_dict()

    @staticmethod
    def _normalize_gender(value: Any) -> str:
        """Convert an Azure gender enum into readable text."""

        text = str(value).strip()

        if "." in text:
            text = text.rsplit(".", 1)[-1]

        if text.lower() == "male":
            return "Male"

        if text.lower() == "female":
            return "Female"

        return text or "Unknown"

    @staticmethod
    def _name_from_short_name(short_name: str) -> str:
        """Derive a readable speaker name from an Azure voice ID."""

        if not short_name:
            return "Unknown Voice"

        name_part = short_name.rsplit("-", 1)[-1]

        if name_part.lower().endswith("neural"):
            name_part = name_part[:-6]

        return name_part or short_name

    @classmethod
    def _build_ssml(
        cls,
        text: str,
        voice: str,
        rate: str,
        pitch: str,
        volume: str,
    ) -> str:
        """Build safe SSML for Azure narration synthesis."""

        locale = cls._locale_from_voice_name(voice)

        return (
            f'<speak version="1.0" '
            f'xmlns="http://www.w3.org/2001/10/synthesis" '
            f'xml:lang="{escape(locale, quote=True)}">'
            f'<voice name="{escape(voice, quote=True)}">'
            f'<prosody '
            f'rate="{escape(rate, quote=True)}" '
            f'pitch="{escape(pitch, quote=True)}" '
            f'volume="{escape(volume, quote=True)}">'
            f'{escape(text)}'
            f'</prosody>'
            f'</voice>'
            f'</speak>'
        )

    @staticmethod
    def _locale_from_voice_name(voice: str) -> str:
        """Extract the locale prefix from an Azure voice short name."""

        parts = voice.split("-")

        if len(parts) >= 2:
            return f"{parts[0]}-{parts[1]}"

        return "en-US"

    @staticmethod
    def _validate_percentage(
        value: str,
        field_name: str,
    ) -> str:
        """Validate a signed SSML percentage adjustment."""

        normalized = value.strip()

        if not normalized.endswith("%"):
            raise ValueError(
                f"Azure {field_name} must end with %."
            )

        number_text = normalized[:-1]

        try:
            numeric_value = int(number_text)
        except ValueError as error:
            raise ValueError(
                f"Azure {field_name} must be a whole-number "
                "percentage such as +0% or -10%."
            ) from error

        if not -100 <= numeric_value <= 100:
            raise ValueError(
                f"Azure {field_name} must be between "
                "-100% and +100%."
            )

        return f"{numeric_value:+d}%"

    @staticmethod
    def _validate_pitch(value: str) -> str:
        """Validate a signed SSML pitch adjustment."""

        normalized = value.strip()

        if not normalized.lower().endswith("hz"):
            raise ValueError(
                "Azure pitch must end with Hz."
            )

        number_text = normalized[:-2]

        try:
            numeric_value = int(number_text)
        except ValueError as error:
            raise ValueError(
                "Azure pitch must be a whole-number adjustment "
                "such as +0Hz or -10Hz."
            ) from error

        if not -100 <= numeric_value <= 100:
            raise ValueError(
                "Azure pitch must be between -100Hz and +100Hz."
            )

        return f"{numeric_value:+d}Hz"
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from PySide6.QtCore import QSettings

from services.application_paths import ApplicationPaths
from services.speech_engine_manager import SpeechEngineManager

try:
    import keyring
    from keyring.errors import KeyringError
except ImportError:
    keyring = None  # type: ignore[assignment]

    class KeyringError(Exception):
        """Fallback error used when keyring is unavailable."""


@dataclass(frozen=True, slots=True)
class AzureSpeechSettings:
    """Represent the saved Azure Speech configuration."""

    subscription_key: str
    region: str

    @property
    def is_configured(self) -> bool:
        """Return whether both required Azure values exist."""

        return bool(
            self.subscription_key.strip()
            and self.region.strip()
        )


class AzureSettingsService:
    """Store Azure preferences and protect the subscription key."""

    SETTINGS_FILE_NAME: Final[str] = "settings.ini"

    ENGINE_KEY: Final[str] = "speech/engine"
    AZURE_REGION_KEY: Final[str] = "speech/azure_region"

    DEFAULT_ENGINE_ID: Final[str] = (
        SpeechEngineManager.EDGE_ENGINE_ID
    )
    DEFAULT_AZURE_REGION: Final[str] = "southafricanorth"

    KEYRING_SERVICE_NAME: Final[str] = (
        "Scriptolator.AzureSpeech"
    )
    KEYRING_ACCOUNT_NAME: Final[str] = "subscription-key"

    def __init__(
        self,
        paths: ApplicationPaths | Path,
    ) -> None:
        """Create the service using Scriptolator's settings folder."""

        if isinstance(paths, ApplicationPaths):
            self.application_paths = paths
            self.settings_folder = paths.settings
        else:
            self.application_paths = None
            project_root = Path(paths).expanduser()
            self.settings_folder = project_root / "settings"

        self.settings_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.settings_path = (
            self.settings_folder / self.SETTINGS_FILE_NAME
        )
        self.settings = QSettings(
            str(self.settings_path),
            QSettings.Format.IniFormat,
        )

    def get_selected_engine(self) -> str:
        """Return the selected speech-engine identifier."""

        saved_engine = self.settings.value(
            self.ENGINE_KEY,
            self.DEFAULT_ENGINE_ID,
            type=str,
        ).strip().lower()

        if (
            saved_engine
            not in SpeechEngineManager.available_engines()
        ):
            return self.DEFAULT_ENGINE_ID

        return saved_engine

    def set_selected_engine(self, engine_id: str) -> None:
        """Store the selected speech-engine identifier."""

        normalized_engine = engine_id.strip().lower()

        if (
            normalized_engine
            not in SpeechEngineManager.available_engines()
        ):
            supported = ", ".join(
                sorted(
                    SpeechEngineManager.available_engines()
                )
            )
            raise ValueError(
                "Unsupported speech engine: "
                f"{engine_id!r}. Supported engines: {supported}."
            )

        self.settings.setValue(
            self.ENGINE_KEY,
            normalized_engine,
        )
        self.settings.sync()

    def get_azure_region(self) -> str:
        """Return the saved Azure Speech region."""

        return self.settings.value(
            self.AZURE_REGION_KEY,
            self.DEFAULT_AZURE_REGION,
            type=str,
        ).strip().lower()

    def set_azure_region(self, region: str) -> None:
        """Store the Azure Speech region."""

        normalized_region = region.strip().lower()

        if not normalized_region:
            raise ValueError(
                "An Azure Speech region is required."
            )

        self.settings.setValue(
            self.AZURE_REGION_KEY,
            normalized_region,
        )
        self.settings.sync()

    def get_azure_subscription_key(self) -> str:
        """Return the protected Azure subscription key."""

        self._require_keyring()

        try:
            saved_key = keyring.get_password(
                self.KEYRING_SERVICE_NAME,
                self.KEYRING_ACCOUNT_NAME,
            )
        except KeyringError as error:
            raise RuntimeError(
                "Windows Credential Manager could not read the "
                "Azure Speech key."
            ) from error

        return (saved_key or "").strip()

    def set_azure_subscription_key(
        self,
        subscription_key: str,
    ) -> None:
        """Protect and store the Azure subscription key."""

        self._require_keyring()

        normalized_key = subscription_key.strip()

        if not normalized_key:
            raise ValueError(
                "An Azure Speech subscription key is required."
            )

        try:
            keyring.set_password(
                self.KEYRING_SERVICE_NAME,
                self.KEYRING_ACCOUNT_NAME,
                normalized_key,
            )
        except KeyringError as error:
            raise RuntimeError(
                "Windows Credential Manager could not save the "
                "Azure Speech key."
            ) from error

    def get_azure_settings(self) -> AzureSpeechSettings:
        """Return the complete saved Azure configuration."""

        return AzureSpeechSettings(
            subscription_key=(
                self.get_azure_subscription_key()
            ),
            region=self.get_azure_region(),
        )

    def save_azure_settings(
        self,
        subscription_key: str,
        region: str,
    ) -> None:
        """Store the complete Azure Speech configuration."""

        normalized_key = subscription_key.strip()
        normalized_region = region.strip().lower()

        if not normalized_key:
            raise ValueError(
                "An Azure Speech subscription key is required."
            )

        if not normalized_region:
            raise ValueError(
                "An Azure Speech region is required."
            )

        self.set_azure_subscription_key(normalized_key)
        self.set_azure_region(normalized_region)

    def is_azure_configured(self) -> bool:
        """Return whether Azure credentials are available."""

        try:
            return self.get_azure_settings().is_configured
        except RuntimeError:
            return False

    def clear_azure_settings(self) -> None:
        """Remove the Azure key and region preference."""

        self._require_keyring()

        try:
            keyring.delete_password(
                self.KEYRING_SERVICE_NAME,
                self.KEYRING_ACCOUNT_NAME,
            )
        except keyring.errors.PasswordDeleteError:
            pass
        except KeyringError as error:
            raise RuntimeError(
                "Windows Credential Manager could not remove the "
                "Azure Speech key."
            ) from error

        self.settings.remove(self.AZURE_REGION_KEY)

        if (
            self.get_selected_engine()
            == SpeechEngineManager.AZURE_ENGINE_ID
        ):
            self.settings.setValue(
                self.ENGINE_KEY,
                self.DEFAULT_ENGINE_ID,
            )

        self.settings.sync()

    @staticmethod
    def _require_keyring() -> None:
        """Raise a clear error when keyring is unavailable."""

        if keyring is None:
            raise RuntimeError(
                "Secure Azure credential storage requires the "
                "'keyring' package."
            )
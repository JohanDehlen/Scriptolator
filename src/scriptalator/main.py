import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from main_window import MainWindow
from version import APP_NAME, APP_VERSION


def _resource_path(filename: str) -> Path:
    """Return the absolute path to a bundled application resource."""

    return Path(__file__).resolve().parent / "resources" / filename


def _load_application_icon() -> QIcon:
    """Load the Scriptolator application icon."""

    icon_path = _resource_path("scriptolator.ico")

    if not icon_path.is_file():
        return QIcon()

    return QIcon(str(icon_path))


def _create_splash_screen() -> QSplashScreen | None:
    """Create the Scriptolator splash screen when its image exists."""

    splash_path = _resource_path("scriptolator_splash.png")

    if not splash_path.is_file():
        return None

    splash_pixmap = QPixmap(str(splash_path))

    if splash_pixmap.isNull():
        return None

    splash = QSplashScreen(
        splash_pixmap,
        Qt.WindowType.WindowStaysOnTopHint,
    )
    splash.setWindowFlag(
        Qt.WindowType.FramelessWindowHint,
        True,
    )

    return splash


def main() -> None:
    """Start the Scriptolator desktop application."""

    app = QApplication(sys.argv)

    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("JohanDehlen")
    app.setDesktopFileName("Scriptolator")

    application_icon = _load_application_icon()

    if not application_icon.isNull():
        app.setWindowIcon(application_icon)

    splash = _create_splash_screen()

    if splash is not None:
        splash.show()
        app.processEvents()

    window = MainWindow()

    if not application_icon.isNull():
        window.setWindowIcon(application_icon)

    window.show()

    if splash is not None:
        splash.finish(window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
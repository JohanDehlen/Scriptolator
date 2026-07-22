from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QWidget,
)


class ScriptStatistics(QWidget):
    """Display live script length and narration-duration estimates."""

    BASE_WORDS_PER_MINUTE = 160
    MINIMUM_WORDS_PER_MINUTE = 40

    def __init__(self) -> None:
        super().__init__()

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(4)

        heading = QLabel("Script Statistics")
        heading.setStyleSheet("font-weight: bold;")

        self.charactersValue = QLabel("0")
        self.wordsValue = QLabel("0")
        self.durationValue = QLabel("0 sec")

        layout.addWidget(
            heading,
            0,
            0,
            1,
            2,
        )

        layout.addWidget(
            QLabel("Characters:"),
            1,
            0,
        )
        layout.addWidget(
            self.charactersValue,
            1,
            1,
        )

        layout.addWidget(
            QLabel("Words:"),
            2,
            0,
        )
        layout.addWidget(
            self.wordsValue,
            2,
            1,
        )

        layout.addWidget(
            QLabel("Estimated Duration:"),
            3,
            0,
        )
        layout.addWidget(
            self.durationValue,
            3,
            1,
        )

        layout.setColumnStretch(1, 1)

        self.charactersValue.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.wordsValue.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.durationValue.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

    def update_statistics(
        self,
        text: str,
        speed_adjustment: int,
    ) -> None:
        """Update character, word, and duration statistics."""

        character_count = len(text)
        word_count = len(text.split())

        estimated_seconds = self._estimate_duration_seconds(
            word_count=word_count,
            speed_adjustment=speed_adjustment,
        )

        self.charactersValue.setText(
            f"{character_count:,}"
        )
        self.wordsValue.setText(
            f"{word_count:,}"
        )
        self.durationValue.setText(
            self._format_duration(estimated_seconds)
        )

    @classmethod
    def _estimate_duration_seconds(
        cls,
        word_count: int,
        speed_adjustment: int,
    ) -> int:
        """Estimate narration length from words and speed adjustment."""

        if word_count <= 0:
            return 0

        effective_words_per_minute = round(
            cls.BASE_WORDS_PER_MINUTE
            * (1 + speed_adjustment / 100)
        )

        effective_words_per_minute = max(
            cls.MINIMUM_WORDS_PER_MINUTE,
            effective_words_per_minute,
        )

        estimated_minutes = (
            word_count / effective_words_per_minute
        )

        return max(
            1,
            round(estimated_minutes * 60),
        )

    @staticmethod
    def _format_duration(total_seconds: int) -> str:
        """Format seconds as a natural duration string."""

        if total_seconds <= 0:
            return "0 sec"

        hours, remaining_seconds = divmod(
            total_seconds,
            3600,
        )
        minutes, seconds = divmod(
            remaining_seconds,
            60,
        )

        if hours:
            if minutes:
                return f"{hours} hr {minutes} min"

            return f"{hours} hr"

        if minutes:
            if seconds:
                return f"{minutes} min {seconds} sec"

            return f"{minutes} min"

        return f"{seconds} sec"
from enum import Enum


class TsukiState(str, Enum):
    STANDBY = "standby"
    ACTIVE = "active"
    PROCESSING = "processing"


class TsukiRuntime:
    """Estado de execução independente da interface (terminal, voz, API)."""

    TURN_ON_PHRASE = "tsuki turn on"
    TURN_OFF_PHRASE = "tsuki turn off"

    def __init__(self):
        self.state = TsukiState.STANDBY

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.lower().strip().split())

    def handle_control_phrase(self, text: str) -> str | None:
        normalized = self._normalize(text)

        if normalized == self.TURN_ON_PHRASE:
            self.state = TsukiState.ACTIVE
            return "activated"

        if normalized == self.TURN_OFF_PHRASE:
            self.state = TsukiState.STANDBY
            return "deactivated"

        return None

    @property
    def is_active(self) -> bool:
        return self.state == TsukiState.ACTIVE

    def begin_processing(self) -> None:
        if self.is_active:
            self.state = TsukiState.PROCESSING

    def finish_processing(self) -> None:
        if self.state == TsukiState.PROCESSING:
            self.state = TsukiState.ACTIVE

from app.core.runtime import TsukiRuntime


class TsukiCoordinator:
    """Orquestra entradas do Tsuki sem acoplar o Core à interface."""

    def __init__(self, assistant, runtime: TsukiRuntime | None = None):
        self.assistant = assistant
        self.runtime = runtime or TsukiRuntime()

    def handle(self, text: str, require_active: bool = False) -> str | None:
        text = text.strip()
        if not text:
            return None

        control = self.runtime.handle_control_phrase(text)
        if control == "activated":
            return "Tsuki ativada."
        if control == "deactivated":
            return "Tsuki em standby."

        if require_active and not self.runtime.is_active:
            return None

        was_active = self.runtime.is_active
        if was_active:
            self.runtime.begin_processing()

        try:
            return self.assistant.process_message(text)
        finally:
            if was_active:
                self.runtime.finish_processing()

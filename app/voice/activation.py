from app.core.runtime import TsukiRuntime


class VoiceActivation:
    """Interpreta somente frases de controle; não depende do STT escolhido."""

    def __init__(self, runtime: TsukiRuntime):
        self.runtime = runtime

    def consume(self, transcript: str) -> str | None:
        return self.runtime.handle_control_phrase(transcript)

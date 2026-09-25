import os
import tempfile
import wave

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


class VoiceTranscriber:
    """Captura o microfone e transcreve localmente com faster-whisper."""

    def __init__(
        self,
        model_size: str = "base",
        language: str = "pt",
        sample_rate: int = 16000,
        silence_seconds: float = 1.2,
        max_seconds: float = 12.0,
    ):
        self.sample_rate = sample_rate
        self.language = language
        self.initial_prompt = "Tsuki. Tsuki Turn On. Tsuki Turn Off. Assistente virtual Tsuki, comandos em português do Brasil."
        self.silence_seconds = silence_seconds
        self.max_seconds = max_seconds
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def listen(self) -> str:
        block_seconds = 0.25
        block_size = int(self.sample_rate * block_seconds)
        max_blocks = int(self.max_seconds / block_seconds)
        silence_blocks_needed = max(1, int(self.silence_seconds / block_seconds))
        frames = []
        speech_started = False
        silent_blocks = 0
        ambient = []

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            blocksize=block_size,
        ) as stream:
            for index in range(max_blocks):
                data, overflowed = stream.read(block_size)
                if overflowed:
                    continue

                mono = data[:, 0].copy()
                rms = float(np.sqrt(np.mean(np.square(mono)))) if mono.size else 0.0

                if index < 4 and not speech_started:
                    ambient.append(rms)
                    frames.append(mono)
                    continue

                ambient_level = (sum(ambient) / len(ambient)) if ambient else 0.005
                threshold = max(0.012, ambient_level * 3.0)

                if rms >= threshold:
                    speech_started = True
                    silent_blocks = 0
                elif speech_started:
                    silent_blocks += 1

                frames.append(mono)

                if speech_started and silent_blocks >= silence_blocks_needed:
                    break

        if not speech_started or not frames:
            return ""

        audio = np.concatenate(frames)
        return self._transcribe(audio)

    def _transcribe(self, audio: np.ndarray) -> str:
        fd, path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)

        try:
            pcm = np.clip(audio, -1.0, 1.0)
            pcm = (pcm * 32767).astype(np.int16)

            with wave.open(path, "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(self.sample_rate)
                wav.writeframes(pcm.tobytes())

            segments, _ = self.model.transcribe(
                path,
                language=self.language,
                initial_prompt=self.initial_prompt,
                vad_filter=True,
                beam_size=1,
            )
            return " ".join(segment.text.strip() for segment in segments).strip()
        finally:
            if os.path.exists(path):
                os.remove(path)

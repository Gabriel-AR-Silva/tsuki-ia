import time

import requests

from config import OLLAMA_MODEL, OLLAMA_URL


class OllamaClient:

    def __init__(
        self,
        base_url: str = OLLAMA_URL,
        model: str = OLLAMA_MODEL,
    ):
        self.base_url = base_url
        self.model = model

    def chat(
        self,
        messages: list[dict],
        tools=None
    ) -> dict:

        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "keep_alive": -1,

            # Controla a geração do Qwen.
            "options": {
                # Evita respostas enormes para
                # perguntas simples.
                "num_predict": 120,

                # Reduz variações desnecessárias.
                "temperature": 0.2,
            }
        }

        if tools:
            payload["tools"] = tools

        started_at = time.perf_counter()

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=120,
            )

            response.raise_for_status()

        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError(
                "Não consegui conectar ao Ollama. "
                "Confirme se ele está instalado e em execução."
            ) from exc

        except requests.exceptions.Timeout as exc:
            raise RuntimeError(
                f"O modelo {self.model} demorou mais "
                "de 120 segundos para responder."
            ) from exc

        except requests.exceptions.HTTPError as exc:
            raise RuntimeError(
                f"Ollama retornou erro HTTP: "
                f"{response.text}"
            ) from exc

        http_duration = (
            time.perf_counter()
            - started_at
        )

        data = response.json()

        message = data.get(
            "message",
            {}
        )

        if not message:
            raise RuntimeError(
                "O modelo não retornou uma mensagem."
            )

        data["_tsuki_http_duration"] = (
            http_duration
        )

        return data

    def warm_up(self) -> float:
        """
        Carrega o modelo no Ollama e mantém
        ele carregado na memória.
        """

        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": [],
            "stream": False,
            "keep_alive": -1,
        }

        started_at = time.perf_counter()

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=120,
            )

            response.raise_for_status()

        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError(
                "Não consegui conectar ao Ollama."
            ) from exc

        except requests.exceptions.Timeout as exc:
            raise RuntimeError(
                f"O modelo {self.model} demorou demais "
                "para ser preparado."
            ) from exc

        except requests.exceptions.HTTPError as exc:
            raise RuntimeError(
                f"Ollama retornou erro HTTP: "
                f"{response.text}"
            ) from exc

        return (
            time.perf_counter()
            - started_at
        )
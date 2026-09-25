from app.assistant_service import AssistantService
from app.core.coordinator import TsukiCoordinator
from app.voice.transcriber import VoiceTranscriber


def main():
    print("Inicializando Tsuki Voice...")
    assistant = AssistantService()
    coordinator = TsukiCoordinator(assistant)
    transcriber = VoiceTranscriber()

    print("Microfone ativo.")
    print("Diga 'Tsuki Turn On' para ativar e 'Tsuki Turn Off' para voltar ao standby.")
    print("Ctrl+C encerra o processo.")

    while True:
        try:
            transcript = transcriber.listen()
        except KeyboardInterrupt:
            print("\nTsuki Voice encerrado.")
            break
        except Exception as exc:
            print(f"Erro no microfone/transcrição: {exc}")
            continue

        if not transcript:
            continue

        print(f"Você (voz) > {transcript}")

        try:
            response = coordinator.handle(transcript, require_active=True)
        except Exception as exc:
            print(f"Tsuki > Erro: {exc}")
            continue

        if response:
            print(f"Tsuki > {response}\n")


if __name__ == "__main__":
    main()

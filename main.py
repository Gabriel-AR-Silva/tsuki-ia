from app.assistant_service import AssistantService
from app.core.coordinator import TsukiCoordinator


HELP_TEXT = """
Comandos:
  /help                     mostra esta ajuda
  /memories                 lista todas as memórias
  /remember <texto>         salva uma memória
  /search <texto>           procura memórias
  /forget <id>              apaga uma memória
  /exit                     encerra o Tsuki
"""


def main():
    # AssistantService aquece o modelo na inicialização.
    assistant = AssistantService()
    coordinator = TsukiCoordinator(assistant)

    print("Tsuki Core iniciado.")
    print("Terminal disponível. Voz permanece em standby até 'Tsuki Turn On'.")

    while True:
        try:
            message = input("Você > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nTsuki > Encerrando.")
            break

        if not message:
            continue

        if message.lower() == "/exit":
            print("Tsuki > Até mais.")
            break

        if message.lower() == "/help":
            print(HELP_TEXT)
            continue

        try:
            # Terminal não exige ativação por voz. Ele usa o mesmo Core,
            # mas continua disponível mesmo com a escuta em standby.
            response = coordinator.handle(message, require_active=False)
            if response:
                print(f"Tsuki > {response}\n")
        except Exception as exc:
            print(f"Tsuki > Erro: {exc}\n")


if __name__ == "__main__":
    main()

from app.assistant_service import AssistantService


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
    assistant = AssistantService()

    print("Tsuki MVP iniciado.")

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
            response = assistant.process_message(message)
            print(f"Tsuki > {response}\n")
        except Exception as exc:
            print(f"Tsuki > Erro: {exc}\n")


if __name__ == "__main__":
    main()

import json
import time

from app.llm.ollama_client import OllamaClient
from app.memory.repository import MemoryRepository
from app.tools.memory_tools import MemoryTools
from app.actions.action_registry import ACTIONS
from app.tools.tools import TOOLS, TOOL_FUNCTIONS


SYSTEM_PROMPT = """
Você é Tsuki, uma assistente pessoal local.

REGRAS:
- Responda sempre em português brasileiro.
- Seja breve e direta.
- Não invente informações.
- Não explique seu funcionamento interno.
- Não diga que uma ferramenta não foi necessária.
- Não mencione Tools, funções, JSON ou memória ao usuário.
- Para perguntas simples, responda em poucas frases.

FERRAMENTAS:
Quando uma ferramenta disponível puder executar diretamente
o pedido do usuário, utilize essa ferramenta.

MEMÓRIA:
Só salve informações pessoais do usuário que sejam úteis
em conversas futuras.

Exemplos do que pode ser salvo:
- objetivos do usuário;
- projetos do usuário;
- preferências;
- decisões;
- planos;
- rotinas;
- mudanças de prioridade.

NÃO salve:
- perguntas de conhecimento geral;
- assuntos que o usuário apenas perguntou;
- explicações;
- respostas da assistente;
- cumprimentos;
- informações temporárias.

Exemplo:

Usuário:
"O que é Laravel?"

Isso NÃO é memória.

Usuário:
"Estou desenvolvendo meu sistema usando Laravel."

Isso PODE ser memória.

Quando não utilizar uma ferramenta,
retorne SOMENTE JSON válido:

{
    "response": "resposta curta ao usuário",
    "should_save": false,
    "memory": null
}

Quando houver uma informação realmente útil
para memória:

{
    "response": "resposta ao usuário",
    "should_save": true,
    "memory": "fato curto e objetivo sobre o usuário"
}

Nunca crie listas ou objetos dentro de "memory".
"memory" deve ser somente uma string curta ou null.
"""


class AssistantService:

    def __init__(self):

        self.llm = OllamaClient(
            model="qwen3:1.7b"
        )

        print("Preparando Qwen 1.7B...")

        try:
            warm_up_time = self.llm.warm_up()

            print(
                f"Qwen 1.7B pronto "
                f"({warm_up_time:.2f}s)."
            )

        except Exception as exc:
            print(
                f"Não foi possível preparar o Qwen: {exc}"
            )

        self.memory_repository = (
            MemoryRepository()
        )

        self.memory_tools = MemoryTools(
            self.memory_repository
        )

    def process_message(
        self,
        message: str
    ) -> str:

        total_started_at = (
            time.perf_counter()
        )

        message = message.strip()

        if not message:
            return "Digite alguma coisa."

        # =============================================
        # COMANDOS INTERNOS
        # =============================================

        command_response = self._try_command(
            message
        )

        if command_response is not None:
            return command_response

        # =============================================
        # AÇÕES DIRETAS
        # =============================================

        for action_name, action in ACTIONS.items():

            aliases = action["aliases"]

            normalized_aliases = [
                alias.lower()
                for alias in aliases
            ]

            if message.lower() in normalized_aliases:

                tool_started_at = (
                    time.perf_counter()
                )

                try:
                    result = action["handler"]()

                except Exception as exc:
                    return (
                        f"Erro ao executar "
                        f"'{action_name}': {exc}"
                    )

                tool_duration = (
                    time.perf_counter()
                    - tool_started_at
                )

                total_duration = (
                    time.perf_counter()
                    - total_started_at
                )

                performance = (
                    self._format_performance(
                        memory_duration=0.0,
                        ollama_data=None,
                        tool_duration=tool_duration,
                        total_duration=total_duration
                    )
                )

                return (
                    f"{result}\n\n"
                    f"{performance}"
                )

        # =============================================
        # MEMÓRIA
        # =============================================

        memory_started_at = (
            time.perf_counter()
        )

        memories = self.memory_tools.search(
            message,
            limit=5
        )

        memory_duration = (
            time.perf_counter()
            - memory_started_at
        )

        memory_context = (
            self._format_memories(
                memories
            )
        )

        # =============================================
        # MENSAGENS PARA O QWEN
        # =============================================

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "system",
                "content": (
                    "Memórias relevantes do usuário:\n"
                    + memory_context
                )
            },
            {
                "role": "user",
                "content": message
            }
        ]

        # =============================================
        # QWEN
        # =============================================

        try:
            raw_response = self.llm.chat(
                messages,
                tools=TOOLS
            )

        except Exception as exc:
            return (
                f"Erro ao consultar o modelo: {exc}"
            )

        qwen_message = raw_response.get(
            "message",
            {}
        )

        # =============================================
        # TOOL CALL
        # =============================================

        tool_calls = qwen_message.get(
            "tool_calls",
            []
        )

        if tool_calls:

            tool_started_at = (
                time.perf_counter()
            )

            result = self._execute_tool(
                tool_calls[0]
            )

            tool_duration = (
                time.perf_counter()
                - tool_started_at
            )

            total_duration = (
                time.perf_counter()
                - total_started_at
            )

            performance = (
                self._format_performance(
                    memory_duration=memory_duration,
                    ollama_data=raw_response,
                    tool_duration=tool_duration,
                    total_duration=total_duration
                )
            )

            return (
                f"{result}\n\n"
                f"{performance}"
            )

        # =============================================
        # RESPOSTA NORMAL
        # =============================================

        raw_text = qwen_message.get(
            "content",
            ""
        ).strip()

        if not raw_text:
            return (
                "O modelo não retornou uma resposta."
            )

        result = self._parse_ai_response(
            raw_text
        )

        response_text = result.get(
            "response",
            ""
        )

        should_save = result.get(
            "should_save",
            False
        )

        memory = result.get(
            "memory"
        )

        # Segurança adicional:
        # memória precisa obrigatoriamente ser string.
        if not isinstance(memory, str):
            memory = None
            should_save = False

        # =============================================
        # SALVAR MEMÓRIA
        # =============================================

        if should_save and memory:

            save_started_at = (
                time.perf_counter()
            )

            memory_id = (
                self.memory_tools.remember(
                    memory
                )
            )

            save_duration = (
                time.perf_counter()
                - save_started_at
            )

            memory_duration += (
                save_duration
            )

            response_text += (
                f"\n\n"
                f"[Memória {memory_id} salva: "
                f"{memory}]"
            )

        else:

            response_text += (
                "\n\n"
                "[Nenhuma memória nova foi necessária.]"
            )

        # =============================================
        # PERFORMANCE
        # =============================================

        total_duration = (
            time.perf_counter()
            - total_started_at
        )

        performance = (
            self._format_performance(
                memory_duration=memory_duration,
                ollama_data=raw_response,
                tool_duration=0.0,
                total_duration=total_duration
            )
        )

        response_text += (
            f"\n\n{performance}"
        )

        return response_text

    # ================================================
    # PERFORMANCE
    # ================================================

    def _format_performance(
        self,
        memory_duration: float,
        ollama_data,
        tool_duration: float,
        total_duration: float
    ) -> str:

        lines = [
            "[PERFORMANCE]"
        ]

        lines.append(
            f"Memória SQLite: "
            f"{memory_duration:.3f}s"
        )

        if ollama_data:

            http_duration = ollama_data.get(
                "_tsuki_http_duration",
                0
            )

            load_duration = (
                self._ns_to_seconds(
                    ollama_data.get(
                        "load_duration",
                        0
                    )
                )
            )

            prompt_duration = (
                self._ns_to_seconds(
                    ollama_data.get(
                        "prompt_eval_duration",
                        0
                    )
                )
            )

            eval_duration = (
                self._ns_to_seconds(
                    ollama_data.get(
                        "eval_duration",
                        0
                    )
                )
            )

            ollama_total = (
                self._ns_to_seconds(
                    ollama_data.get(
                        "total_duration",
                        0
                    )
                )
            )

            prompt_tokens = ollama_data.get(
                "prompt_eval_count",
                0
            )

            output_tokens = ollama_data.get(
                "eval_count",
                0
            )

            lines.append(
                f"Ollama HTTP: "
                f"{http_duration:.3f}s"
            )

            lines.append(
                f"Ollama total: "
                f"{ollama_total:.3f}s"
            )

            lines.append(
                f"  Carregar modelo: "
                f"{load_duration:.3f}s"
            )

            lines.append(
                f"  Processar prompt: "
                f"{prompt_duration:.3f}s"
            )

            lines.append(
                f"  Gerar resposta: "
                f"{eval_duration:.3f}s"
            )

            lines.append(
                f"Tokens entrada: "
                f"{prompt_tokens}"
            )

            lines.append(
                f"Tokens saída: "
                f"{output_tokens}"
            )

            if (
                eval_duration > 0
                and output_tokens
            ):

                tokens_per_second = (
                    output_tokens
                    / eval_duration
                )

                lines.append(
                    f"Velocidade geração: "
                    f"{tokens_per_second:.2f} "
                    f"tokens/s"
                )

        if tool_duration > 0:

            lines.append(
                f"Tool Python: "
                f"{tool_duration:.3f}s"
            )

        lines.append(
            f"Total Tsuki: "
            f"{total_duration:.3f}s"
        )

        return "\n".join(
            lines
        )

    def _ns_to_seconds(
        self,
        value
    ) -> float:

        if not value:
            return 0.0

        return (
            value
            / 1_000_000_000
        )

    # ================================================
    # EXECUTAR TOOL
    # ================================================

    def _execute_tool(
        self,
        tool_call
    ):

        function_data = tool_call.get(
            "function",
            {}
        )

        tool_name = function_data.get(
            "name"
        )

        arguments = function_data.get(
            "arguments",
            {}
        )

        if not tool_name:
            return (
                "A Tool não informou uma função."
            )

        if tool_name not in TOOL_FUNCTIONS:
            return (
                f"A ferramenta '{tool_name}' "
                "não está registrada."
            )

        function = TOOL_FUNCTIONS[
            tool_name
        ]

        if isinstance(
            arguments,
            str
        ):

            try:
                arguments = json.loads(
                    arguments
                )

            except json.JSONDecodeError:
                arguments = {}

        if not isinstance(
            arguments,
            dict
        ):
            arguments = {}

        try:

            return function(
                **arguments
            )

        except TypeError:

            try:
                return function()

            except Exception as exc:
                return (
                    f"Erro ao executar "
                    f"'{tool_name}': {exc}"
                )

        except Exception as exc:

            return (
                f"Erro ao executar "
                f"'{tool_name}': {exc}"
            )

    # ================================================
    # COMANDOS INTERNOS
    # ================================================

    def _try_command(
        self,
        message: str
    ):

        if message == "/memories":

            memories = (
                self.memory_tools.list_all()
            )

            if not memories:
                return (
                    "Nenhuma memória salva."
                )

            lines = []

            for memory in memories:

                lines.append(
                    f"[{memory['id']}] "
                    f"{memory['content']}"
                )

            return "\n".join(
                lines
            )

        if message == "/remember":

            return (
                "Uso: /remember "
                "alguma informação"
            )

        if message.startswith(
            "/remember "
        ):

            content = message[
                len("/remember "):
            ].strip()

            if not content:

                return (
                    "Uso: /remember "
                    "alguma informação"
                )

            memory_id = (
                self.memory_tools.remember(
                    content
                )
            )

            return (
                f"Memória {memory_id} salva."
            )

        if message == "/search":

            return (
                "Uso: /search alguma coisa"
            )

        if message.startswith(
            "/search "
        ):

            query = message[
                len("/search "):
            ].strip()

            if not query:

                return (
                    "Uso: /search "
                    "alguma coisa"
                )

            memories = (
                self.memory_tools.search(
                    query,
                    limit=10
                )
            )

            if not memories:

                return (
                    "Nenhuma memória encontrada."
                )

            lines = []

            for memory in memories:

                lines.append(
                    f"[{memory['id']}] "
                    f"{memory['content']}"
                )

            return "\n".join(
                lines
            )

        if message == "/forget":

            return (
                "Uso: /forget ID"
            )

        if message.startswith(
            "/forget "
        ):

            memory_id = message[
                len("/forget "):
            ].strip()

            if not memory_id.isdigit():

                return (
                    "Uso: /forget ID"
                )

            deleted = (
                self.memory_tools.forget(
                    int(memory_id)
                )
            )

            if deleted:

                return (
                    f"Memória {memory_id} "
                    "removida."
                )

            return (
                f"Memória {memory_id} "
                "não encontrada."
            )

        return None

    # ================================================
    # FORMATAR MEMÓRIAS
    # ================================================

    def _format_memories(
        self,
        memories
    ) -> str:

        if not memories:

            return (
                "Nenhuma memória relevante."
            )

        lines = []

        for memory in memories:

            lines.append(
                f"- {memory['content']}"
            )

        return "\n".join(
            lines
        )

    # ================================================
    # INTERPRETAR RESPOSTA
    # ================================================

    def _parse_ai_response(
        self,
        raw_response: str
    ) -> dict:

        raw_response = (
            raw_response.strip()
        )

        if raw_response.startswith(
            "```"
        ):

            raw_response = (
                raw_response.replace(
                    "```json",
                    ""
                )
            )

            raw_response = (
                raw_response.replace(
                    "```",
                    ""
                )
            )

            raw_response = (
                raw_response.strip()
            )

        try:

            data = json.loads(
                raw_response
            )

            return {
                "response": data.get(
                    "response",
                    ""
                ),
                "should_save": data.get(
                    "should_save",
                    False
                ),
                "memory": data.get(
                    "memory"
                )
            }

        except json.JSONDecodeError:

            return {
                "response": raw_response,
                "should_save": False,
                "memory": None
            }''
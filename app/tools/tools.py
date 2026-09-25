from app.actions.project_actions import open_finansys


OPEN_FINANSYS_TOOL = {
    "type": "function",

    "function": {
        "name": "open_finansys",

        "description": (
            "Abre e inicia o sistema financeiro pessoal FinanSys "
            "do usuário no computador. "
            "Use esta ferramenta sempre que o usuário quiser abrir, "
            "acessar, visualizar ou entrar no sistema financeiro, "
            "FinanSys, suas finanças, seu dinheiro, seus gastos, "
            "movimentações financeiras ou informações financeiras "
            "que ficam no sistema."
        ),

        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}


TOOLS = [
    OPEN_FINANSYS_TOOL
]


TOOL_FUNCTIONS = {
    "open_finansys": open_finansys
}
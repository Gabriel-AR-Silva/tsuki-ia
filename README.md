# Tsuki MVP

Um assistente pessoal local, simples e didático, feito para estudar arquitetura de aplicações com IA.

## O que esta versão faz

- roda no terminal;
- conversa com um modelo local via Ollama;
- salva memórias em SQLite;
- lista memórias;
- busca memórias por texto;
- permite apagar uma memória pelo ID;
- injeta memórias relevantes no contexto antes de responder;
- mantém as responsabilidades separadas por arquivo.

## Arquitetura

```text
Você
  ↓
main.py
  ↓
AssistantService
  ├── MemoryRepository → SQLite
  └── OllamaClient → Ollama → modelo local
```

## Estrutura

```text
tsuki_mvp/
├── main.py
├── config.py
├── requirements.txt
├── .env.example
└── app/
    ├── assistant_service.py
    ├── llm/
    │   └── ollama_client.py
    ├── memory/
    │   ├── database.py
    │   └── repository.py
    └── tools/
        └── memory_tools.py
```

## 1. Instale Python

Use Python 3.11+.

No terminal:

```bash
python --version
```

## 2. Crie o ambiente virtual

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

## 3. Instale as dependências

```bash
pip install -r requirements.txt
```

## 4. Instale e inicie o Ollama

Depois de instalar o Ollama, baixe um modelo pequeno:

```bash
ollama pull qwen3:4b
```

Teste:

```bash
ollama run qwen3:4b
```

Se seu computador tiver pouca memória, experimente:

```bash
ollama pull qwen3:1.7b
```

## 5. Configure

Copie:

```text
.env.example
```

para:

```text
.env
```

Por padrão:

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
```

## 6. Rode

```bash
python main.py
```

## Comandos especiais

```text
/help
/memories
/remember alguma informação
/search palavra
/forget 3
/exit
```

Exemplos:

```text
Você > /remember Meu projeto principal é o Tsuki.
Você > /memories
Você > /search Tsuki
Você > /forget 1
```

Também existe memória automática simples. Ao escrever:

```text
lembre que minha prioridade é estudar Python
```

o Tsuki salva essa informação antes de continuar.

## Como estudar este projeto

Sugestão de ordem:

1. `main.py`
2. `app/assistant_service.py`
3. `app/tools/memory_tools.py`
4. `app/memory/repository.py`
5. `app/memory/database.py`
6. `app/llm/ollama_client.py`
7. `config.py`

Sempre siga uma mensagem pelo sistema.

Exemplo:

```text
main.py
→ AssistantService.process_message()
→ MemoryTools.search()
→ MemoryRepository.search()
→ banco SQLite
→ OllamaClient.chat()
→ resposta
```

## O que NÃO está nesta versão

Intencionalmente:

- Vue;
- FastAPI;
- voz;
- embeddings;
- banco vetorial;
- agentes autônomos;
- n8n;
- MCP;
- controle geral do Windows.

Essas partes devem entrar só depois que esta base estiver clara.

## Próximas versões sugeridas

### v0.2
FastAPI + endpoint `/chat`.

### v0.3
Vue 3.

### v0.4
tool calling real, em vez de regras fixas.

### v0.5
embeddings + busca semântica.

### v0.6
voz.

### v0.7
integrações e ferramentas locais controladas.

# 🛠️ Advanced Tool Use: Anthropic's Context Engineering Patterns

A practical implementation of **Anthropic's Advanced Tool Use** patterns using LangChain v1.

> 📖 Based on [Anthropic Engineering Blog: Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use)

---

## 🎯 What This Demonstrates

This project implements the **3 key patterns** from Anthropic's blog for building production-ready AI agents:

| Concept | Problem It Solves | Implementation |
|---------|------------------|----------------|
| **Tool Search Tool** | Context bloat from 100s of tools | `defer_loading` flag + similarity search |
| **Programmatic Tool Calling** | Intermediate results polluting context | `run_python` tool for orchestration |
| **Tool Use Examples** | Parameter format errors | `examples` field in tool metadata |

### Results from Anthropic's Testing:
- **85%** token reduction with Tool Search
- **37%** token reduction with Programmatic Tool Calling  
- **72% → 90%** accuracy with Tool Use Examples

---

## 📁 Project Structure

```
tools_context_engineering/
├── demo_agent.py      # Main implementation with all 3 patterns
├── LEARNING_GUIDE.md  # Detailed documentation mapping blog → code
├── requirements.txt   # Dependencies
├── .env               # Your API keys (not committed)
└── README.md          # This file
```

---

## 🚀 Quickstart

### 1. Install Dependencies

```bash
cd tools_context_engineering
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set Your API Key

```bash
export OPENAI_API_KEY="sk-..."
# Or add to .env file
```

### 3. Run the Agent

```bash
# Simple query
python demo_agent.py --query "What is the weather in Tokyo?"

# Complex multi-tool query
python demo_agent.py --query "Find GitHub repos about RAG and compare SF vs NYC weather"

# Adjust tool selection (Concept 1)
python demo_agent.py --query "Convert USD to EUR" --top-k 2
```

---

## 📖 The 3 Concepts Explained

### Concept 1: Tool Search Tool

**Problem**: Loading 50+ tools = 55K+ tokens before work begins.

**Solution**: Mark tools as `defer_loading=True` and discover on-demand.

```python
# Always-loaded (critical tools)
duck = ToolSpec(name="search", defer_loading=False)

# Deferred (loaded when query matches)
weather = ToolSpec(name="weather", defer_loading=True)
```

**Output shows tool selection:**
```
CONCEPT 1: Tool Search Tool - Selected tools for this query:
  [ALWAYS] duckduckgo_search
  [MATCHED] open_meteo_weather  ← Only loaded for weather queries!
```

---

### Concept 2: Programmatic Tool Calling

**Problem**: Each tool call = inference pass + results bloat context.

**Solution**: Let model write Python code to orchestrate workflows.

```python
@tool
def run_python(code: str) -> str:
    """Execute code - only final output enters context."""
    exec(code)
    return output  # 2000 records → 3 names
```

---

### Concept 3: Tool Use Examples

**Problem**: JSON schemas can't show format patterns.

**Solution**: Provide example invocations.

```python
weather = ToolSpec(
    name="weather",
    examples=[
        "get_weather('San Francisco')",  # Shows: city name format
        "get_weather('Tokyo')"           # Shows: international OK
    ]
)
```

---

## 🛠️ Available Tools

| Tool | Description | Always Loaded? |
|------|-------------|----------------|
| `duckduckgo_search` | Web search | ✅ Yes |
| `wikipedia` | Encyclopedia lookup | ✅ Yes |
| `open_meteo_weather` | Weather forecasts | No (matched) |
| `github_repo_search` | GitHub repos by stars | No (matched) |
| `fx_rate` | Currency conversion | No (matched) |
| `http_get` | Fetch URLs | No (matched) |
| `run_python` | Execute Python code | No (matched) |

---

## 📚 Learn More

- **[LEARNING_GUIDE.md](./LEARNING_GUIDE.md)** - Deep dive into each concept with code references
- **[Anthropic Blog](https://www.anthropic.com/engineering/advanced-tool-use)** - Original source

---

## 🔧 Tech Stack

- **LangChain v1.2+** - Modern `create_agent` API
- **Python 3.10+**
- **OpenAI GPT-4o-mini** (default, configurable)

---

## 📝 License

MIT License - See [LICENSE](../LICENSE) for details.

---

*Built to learn and demonstrate Anthropic's context engineering patterns for production AI agents.*

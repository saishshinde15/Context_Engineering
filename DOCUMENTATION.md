# 📝 Context Offloading with CrewAI - Complete Documentation

## Overview

This project demonstrates **Context Offloading**, a context engineering technique that stores information **outside** the LLM's context window to avoid context rot and enable information reuse across tasks.

### What is Context Offloading?

**Context Offloading** = Storing information in external persistent storage (scratchpad, file system, database) rather than keeping everything in the LLM's context window.

**Key Benefits:**
- **Avoids Context Rot**: Information buried deep in context loses accuracy (Chroma's research)
- **Enables Reusability**: Information can be retrieved multiple times
- **Supports Long Tasks**: Complex multi-step tasks can persist state
- **Cross-Session Memory**: Information survives beyond single conversations

## Architecture

This implementation uses a **3-agent sequential workflow** with a **persistent scratchpad**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTEXT OFFLOADING FLOW                      │
└─────────────────────────────────────────────────────────────────┘

1. RESEARCH PLANNER AGENT
   ├── Read user preferences (from knowledge/user_preference.txt)
   ├── Check scratchpad for existing info
   ├── Create detailed research plan
   └── SAVE PLAN TO SCRATCHPAD (category: 'research_plan')
         │
         ▼
2. RESEARCHER AGENT
   ├── READ PLAN FROM SCRATCHPAD
   ├── Conduct web searches (Tavily)
   ├── WRITE FINDINGS TO SCRATCHPAD (category: 'findings')
   ├── Iterate: search → update scratchpad → search
   └── WRITE SUMMARY TO SCRATCHPAD (category: 'summary')
         │
         ▼
3. SYNTHESIS AGENT
   ├── READ ALL SCRATCHPAD NOTES (all categories)
   ├── Synthesize: plan + findings + summary + user preferences
   └── Generate comprehensive report (report.md)
```

### Key Implementation Details

**Scratchpad Tools:**
- `scratchpad_write`: Save notes to persistent JSON file (organized by category)
- `scratchpad_read`: Retrieve notes from scratchpad (by category or all)
- `read_user_preferences`: Load user requirements from knowledge base

**Storage:**
- `knowledge/scratchpad.json`: Persistent scratchpad (cleared each run)
- `knowledge/user_preference.txt`: User preferences (persistent)

**LLM:**
- Google Gemini 1.5 Flash (`gemini/gemini-1.5-flash-latest`)

## Installation

### Prerequisites
- Python >=3.10, <3.14
- UV package manager
- Google Gemini API key
- Tavily API key (for web search)

### Setup

1. **Install UV** (if not already installed):
```bash
pip install uv
```

2. **Navigate to project directory**:
```bash
cd context_offloading
```

3. **Install dependencies**:
```bash
crewai install
```

4. **Configure environment variables**:

Create a `.env` file in the project root:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

**Get API Keys:**
- Gemini: https://aistudio.google.com/app/apikey
- Tavily: https://tavily.com/ (free tier available)

## Usage

### Run the Crew

From the project root:

```bash
crewai run
```

This will execute the default query comparing Commonwealth Fusion Systems vs Helion Energy.

### Customize the Research Topic

Edit `src/context_offloading/main.py` and modify the `inputs` dictionary:

```python
inputs = {
    'topic': 'Your research question here',
    'current_year': str(datetime.now().year)
}
```

### Customize User Preferences

Edit `knowledge/user_preference.txt` to change research requirements, depth, and output style.

## How It Works

### 1. Planning Phase

The **Research Planner Agent** creates a structured research plan:
- Reads user preferences to understand requirements
- Checks scratchpad for any existing context
- Creates detailed plan with objectives, questions, methodology
- **Saves plan to scratchpad** (category: `research_plan`)

### 2. Research Phase

The **Researcher Agent** conducts iterative research:
- **Reads research plan from scratchpad**
- Performs web searches using Tavily
- After each search, **writes findings to scratchpad** (category: `findings`)
- This creates an **audit trail** and **avoids context rot**
- Finally writes a **summary to scratchpad** (category: `summary`)

### 3. Synthesis Phase

The **Synthesis Agent** creates the final report:
- **Reads ALL scratchpad notes** (plan, findings, summary)
- Also considers user preferences
- Synthesizes everything into a comprehensive, well-structured report
- Saves to `report.md`

## Key Concepts Demonstrated

### Context Rot Mitigation
By offloading information to the scratchpad, we prevent information from being "buried" deep in the context window where accuracy degrades.

### Recitation Effect
Re-writing information to the scratchpad effectively pushes it to the **end** of the context window in subsequent reads, improving model performance (Manus discovery).

### Persistent Memory
The scratchpad persists across agent turns, enabling:
- Information sharing between agents
- Building upon previous work
- Creating an audit trail of agent reasoning

### Structured Workflows
The explicit workflow guidance in task descriptions creates systematic context offloading behavior.

## Project Structure

```
context_offloading/
├── src/
│   └── context_offloading/
│       ├── config/
│       │   ├── agents.yaml          # Agent definitions
│       │   └── tasks.yaml           # Task definitions
│       ├── tools/
│       │   └── custom_tool.py       # Scratchpad tools
│       ├── crew.py                  # Crew orchestration
│       └── main.py                  # Entry point
├── knowledge/
│   ├── user_preference.txt          # User requirements
│   └── scratchpad.json              # Persistent scratchpad (auto-created)
├── report.md                        # Generated report (output)
├── pyproject.toml                   # Dependencies
├── README.md                        # Quick start
└── DOCUMENTATION.md                 # This file
```

## Comparison with Context Pruning

| Aspect | Context Pruning | Context Offloading |
|--------|----------------|-------------------|
| **Goal** | Remove irrelevant info | Move info externally |
| **Token Impact** | Reduces tokens | Neutral (moves tokens) |
| **Use Case** | Noisy context | Multi-step tasks |
| **Persistence** | None | Cross-session capable |
| **Information Loss** | Intentional (prune) | None (retrieve anytime) |

## Troubleshooting

### Import Errors
If you see import errors for `crewai`, ensure dependencies are installed:
```bash
crewai install
```

### API Key Errors
Verify your `.env` file has valid API keys:
```bash
cat .env
```

### Empty Scratchpad
If scratchpad is empty, check that agents are actually calling the tools. Enable verbose mode (already on) to see tool calls.

### Scratchpad Not Clearing
The scratchpad is intentionally cleared at the start of each `crewai run`. To preserve across runs, modify `crew.py` `_clear_scratchpad()` method.

## Advanced Usage

### Keep Scratchpad Between Runs

Comment out the `_clear_scratchpad()` call in `crew.py`:

```python
def __init__(self):
    super().__init__()
    self.llm = LLM(...)
    # self._clear_scratchpad()  # Comment this out
```

### Add More Tools

Add tools to specific agents in `crew.py`:

```python
@agent
def researcher(self) -> Agent:
    return Agent(
        config=self.agents_config['researcher'],
        tools=[
            self.scratchpad_read, 
            self.scratchpad_write,
            YourCustomTool()  # Add here
        ],
        llm=self.llm,
        verbose=True
    )
```

### Organize Scratchpad by Projects

Modify the `namespace` concept in `custom_tool.py` to support multiple projects:

```python
# Instead of single scratchpad.json
project_id = "fusion_energy_research"
scratchpad_file = self.scratchpad_dir / f"{project_id}_scratchpad.json"
```

## Tool API Reference

### ScratchpadWriteTool

**Purpose**: Write notes to persistent scratchpad

**Arguments**:
- `notes` (str, required): Content to save
- `category` (str, optional): Organizational category (default: "general")

**Example**:
```yaml
tools:
  - scratchpad_write:
      notes: "Research plan: Compare fusion companies"
      category: "research_plan"
```

### ScratchpadReadTool

**Purpose**: Read notes from scratchpad

**Arguments**:
- `reasoning` (str, required): Why you need the information
- `category` (str, optional): Specific category to read (None = read all)

**Example**:
```yaml
tools:
  - scratchpad_read:
      reasoning: "Need to review research plan before searching"
      category: "research_plan"
```

### UserPreferenceTool

**Purpose**: Read user preferences from knowledge base

**Arguments**:
- `query` (str, required): What preference information you're looking for

**Example**:
```yaml
tools:
  - read_user_preferences:
      query: "What are the user's report formatting requirements?"
```

## Scratchpad JSON Format

```json
{
  "research_plan": [
    {
      "timestamp": "2025-10-08T10:30:00",
      "notes": "Research plan content here"
    }
  ],
  "findings": [
    {
      "timestamp": "2025-10-08T10:35:00",
      "notes": "Finding 1 from search"
    },
    {
      "timestamp": "2025-10-08T10:40:00",
      "notes": "Finding 2 from search"
    }
  ],
  "summary": [
    {
      "timestamp": "2025-10-08T10:45:00",
      "notes": "Summary of all findings"
    }
  ]
}
```

## References

- **LangGraph Context Offloading Notebook**: Original implementation using state objects and BaseStore
- **Anthropic's Think Tool**: https://www.anthropic.com/engineering/claude-think-tool
- **Manus Blog**: https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
- **Chroma Context Rot Research**: https://research.trychroma.com/context-rot
- **CrewAI Documentation**: https://docs.crewai.com

## Support

For questions or issues:
- CrewAI: https://docs.crewai.com
- CrewAI Discord: https://discord.com/invite/X4JWnZnxPb
- LangChain Context Engineering Repo: https://github.com/langchain-ai/how_to_fix_your_context

---

**Built with CrewAI and Google Gemini** 🚀

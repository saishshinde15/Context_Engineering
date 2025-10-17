# 🧠 Context Engineering: Building AI Agents That Remember What Matters

> **The Problem**: LLMs forget. Information buried deep in long conversations loses accuracy, leading to errors and hallucinations.  
> **The Solution**: Context engineering techniques that help AI agents manage their memory effectively.

This repository demonstrates **context offloading**, a powerful context engineering pattern that stores information externally—like giving your AI a notepad—to avoid context rot and enable reliable multi-step reasoning.

## 🎯 Why Context Engineering Matters

When building AI agents, you'll hit a fundamental problem: **context rot**.

Research by Chroma shows that information buried in the middle of long context windows loses 30%+ accuracy. As conversations grow longer, your AI "forgets" earlier details, makes mistakes, and contradicts itself.

**Real-world impact:**
- ❌ Research agent loses track of its plan after 10 web searches
- ❌ Code assistant forgets user requirements halfway through implementation  
- ❌ Multi-step workflows fail because agents can't remember previous steps
- ❌ Long conversations degrade into confusion and hallucinations

**Context engineering solves this** by teaching agents to manage their memory—just like humans take notes, organize information, and refer back to what matters.

## 💡 What This Project Demonstrates

This implementation showcases **context offloading**: storing information in external persistent storage (a "scratchpad") rather than keeping everything in the LLM's context window.

**The Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTEXT OFFLOADING FLOW                      │
└─────────────────────────────────────────────────────────────────┘

📝 RESEARCH PLANNER AGENT
   ├── Reads user preferences
   ├── Creates detailed research plan
   └── 💾 SAVES PLAN TO SCRATCHPAD
         │
         ▼
🔍 RESEARCHER AGENT
   ├── 📖 READS PLAN FROM SCRATCHPAD
   ├── Conducts web searches
   ├── 💾 WRITES FINDINGS TO SCRATCHPAD after each search
   └── 💾 WRITES SUMMARY TO SCRATCHPAD
         │
         ▼
✍️ SYNTHESIS AGENT
   ├── 📖 READS ALL SCRATCHPAD NOTES
   └── Generates comprehensive report
```

**Key Benefits:**
- ✅ **Avoids Context Rot**: Information stays accurate, no matter how long the workflow
- ✅ **Enables Reusability**: Multiple agents share the same persistent information
- ✅ **Supports Complex Tasks**: Multi-step workflows maintain state across agent turns
- ✅ **Creates Audit Trail**: Every decision and finding is timestamped and retrievable

## 🚀 Quick Start

### Prerequisites
- Python >=3.10, <3.14
- Google Gemini API key ([Get it here](https://aistudio.google.com/app/apikey))
- Tavily API key ([Get it here](https://tavily.com/))

### Setup in 3 Commands

```bash
# 1. Install dependencies
crewai install

# 2. Configure API keys (create .env file)
echo "GEMINI_API_KEY=your_gemini_key_here" > .env
echo "TAVILY_API_KEY=your_tavily_key_here" >> .env

# 3. Run the crew
crewai run
```

**What happens:**
1. Planning agent creates a research plan and saves it to the scratchpad
2. Research agent reads the plan, conducts searches, and updates the scratchpad
3. Synthesis agent reads all notes and generates `report.md`

**Observe context offloading in action:**
```bash
# Watch the scratchpad populate with agent notes
cat knowledge/scratchpad.json | python -m json.tool
```

## 📊 Context Offloading vs Context Pruning

This repository demonstrates **context offloading**. Here's how it compares to other context engineering techniques:

| Technique | What It Does | When To Use |
|-----------|-------------|------------|
| **Context Offloading** | Moves info to external storage | Multi-step workflows, agent collaboration |
| **Context Pruning** | Removes irrelevant information | Noisy conversations, token reduction |
| **Context Compression** | Summarizes information | Long documents, reducing costs |

**Why offloading?** Unlike pruning (which discards) or compression (which loses detail), offloading preserves full information while preventing context rot.

## 🔬 How It Works

### The Scratchpad Pattern

Instead of keeping everything in context:
```python
# ❌ Traditional approach: Everything in context
prompt = f"Plan: {plan}\nSearch 1: {search1}\nSearch 2: {search2}..."
# Problem: Context grows huge, information gets lost

# ✅ Context offloading: External storage
scratchpad_write(notes=plan, category="research_plan")
scratchpad_write(notes=search1, category="findings")
scratchpad_write(notes=search2, category="findings")
# Benefit: Clean context, accurate retrieval
```

### Persistent Storage
All agent notes are stored in `knowledge/scratchpad.json`:
```json
{
  "research_plan": [
    {"timestamp": "2025-10-17T10:30:00", "notes": "Research plan..."}
  ],
  "findings": [
    {"timestamp": "2025-10-17T10:35:00", "notes": "Finding 1..."},
    {"timestamp": "2025-10-17T10:40:00", "notes": "Finding 2..."}
  ]
}
```

### Recitation Effect
When an agent reads from the scratchpad, that information moves to the **end** of the context window, improving model attention—a phenomenon discovered by Manus in their agent research.

## 📁 Project Structure

```
context_offloading/
├── src/context_offloading/
│   ├── config/
│   │   ├── agents.yaml          # 3 agents: planner, researcher, synthesizer
│   │   └── tasks.yaml           # Structured workflows with scratchpad ops
│   ├── tools/
│   │   └── custom_tool.py       # Scratchpad read/write tools
│   ├── crew.py                  # Crew orchestration
│   └── main.py                  # Entry point
├── knowledge/
│   ├── user_preference.txt      # User requirements
│   └── scratchpad.json          # Persistent scratchpad (auto-created)
├── report.md                    # Generated output
├── README.md                    # This file
├── DOCUMENTATION.md             # Detailed technical documentation
└── QUICKSTART.md                # Rapid setup guide
```

## 🎓 Learn More

- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Complete technical guide with API reference
- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 3 steps
- **[Implementation Details](IMPLEMENTATION_SUMMARY.md)** - Architecture and design decisions

## 🌟 Key Concepts Demonstrated

1. **Context Rot Mitigation** - External storage prevents information decay
2. **Persistent Memory** - Information survives across agent turns and tasks
3. **Audit Trail** - Timestamped notes create transparency into agent reasoning
4. **Structured Workflows** - Explicit scratchpad operations ensure systematic behavior
5. **Multi-Agent Collaboration** - Shared scratchpad enables agent coordination

## 🔗 References & Further Reading

- **Chroma's Context Rot Research**: [research.trychroma.com/context-rot](https://research.trychroma.com/context-rot)
- **Manus Blog on Context Engineering**: [manus.im/blog/Context-Engineering-for-AI-Agents](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
- **Anthropic's Think Tool**: [anthropic.com/engineering/claude-think-tool](https://www.anthropic.com/engineering/claude-think-tool)
- **LangChain Context Engineering**: [github.com/langchain-ai/how_to_fix_your_context](https://github.com/langchain-ai/how_to_fix_your_context)

## 🛠️ Built With

- **[CrewAI](https://crewai.com)** - Multi-agent orchestration framework
- **[Google Gemini](https://ai.google.dev/)** - Large language model
- **[Tavily](https://tavily.com/)** - Web search API

---

**Made with ❤️ to demonstrate practical context engineering for AI agents**

*Have questions? Read the [documentation](DOCUMENTATION.md) or check out [CrewAI's Discord](https://discord.com/invite/X4JWnZnxPb)*


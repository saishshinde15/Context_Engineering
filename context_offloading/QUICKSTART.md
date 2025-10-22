# 🚀 Context Offloading - Quick Start

## What You'll Learn

This crew demonstrates **context offloading**: storing information outside the LLM's context window using a persistent scratchpad.

## 3-Step Setup

### 1️⃣ Install Dependencies

```bash
cd context_offloading
crewai install
```

### 2️⃣ Configure API Keys

Create `.env` file:
```bash
GEMINI_API_KEY=your_gemini_key_here
TAVILY_API_KEY=your_tavily_key_here
```

Get keys:
- **Gemini**: https://aistudio.google.com/app/apikey
- **Tavily**: https://tavily.com/ (free tier)

### 3️⃣ Run the Crew

```bash
crewai run
```

## What Happens

1. **Planning Agent** → Creates research plan → Saves to scratchpad
2. **Research Agent** → Reads plan → Searches web → Updates scratchpad
3. **Synthesis Agent** → Reads scratchpad → Creates report

## Output

- `report.md` - Final comprehensive report
- `knowledge/scratchpad.json` - All intermediate notes

## View the Scratchpad

```bash
cat knowledge/scratchpad.json | python -m json.tool
```

## Customize

**Change research topic**: Edit `src/context_offloading/main.py`
```python
inputs = {
    'topic': 'Your question here',
    'current_year': str(datetime.now().year)
}
```

**Change preferences**: Edit `knowledge/user_preference.txt`

## Key Concept

Unlike **context pruning** (removes info), **context offloading** moves info externally for later retrieval - like taking notes!

## Next Steps

- Read `DOCUMENTATION.md` for detailed explanation
- Explore `knowledge/scratchpad.json` to see agent notes
- Compare with `context_pruning` implementation

---

**Questions?** See [CrewAI Docs](https://docs.crewai.com)

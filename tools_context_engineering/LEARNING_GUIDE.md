# Anthropic Advanced Tool Use: Complete Learning Guide

> **Source**: [Anthropic Engineering Blog - Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use)  
> **Implementation**: [demo_agent.py](./demo_agent.py)

---

## Executive Summary

Anthropic introduced **3 techniques** to scale AI agents to work with hundreds of tools efficiently:

| Concept | Problem It Solves | Token Impact |
|---------|------------------|--------------|
| **Tool Search Tool** | Context bloat from tool definitions | 85% reduction |
| **Programmatic Tool Calling** | Intermediate results polluting context | 37% reduction |
| **Tool Use Examples** | Parameter format errors | 72% → 90% accuracy |

This guide explains each concept with code from our implementation.

---

## Concept 1: Tool Search Tool

### The Problem

Real-world agents connect to many services. Each tool definition consumes tokens:

```
GitHub:   35 tools → ~26K tokens
Slack:    11 tools → ~21K tokens  
Jira:     15 tools → ~17K tokens
Sentry:    5 tools →  ~3K tokens
────────────────────────────────
Total:    66 tools → ~67K tokens (before any conversation!)
```

**Issues:**
1. Wastes context window on unused tools
2. Model confuses similar tools (e.g., `notification-send-user` vs `notification-send-channel`)

### The Solution: On-Demand Tool Discovery

Instead of loading all tools upfront:
- Mark critical tools as "always loaded"
- Mark others as "deferred" (discoverable on-demand)
- Search for relevant tools when needed

### Our Implementation

#### Step 1: ToolSpec with `defer_loading` Flag

```python
@dataclass
class ToolSpec:
    name: str
    description: str
    tool: Callable
    defer_loading: bool = True  # The key flag!
    examples: List[str] = field(default_factory=list)
```

#### Step 2: Catalog with Mixed Loading Strategy

```python
def build_catalog():
    # ═══════════════════════════════════════════════════════════
    # ALWAYS-LOADED TOOLS (defer_loading=False)
    # These are your most-used tools, always available
    # ═══════════════════════════════════════════════════════════
    
    duck = ToolSpec(
        name="duckduckgo_search",
        description="Web search for fresh results...",
        tool=DuckDuckGoSearchRun(),
        defer_loading=False,  # ← Always available
    )
    
    wiki = ToolSpec(
        name="wikipedia",
        description="Wikipedia lookup...",
        tool=WikipediaQueryRun(...),
        defer_loading=False,  # ← Always available
    )
    
    # ═══════════════════════════════════════════════════════════
    # DEFERRED TOOLS (defer_loading=True)
    # Only loaded when query matches - saves context tokens
    # ═══════════════════════════════════════════════════════════
    
    weather = ToolSpec(
        name="open_meteo_weather",
        description="Get weather forecast by city name...",
        tool=get_weather,
        defer_loading=True,  # ← Only for weather queries
    )
    
    github = ToolSpec(
        name="github_repo_search",
        description="Search GitHub repositories...",
        tool=search_github_repos,
        defer_loading=True,  # ← Only for GitHub queries
    )
```

#### Step 3: Selection Algorithm

```python
def _score(query: str, spec: ToolSpec) -> float:
    """
    Compute similarity between user query and tool metadata.
    
    In production, you'd use embeddings or BM25.
    We use SequenceMatcher as a simple baseline.
    """
    target = f"{spec.name} {spec.description}".lower()
    return difflib.SequenceMatcher(None, query.lower(), target).ratio()


def select_tools(query: str, catalog: List[ToolSpec], top_k: int = 3):
    """
    Tool Search Tool implementation:
    1. Always include non-deferred tools
    2. Score deferred tools by query similarity
    3. Return top-k matches + always-loaded
    """
    # Always-loaded tools (e.g., search, wiki)
    always = [t for t in catalog if not t.defer_loading]
    
    # Score and rank deferred tools
    deferred = [t for t in catalog if t.defer_loading]
    scored = sorted(deferred, key=lambda spec: _score(query, spec), reverse=True)
    
    # Take top-k matches
    chosen = scored[:top_k]
    
    return always + chosen
```

### Example: How It Works

**Query**: `"What is the weather in Tokyo?"`

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Always-loaded tools                                 │
│   → duckduckgo_search, wikipedia                            │
├─────────────────────────────────────────────────────────────┤
│ Step 2: Score deferred tools against "weather in Tokyo"     │
│                                                             │
│   Tool                    Score   Match?                    │
│   ──────────────────────  ─────   ──────                    │
│   open_meteo_weather      0.42    ✓ HIGH (contains weather) │
│   github_repo_search      0.18    ✗ LOW                     │
│   fx_rate                 0.15    ✗ LOW                     │
│   python_repl             0.12    ✗ LOW                     │
│   http_get                0.10    ✗ LOW                     │
├─────────────────────────────────────────────────────────────┤
│ Step 3: Return always + top 3 deferred                      │
│   → [duckduckgo_search, wikipedia, open_meteo_weather, ...] │
└─────────────────────────────────────────────────────────────┘
```

**Output:**
```
CONCEPT 1: Tool Search Tool - Selected tools for this query:
  [ALWAYS] duckduckgo_search
  [ALWAYS] wikipedia
  [MATCHED] open_meteo_weather  ← Correctly identified as relevant!
  [MATCHED] fx_rate
  [MATCHED] github_repo_search
```

### Anthropic's Production Results

| Metric | Without Tool Search | With Tool Search |
|--------|--------------------:|----------------:|
| Token usage | ~77K | ~8.7K |
| **Savings** | — | **85%** |
| Opus 4 accuracy | 49% | 74% |
| Opus 4.5 accuracy | 79.5% | 88.1% |

---

## Concept 2: Programmatic Tool Calling

### The Problem

Traditional tool calling has two issues:

1. **Context pollution**: Every tool result enters context, even if you only need a summary
2. **Inference overhead**: Each tool call = 1 full inference pass

**Example scenario**: "Which team members exceeded Q3 travel budget?"

```
Traditional approach:
├── Call get_team_members()           → 20 people in context
├── Call get_expenses() × 20          → 2,000+ line items in context
├── Call get_budget_by_level() × 4    → budget info in context
└── Claude manually sums, compares    → Many inference passes

Total: 22+ tool calls, 50KB+ of expense data in context
```

### The Solution: Let Model Write Code

Instead of individual tool calls, Claude writes Python that:
- Orchestrates multiple tool calls
- Processes data (loops, filters, aggregates)
- Returns only the final result to context

### Our Implementation

```python
@tool
def run_python(code: str) -> str:
    """
    CONCEPT 2: Programmatic Tool Calling
    
    Execute Python code for data transformations and orchestration.
    Use when you need to:
    - Process multiple items in a loop
    - Aggregate/filter data before returning
    - Keep intermediate results OUT of context
    
    Args:
        code: Python code to execute. Use print() to output results.
    
    Returns:
        stdout from code execution (only this enters context!)
    """
    import io
    import contextlib
    
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            exec(code, {"__builtins__": __builtins__})
        result = output.getvalue()
        return result if result else "Code executed successfully"
    except Exception as e:
        return f"Error: {str(e)}"
```

### Example: Budget Compliance Check

**Without Programmatic Tool Calling:**
```
Context receives:
- 20 team member records
- 2,000+ expense line items 
- 4 budget level definitions
- All intermediate calculations

Total context: ~50KB
```

**With Programmatic Tool Calling:**

Claude writes this code:
```python
# This runs in sandbox - intermediate data stays OUT of context

team = await get_team_members("engineering")

# Fetch all expenses in parallel
expenses = await asyncio.gather(*[
    get_expenses(m["id"], "Q3") for m in team
])

# Fetch budgets
levels = list(set(m["level"] for m in team))
budgets = {level: await get_budget_by_level(level) for level in levels}

# Process and filter - ONLY exceeding members returned
exceeded = []
for member, exp in zip(team, expenses):
    total = sum(e["amount"] for e in exp)
    limit = budgets[member["level"]]["travel_limit"]
    if total > limit:
        exceeded.append({
            "name": member["name"],
            "spent": total,
            "limit": limit
        })

print(json.dumps(exceeded))  # ← ONLY THIS enters context!
```

**Context receives:**
```json
[{"name": "Alice", "spent": 12500, "limit": 10000}]
```

**Total context: ~100 bytes** (vs 50KB!)

### When to Use

✅ **Use Programmatic Tool Calling when:**
- Processing large datasets where you only need aggregates
- Running multi-step workflows with 3+ tool calls
- Filtering/transforming tool results before Claude sees them
- Parallel operations across many items

❌ **Less beneficial when:**
- Simple single-tool invocations
- Claude should reason about all intermediate results
- Quick lookups with small responses

### Anthropic's Production Results

| Metric | Improvement |
|--------|-------------|
| Token usage | 37% reduction |
| Latency | Eliminates N-1 inference passes |
| Internal knowledge retrieval | 25.6% → 28.5% |
| GIA benchmarks | 46.5% → 51.2% |

---

## Concept 3: Tool Use Examples

### The Problem

JSON schemas define structure, but can't express **usage patterns**:

```json
{
  "name": "create_ticket",
  "input_schema": {
    "properties": {
      "due_date": {"type": "string"},     // What format? ISO? US date?
      "reporter": {
        "id": {"type": "string"}          // UUID? "USR-12345"? Just "12345"?
      }
    }
  }
}
```

**Ambiguities:**
- Should `due_date` be `"2024-11-06"`, `"Nov 6, 2024"`, or `"2024-11-06T00:00:00Z"`?
- Is `reporter.id` a UUID, `"USR-12345"`, or just `"12345"`?
- When should optional parameters be included?

### The Solution: Provide Example Invocations

```python
weather = ToolSpec(
    name="open_meteo_weather",
    description="Get weather forecast by city name...",
    tool=get_weather,
    examples=[
        "get_weather('San Francisco')",  # Shows: city name, not coordinates
        "get_weather('Tokyo')",           # Shows: proper capitalization
        "get_weather('London')"           # Shows: international cities OK
    ]
)
```

### Our Implementation

Each `ToolSpec` includes an `examples` field:

```python
@dataclass
class ToolSpec:
    name: str
    description: str
    tool: Callable
    defer_loading: bool = True
    examples: List[str] = field(default_factory=list)  # ← Example invocations
```

**Catalog with examples:**

```python
github_search = ToolSpec(
    name="github_repo_search",
    description="Search GitHub repositories by topic keyword...",
    tool=search_github_repos,
    examples=[
        "search_github_repos('retrieval augmented generation')",
        "search_github_repos('LLM agent framework')"
    ]
)

fx = ToolSpec(
    name="fx_rate",
    description="Fetch FX conversion rate...",
    tool=fx_rate,
    examples=[
        "fx_rate('USD to EUR')",   # Shows: "X to Y" format
        "fx_rate('GBP/JPY')"       # Shows: "X/Y" also works
    ]
)
```

### What Examples Teach the Model

From these 3 ticket examples:
```python
examples=[
    {"title": "Login error", "priority": "critical", "due_date": "2024-11-06"},
    {"title": "Add dark mode", "labels": ["feature-request"]},
    {"title": "Update docs"}  # Minimal - just title
]
```

Claude learns:
- **Formats**: Dates use `YYYY-MM-DD`
- **Patterns**: Critical bugs have `due_date`, features have `labels`, simple tasks are minimal
- **Conventions**: Label names use kebab-case

### Anthropic's Production Results

| Metric | Without Examples | With Examples |
|--------|----------------:|-------------:|
| Complex parameter accuracy | 72% | 90% |
| **Improvement** | — | **+18%** |

---

## Putting It All Together

### When to Use Each Feature

```
┌─────────────────────────────────────────────────────────────┐
│                    DECISION TREE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  "Context bloated by tool definitions?"                     │
│       ↓ YES                                                 │
│  → Use TOOL SEARCH TOOL                                     │
│                                                             │
│  "Intermediate results polluting context?"                  │
│       ↓ YES                                                 │
│  → Use PROGRAMMATIC TOOL CALLING                            │
│                                                             │
│  "Model making parameter format errors?"                    │
│       ↓ YES                                                 │
│  → Use TOOL USE EXAMPLES                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Our Implementation Summary

```python
# demo_agent.py structure

# CONCEPT 1: Tool Search Tool
@dataclass
class ToolSpec:
    defer_loading: bool = True  # Flag for on-demand loading

def select_tools(query, catalog, top_k=3):
    # Search algorithm to find relevant tools


# CONCEPT 2: Programmatic Tool Calling  
@tool
def run_python(code: str) -> str:
    # Execute code, return only final output


# CONCEPT 3: Tool Use Examples
weather = ToolSpec(
    examples=["get_weather('San Francisco')", ...]
)
```

---

## Running the Demo

```bash
cd /Users/saish/Downloads/Context_engineering/tools_context_engineering
source venv/bin/activate

# See tool selection (Concept 1)
python demo_agent.py --query "What is the weather in Tokyo?"

# Complex multi-tool query
python demo_agent.py --query "Find GitHub repos about RAG and compare SF vs NYC weather"

# Adjust how many deferred tools to load
python demo_agent.py --query "Convert USD to EUR" --top-k 2
```

---

## Key Takeaways

1. **Tool Search Tool** = Don't load tools you don't need (85% token savings)
2. **Programmatic Tool Calling** = Let model write code to orchestrate (37% token savings)
3. **Tool Use Examples** = Show, don't just describe (+18% accuracy)

These three patterns together enable agents that can work with **hundreds of tools** efficiently, which is essential for production AI systems.

---

*Document created: January 11, 2026*  
*Based on Anthropic Engineering Blog: "Advanced Tool Use"*

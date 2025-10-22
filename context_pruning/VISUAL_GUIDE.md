# Context Pruning - Implementation Visual Guide

```
╔══════════════════════════════════════════════════════════════════════╗
║                    CONTEXT PRUNING WORKFLOW                          ║
╚══════════════════════════════════════════════════════════════════════╝

USER QUERY: "What are the types of reward hacking discussed in blogs?"
    │
    ↓
┌───────────────────────────────────────────────────────────────────┐
│                         AGENT 1: RETRIEVAL                        │
│  Role: Information Retrieval Specialist                          │
│  Tool: RAGRetrievalTool                                          │
├───────────────────────────────────────────────────────────────────┤
│  Actions:                                                         │
│  1. Load Lilian Weng's blog posts from URLs                      │
│  2. Split into chunks (3000 tokens each)                         │
│  3. Create embeddings (Google embedding-001)                     │
│  4. Build vector store (InMemoryVectorStore)                     │
│  5. Semantic search for relevant chunks (k=4)                    │
├───────────────────────────────────────────────────────────────────┤
│  Output: ~15,000 tokens                                          │
│  Contains: Relevant + Irrelevant + Redundant information        │
└───────────────────────────────────────────────────────────────────┘
    │
    ↓ (passes context automatically)
    │
┌───────────────────────────────────────────────────────────────────┐
│                         AGENT 2: PRUNING                          │
│  Role: Context Pruning Specialist                                │
│  Tool: ContextPruningTool                                        │
├───────────────────────────────────────────────────────────────────┤
│  Actions:                                                         │
│  1. Receive user query + retrieved content                       │
│  2. Initialize Gemini Flash (gemini-1.5-flash, temp=0)          │
│  3. Apply structured pruning prompt:                             │
│     - Keep: Facts, data, examples relevant to query             │
│     - Remove: Tangential discussions, background, redundancy    │
│  4. Extract only relevant information                            │
├───────────────────────────────────────────────────────────────────┤
│  Output: ~6,000 tokens (60% reduction)                          │
│  Contains: Only information directly answering the query         │
└───────────────────────────────────────────────────────────────────┘
    │
    ↓ (passes pruned context)
    │
┌───────────────────────────────────────────────────────────────────┐
│                      AGENT 3: SYNTHESIZER                         │
│  Role: Research Response Synthesizer                             │
│  Tools: None (uses pruned context)                               │
├───────────────────────────────────────────────────────────────────┤
│  Actions:                                                         │
│  1. Read pruned, focused content                                 │
│  2. Structure information logically                              │
│  3. Generate comprehensive markdown answer                       │
│  4. Include specific examples and data points                    │
│  5. Cite sources appropriately                                   │
├───────────────────────────────────────────────────────────────────┤
│  Output: context_pruning_result.md                              │
│  Format: Well-structured markdown with headers, bullets, etc.    │
└───────────────────────────────────────────────────────────────────┘
    │
    ↓
FINAL ANSWER: Comprehensive response about reward hacking types


╔══════════════════════════════════════════════════════════════════════╗
║                        TECHNICAL STACK                               ║
╚══════════════════════════════════════════════════════════════════════╝

Framework:       CrewAI 0.130.0+
Orchestration:   Sequential Process (Task A → B → C)
LLM Provider:    Google Gemini (via langchain-google-genai)
Embeddings:      models/embedding-001 (Google)
Pruning Model:   gemini-1.5-flash
Vector Store:    InMemoryVectorStore (LangChain)
Data Source:     4 Lilian Weng blog posts
Configuration:   YAML (agents + tasks) + Python (tools)


╔══════════════════════════════════════════════════════════════════════╗
║                      FILE STRUCTURE                                  ║
╚══════════════════════════════════════════════════════════════════════╝

context_pruning/
│
├── 📄 .env                           ← API keys configuration
├── 📄 pyproject.toml                 ← Dependencies & scripts
├── 📄 README.md                      ← Complete documentation
├── 📄 QUICKSTART.md                  ← 3-step quick start
├── 📄 IMPLEMENTATION_NOTES.md        ← Technical deep dive
├── 📄 SUMMARY.txt                    ← Implementation summary
├── 📄 test_setup.py                  ← Installation checker
│
└── 📁 src/context_pruning/
    │
    ├── 📄 __init__.py
    ├── 📄 main.py                    ← Entry point with inputs
    ├── 📄 crew.py                    ← Crew definition & wiring
    │
    ├── 📁 config/
    │   ├── 📄 agents.yaml           ← 3 agent definitions
    │   └── 📄 tasks.yaml            ← 3 task definitions
    │
    └── 📁 tools/
        ├── 📄 __init__.py           ← Tool exports
        └── 📄 custom_tool.py        ← RAG + Pruning tools


╔══════════════════════════════════════════════════════════════════════╗
║                    KEY DESIGN DECISIONS                              ║
╚══════════════════════════════════════════════════════════════════════╝

✓ Google Gemini vs OpenAI
  Why: User already has Gemini API key, cost effective, fast
  
✓ Lazy Loading of Vector Store
  Why: Avoid loading heavy resources on import, faster startup
  
✓ Three Separate Agents
  Why: Clear separation of concerns, easy to debug, modular
  
✓ YAML Configuration
  Why: Easy to modify agents/tasks without touching code
  
✓ Sequential Process
  Why: Context pruning is inherently sequential (retrieve → filter)
  
✓ Temperature = 0 for Pruning
  Why: Deterministic pruning, consistent results


╔══════════════════════════════════════════════════════════════════════╗
║                     TOKEN FLOW DIAGRAM                               ║
╚══════════════════════════════════════════════════════════════════════╝

Blog Posts (4 articles)
    ↓ split into chunks
Chunks (~50 total, 3000 tokens each)
    ↓ semantic search (k=4)
Retrieved (4 chunks × ~3750 tokens ≈ 15,000 tokens)
    ↓ context pruning
Pruned (~6,000 tokens, 60% reduction)
    ↓ synthesis
Final Answer (markdown, ~2,000 tokens)


╔══════════════════════════════════════════════════════════════════════╗
║                    COMPARISON TABLE                                  ║
╚══════════════════════════════════════════════════════════════════════╝

Aspect              │ LangGraph Original │ CrewAI Implementation
────────────────────┼────────────────────┼──────────────────────
Orchestration       │ StateGraph         │ Agent Workflow
State Management    │ Custom classes     │ Auto context passing
Tool Calling        │ Manual binding     │ Agent-tool assignment
Flow Control        │ Conditional edges  │ Task dependencies
LLM Provider        │ OpenAI            │ Google Gemini
Embeddings          │ text-embed-3-small│ embedding-001
Pruning Model       │ gpt-4o-mini       │ gemini-1.5-flash
Configuration       │ Python only       │ YAML + Python
Code Lines          │ ~200              │ ~150 + YAML
Learning Curve      │ Steeper           │ Gentler
Abstraction Level   │ Lower             │ Higher
Control             │ More              │ Less
Developer UX        │ Explicit          │ Declarative


╔══════════════════════════════════════════════════════════════════════╗
║                      EXECUTION STEPS                                 ║
╚══════════════════════════════════════════════════════════════════════╝

$ cd /Users/saish/Downloads/Context_engineering/context_pruning
$ crewai run

Expected output:
  1. CrewAI initialization
  2. Agent 1 (Retrieval) starts → RAGRetrievalTool executes
  3. Vector store loads (first run only)
  4. Semantic search runs
  5. Agent 2 (Pruning) starts → ContextPruningTool executes
  6. Gemini Flash prunes content
  7. Agent 3 (Synthesizer) starts → generates answer
  8. Result saved to context_pruning_result.md
  9. Summary printed to console


╔══════════════════════════════════════════════════════════════════════╗
║                      SUCCESS METRICS                                 ║
╚══════════════════════════════════════════════════════════════════════╝

✓ Token Reduction: Should see ~60% reduction
✓ Answer Quality: Should list specific reward hacking types
✓ Execution Time: 20-30 seconds total
✓ Cost: < $0.01 per query
✓ Output Format: Clean markdown in .md file


╔══════════════════════════════════════════════════════════════════════╗
║                   WHAT YOU CAN DO NEXT                               ║
╚══════════════════════════════════════════════════════════════════════╝

1. Run the implementation:
   crewai run

2. Try different queries:
   Edit src/context_pruning/main.py

3. Compare with LangGraph:
   Check ../how_to_fix_your_context/notebooks/04-context-pruning.ipynb

4. Implement other techniques:
   - Tool Loadout
   - Context Quarantine
   - Context Summarization
   - Context Offloading

5. Enhance the implementation:
   - Add caching
   - Add evaluation metrics
   - Support more data sources
   - Add streaming responses
```

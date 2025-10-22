# Context Pruning with CrewAI

This project demonstrates **Context Pruning** - one of the six context engineering techniques for improving LLM agent performance. Context pruning removes irrelevant or unneeded information from retrieved content, helping avoid context distraction and improving response quality.

## What is Context Pruning?

**Context Pruning** is the act of removing irrelevant or otherwise unneeded information from the context.

### Why it Helps

- **Avoids Context Distraction**: When context grows, models can over-focus on accumulated history, neglecting their training. Research shows LLM performance degrades as input length grows.
- **Reduces Token Usage**: By removing irrelevant content, we significantly reduce tokens (e.g., from 25k to 11k in the LangGraph example)
- **Improves Response Quality**: Focused, relevant context leads to better, more accurate responses

## Architecture

This CrewAI implementation uses a **three-agent sequential workflow**:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Retrieval      │────▶│   Pruning       │────▶│   Response      │
│  Agent          │     │   Agent         │     │   Synthesizer   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
      │                        │                        │
      ▼                        ▼                        ▼
 RAG Retrieval          Context Pruning          Final Answer
    Tool                     Tool                  Generation
```

### Agents

1. **Retrieval Agent**: Uses RAG to retrieve relevant content from Lilian Weng's blog posts
   - Tool: `RAGRetrievalTool` - searches vector store for relevant chunks
   - Returns: Raw retrieved content (may contain irrelevant information)

2. **Pruning Agent**: Filters retrieved content using an LLM-based pruning tool
   - Tool: `ContextPruningTool` - uses Gemini Flash to extract only relevant information
   - Returns: Pruned content focused on answering the specific query

3. **Response Synthesizer**: Creates the final comprehensive answer
   - No tools needed - uses pruned context to generate answer
   - Returns: Well-structured markdown response

## Installation

### Prerequisites
- Python >=3.10 <3.14
- [uv](https://docs.astral.sh/uv/) package manager
- Google Gemini API key

### Setup

1. **Install dependencies**:
```bash
cd context_pruning
crewai install
# or manually: uv pip install -e .
```

2. **Configure API keys**:
Edit `.env` file:
```bash
MODEL=gemini/gemini-flash-latest
GEMINI_API_KEY=your-gemini-api-key-here
```

## Running the Project

### Basic Execution
```bash
crewai run
```

This will:
1. Retrieve content about "reward hacking" from Lilian Weng's blog posts
2. Prune the content to focus on relevant information
3. Generate a comprehensive answer
4. Save the result to `context_pruning_result.md`

### Custom Queries

Edit `src/context_pruning/main.py` to change the query:

```python
inputs = {
    'topic': 'your topic here',
    'query': 'Your specific question here'
}
```

## Implementation Details

### Tools

#### RAGRetrievalTool
- Loads 4 blog posts from Lilian Weng (thinking, reward hacking, hallucination, diffusion)
- Splits into chunks (3000 tokens, 50 overlap)
- Uses Google Gemini embeddings (`models/embedding-001`)
- Returns top 4 most relevant chunks

#### ContextPruningTool
- Takes user request + retrieved content
- Uses Gemini Flash (`gemini-1.5-flash`) at temperature 0
- Applies structured pruning prompt to extract only relevant information
- Preserves key facts, data, examples while removing tangential content

### Configuration Files

- `config/agents.yaml`: Defines agent roles, goals, and backstories
- `config/tasks.yaml`: Defines task descriptions, expected outputs, and dependencies
- `src/context_pruning/crew.py`: Wires agents and tasks together
- `src/context_pruning/tools/custom_tool.py`: Implements RAG and pruning tools

## Comparison with LangGraph Implementation

| Aspect | LangGraph | CrewAI |
|--------|-----------|--------|
| **Architecture** | StateGraph with nodes/edges | Sequential agent workflow |
| **Tool Calling** | Direct tool binding to LLM | Agent decides when to use tools |
| **State Management** | Custom State classes | Automatic context passing |
| **Pruning Step** | Explicit node in graph | Dedicated agent with tool |
| **Flexibility** | Full control over flow | Higher-level abstractions |

## Benefits of This Approach

1. **Reduced Token Usage**: Pruning removes ~40-60% of irrelevant content
2. **Improved Accuracy**: Focused context leads to more accurate answers
3. **Cost Efficiency**: Using Gemini Flash for pruning is cost-effective
4. **Modular Design**: Each agent has a clear, single responsibility
5. **Easy to Extend**: Add more agents/tools for additional context engineering techniques

## Example Output

Query: *"What are the types of reward hacking discussed in the blogs?"*

**Before Pruning**: ~15,000 tokens of mixed relevant and irrelevant content  
**After Pruning**: ~6,000 tokens of highly focused content  
**Result**: Clear, comprehensive answer with specific examples and categories

## Training & Testing

Train the crew:
```bash
crewai train <n_iterations> <filename>
```

Test the crew:
```bash
crewai test <n_iterations> <eval_llm>
```

Replay a specific task:
```bash
crewai replay <task_id>
```

## References

- [How to Fix Your Context](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html) by Drew Breunig
- [LangGraph Context Pruning Example](../how_to_fix_your_context/notebooks/04-context-pruning.ipynb)
- [CrewAI Documentation](https://docs.crewai.com)
- [Context Rot Research](https://research.trychroma.com/context-rot)

## Support

For support or questions:
- [CrewAI Documentation](https://docs.crewai.com)
- [CrewAI GitHub](https://github.com/joaomdmoura/crewai)
- [CrewAI Discord](https://discord.com/invite/X4JWnZnxPb)

---

**Next Steps**: Try implementing other context engineering techniques with CrewAI:
- Tool Loadout (semantic tool selection)
- Context Quarantine (multi-agent isolation)
- Context Summarization (compression)
- Context Offloading (external memory)

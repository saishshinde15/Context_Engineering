# Context Pruning - CrewAI Implementation Notes

## Overview

This is a **CrewAI implementation** of the Context Pruning technique from the LangGraph examples. Context Pruning removes irrelevant information from retrieved documents to improve response quality and reduce token usage.

## Key Differences from LangGraph Implementation

### Architecture Comparison

| Feature | LangGraph | CrewAI (This Implementation) |
|---------|-----------|------------------------------|
| **Orchestration** | StateGraph with nodes/edges | Sequential agent workflow |
| **State Management** | Custom State classes with fields | Automatic context passing between tasks |
| **Tool Integration** | Manual tool binding to LLM | Tools assigned to specific agents |
| **Flow Control** | Conditional edges with `should_continue` | Task dependencies via `context` |
| **LLM Provider** | OpenAI (GPT-4o-mini for pruning) | Google Gemini (Flash for pruning) |
| **Embeddings** | OpenAI text-embedding-3-small | Google embedding-001 |

### What We Replicated

✅ **RAG Retrieval**: Vector store with blog post chunks  
✅ **Context Pruning**: LLM-based filtering of irrelevant content  
✅ **Sequential Workflow**: Retrieve → Prune → Synthesize  
✅ **Token Reduction**: Same goal of 40-60% reduction  
✅ **Same Data Source**: Lilian Weng's blog posts

### What's Different

🔄 **Agent-Based Design**: Each step is an autonomous agent  
🔄 **Tool Abstractions**: Tools are first-class objects with schemas  
🔄 **Google Gemini**: Cost-effective alternative to OpenAI  
🔄 **Declarative Config**: Agents and tasks defined in YAML  
🔄 **Higher-Level API**: CrewAI handles orchestration details

## Implementation Details

### File Structure

```
context_pruning/
├── .env                          # API keys (GEMINI_API_KEY)
├── pyproject.toml                # Dependencies
├── README.md                     # Full documentation
├── QUICKSTART.md                 # Quick start guide
├── IMPLEMENTATION_NOTES.md       # This file
└── src/context_pruning/
    ├── main.py                   # Entry point
    ├── crew.py                   # Crew definition
    ├── config/
    │   ├── agents.yaml          # Agent configurations
    │   └── tasks.yaml           # Task definitions
    └── tools/
        ├── __init__.py
        └── custom_tool.py       # RAG & Pruning tools
```

### Agent Design

#### 1. Retrieval Agent
**Role**: Information Retrieval Specialist  
**Tool**: `RAGRetrievalTool`  
**Function**: Searches vector store for relevant blog content  
**Output**: Raw retrieved chunks (may contain noise)

```python
@agent
def retrieval_agent(self) -> Agent:
    return Agent(
        config=self.agents_config['retrieval_agent'],
        tools=[RAGRetrievalTool()],
        verbose=True
    )
```

#### 2. Pruning Agent
**Role**: Context Pruning Specialist  
**Tool**: `ContextPruningTool`  
**Function**: Filters content using Gemini Flash  
**Output**: Pruned, focused content

```python
@agent
def pruning_agent(self) -> Agent:
    return Agent(
        config=self.agents_config['pruning_agent'],
        tools=[ContextPruningTool()],
        verbose=True
    )
```

#### 3. Response Synthesizer
**Role**: Research Response Synthesizer  
**Tools**: None (uses context from previous tasks)  
**Function**: Creates final markdown answer  
**Output**: Comprehensive, well-structured response

### Tool Implementation

#### RAGRetrievalTool

```python
class RAGRetrievalTool(BaseTool):
    - Lazy loads vector store on first use
    - Uses Google Gemini embeddings (embedding-001)
    - Retrieves top-k=4 chunks
    - Concatenates with separators
```

**Key Design Decision**: Lazy initialization prevents loading heavy resources on import.

#### ContextPruningTool

```python
class ContextPruningTool(BaseTool):
    - Takes user_request + retrieved_content
    - Uses Gemini Flash (gemini-1.5-flash)
    - Structured pruning prompt
    - Returns focused content
```

**Key Design Decision**: Uses same pruning prompt structure as LangGraph example.

### Task Dependencies

```yaml
retrieval_task:
  agent: retrieval_agent
  # No dependencies

pruning_task:
  agent: pruning_agent
  context: [retrieval_task]  # Depends on retrieval

synthesis_task:
  agent: response_synthesizer
  context: [pruning_task]    # Depends on pruning
```

CrewAI automatically passes outputs from dependent tasks as context.

## Why Google Gemini?

1. **Cost Effective**: Gemini Flash is significantly cheaper than GPT-4o-mini
2. **Fast**: Flash model optimized for speed
3. **Good Enough**: For pruning tasks, Flash performs well
4. **API Availability**: User already has Gemini API key

### Model Selection

- **Embeddings**: `models/embedding-001` (768 dimensions)
- **Pruning LLM**: `gemini-flash-latest` (fast, cheap)
- **Main Agents**: Use MODEL from .env (`gemini/gemini-flash-latest`)

## Expected Performance

### Token Reduction
- **Before Pruning**: ~15,000 tokens (raw retrieval)
- **After Pruning**: ~6,000 tokens (60% reduction)
- **Similar to LangGraph**: 25k → 11k tokens (56% reduction)

### Execution Time
- **Vector Store Init**: 5-10 seconds (first run only)
- **Retrieval**: 1-2 seconds
- **Pruning**: 3-5 seconds (Gemini Flash)
- **Synthesis**: 5-10 seconds
- **Total**: ~20-30 seconds

### Cost Estimate (Gemini Pricing)
- **Embeddings**: Free tier or very low cost
- **Pruning (Flash)**: ~$0.001 per query
- **Synthesis (Flash)**: ~$0.002 per query
- **Total**: < $0.01 per complete workflow

## Testing the Implementation

### Basic Test
```bash
cd context_pruning
crewai run
```

### Check Output
```bash
cat context_pruning_result.md
```

### Verify Token Reduction
Look for agent logs showing:
1. Retrieved content size
2. Pruned content size
3. Reduction percentage

### Expected Results
The final answer should:
- List specific types of reward hacking
- Include examples from the blog posts
- Be well-structured in markdown
- Cite specific findings

## Common Issues & Solutions

### Issue: Import Errors
**Solution**: Run `crewai install` to ensure all dependencies are installed

### Issue: API Key Not Found
**Solution**: Check `.env` file has `GEMINI_API_KEY=your-key`

### Issue: Vector Store Loading Slow
**Solution**: Normal on first run; subsequent runs use cached embeddings

### Issue: Pruning Not Reducing Tokens
**Solution**: Check pruning prompt in `custom_tool.py`; ensure it's specific

## Extending This Implementation

### Add More Context Techniques

1. **Tool Loadout**: Add semantic tool selection agent
2. **Context Quarantine**: Create isolated specialist agents
3. **Context Summarization**: Replace pruning with summarization
4. **Context Offloading**: Add memory persistence

### Improve Pruning

1. **Two-Stage Pruning**: Coarse filter → fine filter
2. **Quality Metrics**: Add evaluation of pruned content
3. **Adaptive Pruning**: Adjust based on query complexity
4. **Caching**: Store pruned results for similar queries

### Production Readiness

1. **Error Handling**: Add retry logic for API failures
2. **Monitoring**: Log token counts, costs, latency
3. **Evaluation**: Add automated quality checks
4. **Optimization**: Cache vector store, batch requests

## Key Takeaways

✅ **CrewAI Simplifies**: Higher-level abstractions reduce boilerplate  
✅ **Agent Paradigm**: Natural fit for multi-step workflows  
✅ **Declarative Config**: YAML makes agents/tasks easy to modify  
✅ **Tool Integration**: Clean separation of concerns  
✅ **Cost Effective**: Gemini provides good quality at low cost

## Next Steps

1. Run the implementation and verify results
2. Compare output quality with LangGraph version
3. Experiment with different queries
4. Implement other context engineering techniques
5. Add evaluation metrics

---

**Questions or Improvements?** Edit the tools, agents, or tasks to customize behavior!

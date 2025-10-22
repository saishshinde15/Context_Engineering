# How to Fix Your Context

As Karpathy [said](https://x.com/karpathy/status/1937902205765607626), [Context Engineering](https://blog.langchain.com/context-engineering-for-agents/) is the *delicate art and science of filling the context window with just the right information for the next step.* There [are](https://cognition.ai/blog/dont-build-multi-agents) [many](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) ways to do this. In Drew Breunig's post ["How to Fix Your Context"](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html), he outlines 6 common context engineering techniques. This repository demonstrates each technique using LangGraph.

<img width="4777" height="1983" alt="context_eng_drew" src="https://github.com/user-attachments/assets/b6c07894-f6c6-41d0-9d95-e5e7030189b3" />

## 🚀 Quickstart 

### Prerequisites
- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Installation
1. Clone the repository and activate a virtual environment:
```bash
git clone https://github.com/langchain-ai/how_to_fix_your_context
cd how_to_fix_your_context
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
2. Install dependencies:
```bash
uv pip install -r requirements.txt
```

3. Set up environment variables for the model provider(s) you want to use:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

## Background

### The Context Problem

Chroma's report on [Context Rot](https://research.trychroma.com/context-rot) explains that LLMs do not treat every token in their context window equally. Across 18 models (including GPT‑4.1, Claude 4, Gemini 2.5, Qwen3, etc.), they show that performance on even very simple tasks degrades—often in non‑uniform and surprising ways—as the input length grows. Drew Breunig outlined four failure modes that help to explain [why long contexts fail](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html):

1. **Context Poisoning** - Hallucinations or errors that enter the context and get repeatedly referenced
2. **Context Distraction** - When context grows so large that models focus more on accumulated history than training
3. **Context Confusion** - Superfluous content that influences response quality, as models feel compelled to use all available context
4. **Context Clash** - Conflicting information within the accumulated context that degrades reasoning

## Context Engineering

Drew outlined [6 context engineering techniques](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html) to help fix these failure modes, including: 

* RAG (Retrieval-Augmented Generation)
* Tool Loadout
* Context Quarantine
* Context Pruning
* Context Summarization
* Context Offloading

We implement each of these techniques in a set of Jupyter notebooks using LangGraph, as outlined below.

### LangGraph

LangGraph is a low [is a low-level orchestration framework](https://blog.langchain.com/how-to-think-about-agent-frameworks/) for building AI applications. You can [lay out agents or workflows as a set of nodes](https://www.youtube.com/watch?v=aHCDrAbH_go), [define](https://blog.langchain.com/how-to-think-about-agent-frameworks/) the logic within each one, and define a state object that is passed between them. A [StateGraph](https://langchain-ai.github.io/langgraph/concepts/low_level/#stategraph) is LangGraph's primary abstraction for building these stateful workflows and agents with:

- **Nodes** are processing steps that receive current state and return updates
- **Edges** connect nodes to create execution flow (linear, conditional, or cyclical)
- **State** serves as a shared scratchpad between nodes

This low-level control makes it easy to implement each of the context engineering techniques.

### 1. RAG (Retrieval-Augmented Generation)
**Notebook**: [notebooks/01-rag.ipynb](notebooks/01-rag.ipynb)

*Retrieval-Augmented Generation (RAG) is the act of selectively adding relevant information to help the LLM generate a better response.*

**Implementation**: Creates a RAG agent using LangGraph with a retrieval tool built from Lilian Weng's blog posts. The agent uses Claude Sonnet to intelligently search for relevant context before answering questions.

**Key Components**:
- Document loading and chunking with RecursiveCharacterTextSplitter
- Vector store creation using OpenAI embeddings
- LangGraph StateGraph with conditional edges for tool calling
- System prompt that guides the agent to clarify research scope before retrieval

**Performance**: Used 25k tokens for a complex query about reward hacking types, driven by token-heavy tool calls.

### 2. Tool Loadout
**Notebook**: [notebooks/02-tool-loadout.ipynb](notebooks/02-tool-loadout.ipynb)

*Tool Loadout is the act of selecting only relevant tool definitions to add to your context.*

**Implementation**: Demonstrates semantic tool selection by indexing all Python math library functions in a vector store and dynamically selecting only relevant tools based on user queries.

**Key Components**:
- Tool registry with UUID mapping for all math functions
- Vector store indexing of tool descriptions using embeddings
- Dynamic tool binding based on semantic similarity search (limit 5 tools)
- Extended state class to track selected tools per conversation

**Benefits**: Avoids context confusion from overlapping tool descriptions and improves tool selection accuracy compared to loading all available tools.

### 3. Context Quarantine
**Notebook**: [notebooks/03-context-quarantine.ipynb](notebooks/03-context-quarantine.ipynb)

*Context Quarantine is the act of isolating contexts in their own dedicated threads, each used separately by one or more LLMs.*

**Implementation**: Creates a supervisor multi-agent system using LangGraph Supervisor architecture with specialized agents that have isolated context windows.

**Key Components**:
- Supervisor agent that routes tasks to appropriate specialists
- Math expert agent with addition/multiplication tools and focused mathematical prompt
- Research expert agent with web search capabilities and research-focused prompt
- Clear delegation rules based on task type (research vs. calculations)

**Benefits**: Each agent operates in its own context window, preventing context clash and distraction. The supervisor coordinates between agents using tool-based handoffs for complex tasks requiring multiple skills.

### 4. Context Pruning
**Notebook**: [notebooks/04-context-pruning.ipynb](notebooks/04-context-pruning.ipynb)

*Context Pruning is the act of removing irrelevant or otherwise unneeded information from the context.*

**Implementation**: Extends the RAG agent with an intelligent pruning step that removes irrelevant content from retrieved documents before passing them to the main LLM.

**Key Components**:
- Tool pruning prompt that instructs a smaller LLM to extract only relevant information
- GPT-4o-mini as the pruning model to reduce costs
- Extended state class with summary field for context compression
- Pruning based on the original user request to maintain relevance

**Performance Improvement**: Reduced token usage from 25k to 11k tokens for the same query compared to basic RAG, demonstrating significant context compression while maintaining answer quality.

### 5. Context Summarization
**Notebook**: [notebooks/05-context-summarization.ipynb](notebooks/05-context-summarization.ipynb)

*Context Summarization is the act of boiling down an accrued context into a condensed summary.*

**Implementation**: Builds on the RAG agent by adding a summarization step that condenses tool call results to reduce context size while preserving essential information.

**Key Components**:
- Tool summarization prompt that creates comprehensive yet concise versions of documents
- GPT-4o-mini as the summarization model for cost efficiency
- Guidelines to preserve all key information while eliminating verbosity (50-70% reduction target)
- Extended state class with summary field for tracking condensed content

**Approach**: Unlike pruning which removes irrelevant content, summarization condenses all information into a more compact format, making it suitable when all retrieved content is relevant but verbose.

### 6. Context Offloading
**Notebook**: [notebooks/06-context-offloading.ipynb](notebooks/06-context-offloading.ipynb)

*Context Offloading is the act of storing information outside the LLM's context, usually via a tool that stores and manages the data.*

**Implementation**: Demonstrates two approaches to context offloading - temporary scratchpad storage during a session and persistent cross-thread memory using LangGraph's store interface.

**Key Components**:
- Extended state class with scratchpad field for temporary storage
- WriteToScratchpad and ReadFromScratchpad tools for note-taking
- InMemoryStore for persistent cross-thread memory
- Research workflow that maintains organized notes and builds upon previous research

**Two Storage Patterns**:
1. **Session Scratchpad**: Temporary storage within a single conversation thread
2. **Persistent Memory**: Cross-thread storage using namespaced key-value pairs that persist across different conversation sessions

**Benefits**: Enables agents to maintain research plans, accumulate findings, and access previous work across multiple interactions, similar to how Anthropic's multi-agent researcher and products like ChatGPT implement memory.

## References

- [How to Fix Your Context](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html) by Drew Breunig
- [How Contexts Fail and How to Fix Them](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html) by Drew Breunig

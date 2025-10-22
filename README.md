# Context Engineering

> *The delicate art and science of filling the context window with just the right information for the next step.* - Andrej Karpathy

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Overview

**Context Engineering** is a collection of techniques for optimizing how information is provided to Large Language Models (LLMs). This repository provides practical implementations of six core context engineering techniques, helping you build more effective and efficient AI agents.

As LLMs are increasingly used in production systems, managing context windows effectively has become critical. Research from Chroma on [Context Rot](https://research.trychroma.com/context-rot) shows that LLM performance degrades as input length grows - often in non-uniform and surprising ways across 18+ models including GPT-4, Claude, and Gemini.

This repository implements the six context engineering techniques outlined in Drew Breunig's influential post ["How to Fix Your Context"](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html), providing both LangGraph and CrewAI implementations to help you understand and apply these techniques in your own projects.

## 🎯 Why Context Engineering Matters

### The Context Problem

LLMs don't treat every token in their context window equally. As context grows, four failure modes emerge:

1. **Context Poisoning** - Hallucinations or errors that enter the context and get repeatedly referenced
2. **Context Distraction** - Models focus more on accumulated history than their training
3. **Context Confusion** - Superfluous content influences response quality negatively
4. **Context Clash** - Conflicting information within the context degrades reasoning

### The Solution

Context engineering techniques systematically address these failure modes by:
- 🎯 Selecting the most relevant information (RAG, Tool Loadout)
- 🛡️ Isolating contexts to prevent interference (Context Quarantine)
- ✂️ Removing or condensing unnecessary information (Context Pruning, Summarization)
- 💾 Offloading information to external storage (Context Offloading)

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher (< 3.14 for CrewAI projects)
- [uv](https://docs.astral.sh/uv/) package manager
- API keys (OpenAI, Anthropic, or Google Gemini depending on implementation)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/saishshinde15/Context_Engineering.git
cd Context_Engineering
```

2. **Choose your technique and navigate to its directory:**
```bash
# For LangGraph implementations
cd how_to_fix_your_context

# For CrewAI implementations
cd context_pruning  # or context_offloading
```

3. **Install dependencies:**
```bash
# For LangGraph
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# For CrewAI
crewai install
```

4. **Configure API keys:**
```bash
# Create .env file with your API keys
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
export GEMINI_API_KEY="your-key-here"
```

5. **Run the examples:**
```bash
# LangGraph: Open Jupyter notebooks
jupyter notebook notebooks/

# CrewAI: Run the crew
crewai run
```

## 📚 Repository Structure

```
Context_Engineering/
│
├── 📁 how_to_fix_your_context/          # LangGraph implementations
│   ├── notebooks/
│   │   ├── 01-rag.ipynb                 # RAG implementation
│   │   ├── 02-tool-loadout.ipynb        # Tool Loadout
│   │   ├── 03-context-quarantine.ipynb  # Context Quarantine
│   │   ├── 04-context-pruning.ipynb     # Context Pruning
│   │   ├── 05-context-summarization.ipynb # Context Summarization
│   │   └── 06-context-offloading.ipynb  # Context Offloading
│   └── README.md
│
├── 📁 context_pruning/                   # CrewAI Context Pruning
│   ├── src/context_pruning/
│   │   ├── config/                      # Agent & task configs
│   │   ├── tools/                       # RAG & pruning tools
│   │   ├── crew.py                      # Crew orchestration
│   │   └── main.py                      # Entry point
│   ├── README.md                        # Detailed documentation
│   ├── QUICKSTART.md                    # Quick start guide
│   ├── VISUAL_GUIDE.md                  # Visual workflow
│   └── IMPLEMENTATION_NOTES.md          # Technical details
│
├── 📁 context_offloading/                # CrewAI Context Offloading
│   ├── src/context_offloading/
│   │   ├── config/                      # Agent & task configs
│   │   ├── tools/                       # Scratchpad tools
│   │   ├── crew.py                      # Crew orchestration
│   │   └── main.py                      # Entry point
│   ├── README.md                        # Detailed documentation
│   ├── QUICKSTART.md                    # Quick start guide
│   └── DOCUMENTATION.md                 # Complete docs
│
└── README.md                             # This file
```

## 🛠️ Context Engineering Techniques

### 1. 🔍 RAG (Retrieval-Augmented Generation)

**What it is:** Selectively adding relevant information to help the LLM generate better responses.

**Implementation:** [`how_to_fix_your_context/notebooks/01-rag.ipynb`](how_to_fix_your_context/notebooks/01-rag.ipynb)

**Key Features:**
- Document loading and chunking
- Vector store with semantic search
- LangGraph StateGraph with tool calling
- Uses Claude Sonnet for intelligent retrieval

**Use Case:** When you need to ground LLM responses in specific knowledge sources.

---

### 2. 🧰 Tool Loadout

**What it is:** Selecting only relevant tool definitions to add to your context.

**Implementation:** [`how_to_fix_your_context/notebooks/02-tool-loadout.ipynb`](how_to_fix_your_context/notebooks/02-tool-loadout.ipynb)

**Key Features:**
- Semantic tool selection via vector store
- Dynamic tool binding based on query
- Prevents context confusion from overlapping tool descriptions
- Indexes Python math library functions

**Use Case:** When you have many tools and want to avoid overwhelming the context.

---

### 3. 🔒 Context Quarantine

**What it is:** Isolating contexts in dedicated threads, each used separately by specialized agents.

**Implementation:** [`how_to_fix_your_context/notebooks/03-context-quarantine.ipynb`](how_to_fix_your_context/notebooks/03-context-quarantine.ipynb)

**Key Features:**
- Supervisor multi-agent architecture
- Specialized agents (Math Expert, Research Expert)
- Isolated context windows per agent
- Tool-based handoffs for complex tasks

**Use Case:** When different tasks require different expertise and context.

---

### 4. ✂️ Context Pruning

**What it is:** Removing irrelevant or unneeded information from the context.

**Implementations:**
- LangGraph: [`how_to_fix_your_context/notebooks/04-context-pruning.ipynb`](how_to_fix_your_context/notebooks/04-context-pruning.ipynb)
- CrewAI: [`context_pruning/`](context_pruning/)

**Key Features:**
- **Token Reduction:** 40-60% reduction in context size
- **Improved Accuracy:** Focused context leads to better answers
- **Cost Efficiency:** Uses smaller models (GPT-4o-mini or Gemini Flash) for pruning
- **Three-Agent Workflow:** Retrieval → Pruning → Synthesis

**Performance:** Reduces token usage from 25k to 11k tokens while maintaining answer quality.

**Use Case:** When retrieved content contains a mix of relevant and irrelevant information.

**📖 Extended Documentation:**
- [README.md](context_pruning/README.md) - Complete guide
- [QUICKSTART.md](context_pruning/QUICKSTART.md) - 3-step quick start
- [VISUAL_GUIDE.md](context_pruning/VISUAL_GUIDE.md) - Detailed workflow visualization
- [IMPLEMENTATION_NOTES.md](context_pruning/IMPLEMENTATION_NOTES.md) - Technical deep dive

---

### 5. 📊 Context Summarization

**What it is:** Condensing accumulated context into a summary while preserving essential information.

**Implementation:** [`how_to_fix_your_context/notebooks/05-context-summarization.ipynb`](how_to_fix_your_context/notebooks/05-context-summarization.ipynb)

**Key Features:**
- Compresses all content (not just irrelevant parts)
- Preserves key information while eliminating verbosity
- 50-70% reduction target
- Uses GPT-4o-mini for cost efficiency

**Use Case:** When all retrieved content is relevant but too verbose.

---

### 6. 💾 Context Offloading

**What it is:** Storing information outside the LLM's context window in external storage.

**Implementations:**
- LangGraph: [`how_to_fix_your_context/notebooks/06-context-offloading.ipynb`](how_to_fix_your_context/notebooks/06-context-offloading.ipynb)
- CrewAI: [`context_offloading/`](context_offloading/)

**Key Features:**
- **Session Scratchpad:** Temporary storage within a conversation
- **Persistent Memory:** Cross-thread storage using key-value pairs
- **Organized Storage:** Category-based organization
- **Reusability:** Information survives across sessions

**Use Case:** Long research tasks, multi-step workflows, or when information needs to persist across conversations.

**📖 Extended Documentation:**
- [README.md](context_offloading/README.md) - Complete guide
- [QUICKSTART.md](context_offloading/QUICKSTART.md) - 3-step quick start
- [DOCUMENTATION.md](context_offloading/DOCUMENTATION.md) - Architecture details

## 🔧 Implementation Frameworks

### LangGraph Implementation

**Framework:** Low-level orchestration with full control over flow

**Characteristics:**
- ✅ StateGraph with explicit nodes and edges
- ✅ Custom state management
- ✅ Direct tool binding to LLMs
- ✅ Conditional flow control
- ✅ Fine-grained control over execution

**Best For:** Complex workflows requiring precise control

**Location:** [`how_to_fix_your_context/`](how_to_fix_your_context/)

### CrewAI Implementation

**Framework:** High-level agent framework with declarative configuration

**Characteristics:**
- ✅ Agent-based workflow with automatic context passing
- ✅ YAML configuration for agents and tasks
- ✅ Agents decide when to use tools
- ✅ Sequential or hierarchical processes
- ✅ Easier to read and maintain

**Best For:** Rapid prototyping and clear agent roles

**Locations:** [`context_pruning/`](context_pruning/), [`context_offloading/`](context_offloading/)

## 📊 Comparison: LangGraph vs CrewAI

| Aspect | LangGraph | CrewAI |
|--------|-----------|--------|
| **Abstraction Level** | Lower (more control) | Higher (more productivity) |
| **Configuration** | Python code | YAML + Python |
| **State Management** | Manual with custom classes | Automatic context passing |
| **Tool Calling** | Explicit binding | Agent decides |
| **Flow Control** | Conditional edges | Task dependencies |
| **Learning Curve** | Steeper | Gentler |
| **Flexibility** | Maximum | Opinionated |
| **Use Case** | Complex, custom workflows | Standard agent workflows |

## 🎓 Learning Path

### Beginners
1. Start with **RAG** to understand basic retrieval concepts
2. Explore **Context Pruning** (CrewAI) for a complete, well-documented implementation
3. Try **Tool Loadout** to see semantic tool selection in action

### Intermediate
4. Study **Context Quarantine** for multi-agent patterns
5. Implement **Context Summarization** for compression techniques
6. Experiment with **Context Offloading** for persistent memory

### Advanced
7. Compare LangGraph vs CrewAI implementations side-by-side
8. Combine multiple techniques in a single application
9. Adapt techniques to your specific use cases

## 📈 Performance Benchmarks

### Context Pruning
- **Token Reduction:** 40-60% (25k → 11k tokens)
- **Cost Savings:** ~50% on LLM API calls
- **Execution Time:** 20-30 seconds
- **Quality:** Maintained or improved answer quality

### Context Summarization
- **Compression:** 50-70% size reduction
- **Information Retention:** High (preserves key facts)
- **Best For:** Verbose but relevant content

### Context Offloading
- **Memory Efficiency:** Unlimited external storage
- **Persistence:** Cross-session memory
- **Best For:** Long-running research tasks

## 🔬 Research & References

### Core Concepts
- [How to Fix Your Context](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html) - Drew Breunig
- [How Contexts Fail](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html) - Drew Breunig
- [Context Rot Research](https://research.trychroma.com/context-rot) - Chroma
- [Context Engineering for Agents](https://blog.langchain.com/context-engineering-for-agents/) - LangChain

### Frameworks
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [CrewAI Documentation](https://docs.crewai.com)
- [LangChain Documentation](https://python.langchain.com/)

### Influential Posts
- [Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents) - Cognition AI
- [Context Engineering for AI Agents](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) - Manus
- [Karpathy on Context Engineering](https://x.com/karpathy/status/1937902205765607626) - Twitter/X

## 🤝 Contributing

Contributions are welcome! Here are some ways you can contribute:

- 🐛 Report bugs or issues
- 💡 Suggest new context engineering techniques
- 📖 Improve documentation
- 🔧 Add new implementations or examples
- ⭐ Star the repository if you find it useful

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Drew Breunig** for the original context engineering framework
- **LangChain/LangGraph** team for the excellent orchestration tools
- **CrewAI** team for the powerful agent framework
- **Lilian Weng** for her informative blog posts used in examples
- **Chroma** team for their research on context rot

## 📞 Support & Community

- **Issues:** [GitHub Issues](https://github.com/saishshinde15/Context_Engineering/issues)
- **Discussions:** [GitHub Discussions](https://github.com/saishshinde15/Context_Engineering/discussions)
- **LangGraph:** [Discord](https://discord.gg/langchain)
- **CrewAI:** [Discord](https://discord.com/invite/X4JWnZnxPb)

## 🗺️ Roadmap

- [ ] Add evaluation metrics for each technique
- [ ] Implement hybrid approaches (combining multiple techniques)
- [ ] Add streaming support for real-time applications
- [ ] Create benchmarking suite
- [ ] Add support for more LLM providers
- [ ] Implement caching strategies
- [ ] Add video tutorials and walkthroughs

---

<div align="center">

**Built with ❤️ for the AI Agent community**

If this repository helps you, please consider giving it a ⭐!

[Report Bug](https://github.com/saishshinde15/Context_Engineering/issues) · [Request Feature](https://github.com/saishshinde15/Context_Engineering/issues) · [Documentation](https://github.com/saishshinde15/Context_Engineering)

</div>

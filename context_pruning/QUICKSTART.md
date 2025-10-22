# Quick Start Guide - Context Pruning with CrewAI

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
cd /Users/saish/Downloads/Context_engineering/context_pruning
crewai install
```

Or manually:
```bash
uv pip install -e .
```

### Step 2: Set Your API Key

Make sure your `.env` file contains:
```bash
GEMINI_API_KEY=your-actual-gemini-api-key-here
MODEL=gemini/gemini-flash-latest
```

### Step 3: Run the Demo

```bash
crewai run
```

## 📊 What Will Happen

1. **Retrieval Agent** searches Lilian Weng's blog posts for information about reward hacking
2. **Pruning Agent** filters the content to remove irrelevant information
3. **Response Synthesizer** creates a comprehensive answer
4. Result saved to `context_pruning_result.md`

## 🎯 Example Query

Default query: *"What are the types of reward hacking discussed in the blogs?"*

Expected workflow:
```
[Retrieval Agent] Searching blog posts...
  → Retrieved ~15,000 tokens of content

[Pruning Agent] Filtering content...
  → Pruned to ~6,000 relevant tokens (60% reduction)

[Response Synthesizer] Creating answer...
  → Generated comprehensive markdown response
```

## 🔧 Customize Your Query

Edit `src/context_pruning/main.py`:

```python
inputs = {
    'topic': 'hallucination in LLMs',
    'query': 'What causes hallucination in large language models?'
}
```

Then run again:
```bash
crewai run
```

## 📝 View Results

Check the generated file:
```bash
cat context_pruning_result.md
```

## 🐛 Troubleshooting

**Import errors?**
```bash
crewai install
```

**API key issues?**
- Verify GEMINI_API_KEY in `.env`
- Test with: `echo $GEMINI_API_KEY`

**Want more verbose output?**
- Agents already set to `verbose=True` in `crew.py`
- Check terminal for detailed execution logs

## 🎓 Learn More

- Compare with LangGraph implementation: `../how_to_fix_your_context/notebooks/04-context-pruning.ipynb`
- Read full README: `README.md`
- Explore other context engineering techniques

## 💡 Pro Tips

1. **First run is slower** - Vector store initialization takes time
2. **Check token counts** - Watch the logs to see pruning effectiveness
3. **Experiment with queries** - Try different topics from the blog posts:
   - Thinking mechanisms in AI
   - Hallucination causes and solutions
   - Diffusion models for video
   - Reward hacking categories

Happy Context Pruning! 🎉

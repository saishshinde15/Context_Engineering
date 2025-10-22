#!/usr/bin/env python
"""
Context Offloading Main Entry Point

This demonstrates context offloading using a persistent scratchpad.
The crew will:
1. Create a research plan and save to scratchpad
2. Conduct research, updating scratchpad iteratively
3. Synthesize all scratchpad notes into a final report

Default query compares Commonwealth Fusion Systems vs Helion Energy,
mirroring the example from the LangGraph notebook.
"""

import sys
import warnings
from datetime import datetime

from context_offloading.crew import ContextOffloading

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew with context offloading demonstration.
    
    Default query: Compare Commonwealth Fusion Systems vs Helion Energy
    (same as the LangGraph notebook example)
    """
    inputs = {
        'topic': 'Comprehensive analysis of the AI chip market: Compare NVIDIA, AMD, Intel, and emerging players like Groq and Cerebras in terms of architecture, performance, power efficiency, market positioning, recent developments (2024-2025), and future roadmap',
        'current_year': str(datetime.now().year)
    }
    
    print("=" * 80)
    print("🚀 CONTEXT OFFLOADING DEMO")
    print("=" * 80)
    print("\nThis crew demonstrates context offloading via persistent scratchpad:")
    print("1. Planning Agent: Creates research plan → Saves to scratchpad")
    print("2. Research Agent: Reads plan → Searches → Updates scratchpad iteratively")
    print("3. Synthesis Agent: Reads all scratchpad notes → Creates final report")
    print("\n" + "=" * 80 + "\n")
    
    try:
        ContextOffloading().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        ContextOffloading().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        ContextOffloading().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        ContextOffloading().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

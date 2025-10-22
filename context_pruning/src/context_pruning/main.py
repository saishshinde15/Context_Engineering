#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from context_pruning.crew import ContextPruning

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew with context pruning demonstration.
    """
    inputs = {
        'topic': 'reward hacking in AI systems',
        'query': 'What are the types of reward hacking discussed in the blogs?'
    }
    
    try:
        result = ContextPruning().crew().kickoff(inputs=inputs)
        print("\n" + "="*80)
        print("CONTEXT PRUNING DEMO - FINAL RESULT")
        print("="*80)
        print(result)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'topic': 'reward hacking in AI systems',
        'query': 'What are the types of reward hacking discussed in the blogs?'
    }
    try:
        ContextPruning().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        ContextPruning().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'topic': 'reward hacking in AI systems',
        'query': 'What are the types of reward hacking discussed in the blogs?'
    }
    
    try:
        ContextPruning().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

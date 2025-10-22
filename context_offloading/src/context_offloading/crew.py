"""
Context Offloading Crew Implementation

This crew demonstrates context offloading by using a persistent scratchpad
to store information outside the LLM's context window. The workflow follows
a research pattern with three specialized agents:

1. Research Planner: Creates research plan, saves to scratchpad
2. Researcher: Conducts searches, updates scratchpad iteratively
3. Synthesis Agent: Reads all scratchpad notes, creates final report

This mirrors human cognitive processes: planning → note-taking → synthesis
"""

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import TavilySearchTool
from typing import List
import os
from pathlib import Path

# Import custom scratchpad tools
from context_offloading.tools.custom_tool import (
    ScratchpadWriteTool,
    ScratchpadReadTool,
    UserPreferenceTool
)

@CrewBase
class ContextOffloading():
    """
    Context Offloading Crew
    
    Demonstrates how agents can offload context to persistent storage,
    avoiding context rot and enabling information reuse across tasks.
    """

    agents: List[BaseAgent]
    tasks: List[Task]
    
    def __init__(self):
        super().__init__()
        
        # Initialize Gemini LLM (same as context pruning implementation)
        self.llm = LLM(
            model="gemini/gemini-2.0-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            max_retries=3,
            retry_delay=60  # Wait 60 seconds between retries to handle rate limits
        )
        
        # Initialize scratchpad tools (shared across all agents)
        self.scratchpad_write = ScratchpadWriteTool()
        self.scratchpad_read = ScratchpadReadTool()
        self.user_preference_tool = UserPreferenceTool()
        
        # Initialize web search tool
        self.tavily_search = TavilySearchTool()
        
        # Clear scratchpad at start of new crew run
        self._clear_scratchpad()
    
    def _clear_scratchpad(self):
        """Clear scratchpad.json at start of new run for clean slate."""
        scratchpad_file = Path(__file__).parent.parent.parent / "knowledge" / "scratchpad.json"
        if scratchpad_file.exists():
            scratchpad_file.unlink()
    
    @agent
    def research_planner(self) -> Agent:
        """
        Research Planning Agent
        
        Responsibilities:
        - Read user preferences
        - Check existing scratchpad
        - Create structured research plan
        - Save plan to scratchpad
        """
        return Agent(
            config=self.agents_config['research_planner'], # type: ignore[index]
            tools=[self.scratchpad_read, self.scratchpad_write, self.user_preference_tool],
            llm=self.llm,
            verbose=True
        )
    
    @agent
    def researcher(self) -> Agent:
        """
        Research Agent
        
        Responsibilities:
        - Read research plan from scratchpad
        - Conduct web searches
        - Update scratchpad with findings iteratively
        - Create final summary
        """
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            tools=[self.scratchpad_read, self.scratchpad_write, self.tavily_search],
            llm=self.llm,
            verbose=True
        )
    
    @agent
    def synthesis_agent(self) -> Agent:
        """
        Synthesis Agent
        
        Responsibilities:
        - Read ALL scratchpad notes
        - Synthesize into comprehensive report
        - Ensure all information is incorporated
        """
        return Agent(
            config=self.agents_config['synthesis_agent'], # type: ignore[index]
            tools=[self.scratchpad_read],
            llm=self.llm,
            verbose=True
        )
    
    @task
    def planning_task(self) -> Task:
        """Create research plan and save to scratchpad."""
        return Task(
            config=self.tasks_config['planning_task'], # type: ignore[index]
        )
    
    @task
    def research_task(self) -> Task:
        """Conduct research following plan, update scratchpad iteratively."""
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )
    
    @task
    def synthesis_task(self) -> Task:
        """Synthesize all scratchpad notes into final report."""
        return Task(
            config=self.tasks_config['synthesis_task'], # type: ignore[index]
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """
        Creates the Context Offloading crew with sequential process.
        
        Flow:
        1. Planning Agent → Creates plan → Saves to scratchpad
        2. Research Agent → Reads plan → Searches → Updates scratchpad → Repeats
        3. Synthesis Agent → Reads all scratchpad → Creates final report
        
        This demonstrates context offloading across all three stages.
        """
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            outpu
        )

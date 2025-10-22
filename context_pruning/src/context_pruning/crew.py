from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os

# Import custom tools
from context_pruning.tools.custom_tool import RAGRetrievalTool, ContextPruningTool

# Initialize the LLM explicitly
llm = LLM(
    model="gemini/gemini-flash-latest",
    api_key=os.getenv("GEMINI_API_KEY")
)

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class ContextPruning():
    """ContextPruning crew - demonstrates context pruning technique for RAG systems"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def retrieval_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['retrieval_agent'], # type: ignore[index]
            tools=[RAGRetrievalTool()],
            llm=llm,
            verbose=True
        )

    @agent
    def pruning_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['pruning_agent'], # type: ignore[index]
            tools=[ContextPruningTool()],
            llm=llm,
            verbose=True
        )

    @agent
    def response_synthesizer(self) -> Agent:
        return Agent(
            config=self.agents_config['response_synthesizer'], # type: ignore[index]
            llm=llm,
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def retrieval_task(self) -> Task:
        return Task(
            config=self.tasks_config['retrieval_task'], # type: ignore[index]
        )

    @task
    def pruning_task(self) -> Task:
        return Task(
            config=self.tasks_config['pruning_task'], # type: ignore[index]
        )

    @task
    def synthesis_task(self) -> Task:
        return Task(
            config=self.tasks_config['synthesis_task'], # type: ignore[index]
            output_file='context_pruning_result.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ContextPruning crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

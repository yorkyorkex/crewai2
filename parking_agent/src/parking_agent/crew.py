from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from parking_agent.tools.parking_tool import MelbourneParkingTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class ParkingAgent():
    """ParkingAgent crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def parking_finder_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['parking_finder_agent'], # type: ignore[index]
            tools=[MelbourneParkingTool()],
            verbose=False,
            temperature=0.1,
            max_iter=1,
            max_tokens=500,
            memory=False,
            max_rpm=100
        )

    @agent
    def parking_reporter_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['parking_reporter_agent'], # type: ignore[index]
            verbose=False,
            temperature=0.1,
            max_iter=1,
            max_tokens=300,
            memory=False,
            max_rpm=100
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def fetch_parking_task(self) -> Task:
        return Task(
            config=self.tasks_config['fetch_parking_task'] # type: ignore[index]
        )

    @task
    def format_parking_task(self) -> Task:
        return Task(
            config=self.tasks_config['format_parking_task'] # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ParkingAgent crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=False,  # Reduce verbosity for speed
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

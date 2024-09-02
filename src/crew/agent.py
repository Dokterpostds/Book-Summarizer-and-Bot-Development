# Create agent crewAI

from crewai import Agent, Task, Crew, Process

# Create the manager agent

manager = Agent(
    name="Manager",
    tools=[
        # List of tools that the manager can use
    ],
    role="Project Manager",
    description="Manages the project, organizes tasks, and ensures project progress",
)

# Create the researcher agent

researcher = Agent(
    name="Researcher",
    tools=[
        # List of tools that the researcher can use
    ],
    role="Researcher",
    description="Performs research on the topic, extracts information, and generates summaries",
)
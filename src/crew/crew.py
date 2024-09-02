# Create crew from crewAI

from crewai import Agent, Task, Crew, Process

# Define the agents

pdf_researcher = Agent(
    role='PDF Researcher',
    goal='Extract specific information from a PDF document.',
    verbose=True
)

writer = Agent(
    role='Writer',
    goal='Create engaging narratives from research findings.',
    verbose=True,
    backstory="""With a flair for simplifying complex topics, you craft engaging narratives that captivate
    and educate, bringing new discoveries to light in an accessible manner."""
)
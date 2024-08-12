import os
import json
import asyncio

from .pdf_research import generate_research_pdf
from crew_utils.crew import ResearchCrew

async def run_research(topic):
    """
    Run the crew for a specific topic.
    """
    inputs = {
        'topic': topic
    }
    
    try:
        # Run the CrewAI research in a separate thread
        loop = asyncio.get_event_loop()
        crew = ResearchCrew().crew()
        await loop.run_in_executor(None, crew.kickoff, inputs)
        
        with open('final_research.json', 'r') as file:
            research_data = json.load(file)
        
        pdf_filename = await loop.run_in_executor(None, generate_research_pdf, topic, research_data)
        
        return pdf_filename
    
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        raise
    
    finally:
        if os.path.exists('final_research.json'):
            os.remove('final_research.json')
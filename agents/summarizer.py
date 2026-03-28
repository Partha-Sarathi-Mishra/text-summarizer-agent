import os
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

class TextSummarizerAgent:
    def __init__(self):
        """
        Initialize the TextSummarizerAgent using Google's Agent Development Kit (ADK).
        We use Gemini 1.5 Flash as the underlying model.
        """
        self.agent = Agent(
            name="TextSummarizerAgent",
            model="gemini-2.5-flash",
            instruction=(
                "You are an expert text summarizer. "
                "Your objective is to read the provided text and write a concise, clear summary. "
                "Return only the summary. Do not add conversational filler."
            )
        )
        self.runner = InMemoryRunner(agent=self.agent, app_name="TextSummarizerApp")
        self.runner.auto_create_session = True
    
    def summarize(self, text: str) -> str:
        """
        Summarize the given text.
        """
        prompt = f"Summarize the following text:\n\n{text}"
        
        try:
            msg = types.Content(role='user', parts=[types.Part.from_text(text=prompt)])
            events = list(self.runner.run(user_id="user_1", session_id="session_1", new_message=msg))
            
            if not events:
                return "Agent returned no response."
                
            last_event = events[-1]
            if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts') and last_event.content.parts:
                return last_event.content.parts[0].text
            elif hasattr(last_event, 'message') and hasattr(last_event.message, 'content') and last_event.message.content.parts:
                return last_event.message.content.parts[0].text
            return str(last_event)
        except Exception as e:
            raise RuntimeError(f"Error running agent: {str(e)}")

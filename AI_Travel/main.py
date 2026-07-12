import os 
from dotenv import load_dotenv

class LocalRAGSystem:
    def __init__(self):
        print("initializing local rag system")
        load_dotenv()
        self.gemini_api_key=os.getenv("GEMINI_API_KEY")
        self.groq_api_key=os.getenv("GROQ_API_KEY")

        if not self.gemini_api_key or not self.groq_api_key:
            raise ValueError("missing api key")
        print("api keys loaded successfully")

if __name__ == "__main__":
    rag=LocalRAGSystem()
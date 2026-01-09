import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-college-project-key'
    # Optional: Add your OpenAI/Gemini API key here for real AI features
    # OPENAI_API_KEY = "sk-..." 
    AI_PROVIDER = "mock" # Options: "mock", "openai", "gemini"

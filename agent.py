import os
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled, function_tool
from dotenv import load_dotenv
from retrieving import retrieve_textbook_info

# --- CONFIGURATION ---
load_dotenv()
set_tracing_disabled(disabled=True)

# 1. LOAD KEYS
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 2. INITIALIZE CLIENTS
try:
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    print(f"✅ OpenAI Client Initialized for agent.")
except Exception as e:
    print(f"❌ STARTUP ERROR (agent.py): {e}")

# 3. SETUP OPENAI MODEL
model = OpenAIChatCompletionsModel(
    model="gpt-4o",
    openai_client=openai_client
)

# 4. DEFINE THE STRICT AGENT
agent = Agent(
    name="TextbookBot",
    instructions="""
    You are the specialized AI Assistant for the 'Physical AI & Humanoid Robotics' textbook.
    
    YOUR STRICT RULES:
    1. **Primary Source:** You must answer strictly using ONLY the content provided by the `retrieve_textbook_info` tool.
    2. **Refusal Policy:** If the user asks about topics NOT in the book (e.g., politics, celebrities, movies), strictly refuse. Say: "I can only answer questions related to the Physical AI textbook."
    3. **Uncertainty:** If the tool returns "No relevant information found", explicitly state: "This specific topic is not covered in the textbook." Do NOT make up an answer.
    4. **System Errors:** If the tool returns a "SYSTEM ERROR", apologize and tell the user technical maintenance is required.
    """,
    model=model,
    tools=[function_tool(retrieve_textbook_info)]
)

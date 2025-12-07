import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from agents import Runner
from agent import agent

# --- CONFIGURATION ---
load_dotenv()

# 7. FASTAPI SERVER
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/status")
def status():
    return {"status": "ok"}

@app.post("/ask")
async def chat_endpoint(request: ChatRequest):
    print(f"\n📩 User: {request.message}")
    try:
        # Using 'await' prevents the server from freezing
        result = await Runner.run(agent, input=request.message)
        print("✅ Reply sent.")
        return {"reply": result.final_output}
    except Exception as e:
        print(f"❌ [API ERROR]: {e}")
        raise HTTPException(status_code=500, detail=str(e))

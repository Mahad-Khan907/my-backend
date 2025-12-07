import asyncio
from agent import agent
from agents import Runner

async def main():
    print("--- 🧪 Agent Test: Book-related query ---")
    result = await Runner.run(agent, input="What is physical AI?")
    print(f"✅ Reply: {result.final_output}")

    print("\n--- 🧪 Agent Test: Unrelated query ---")
    result = await Runner.run(agent, input="What is the capital of France?")
    print(f"✅ Reply: {result.final_output}")

if __name__ == "__main__":
    asyncio.run(main())

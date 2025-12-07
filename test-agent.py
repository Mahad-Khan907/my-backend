import requests
import json

# The URL of your running Agent server
url = "http://127.0.0.1:8000/chat"

# The message we want to send
payload = {
    "message": "What is physical AI?"
}

print(f"📡 Sending message to {url}...")

try:
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! The AI Replied:")
        print("--------------------------------------------------")
        # Print the AI's reply cleanly
        print(response.json()['reply'])
        print("--------------------------------------------------")
    else:
        print(f"\n❌ Server Error (Status {response.status_code}):")
        print(response.text)

except Exception as e:
    print(f"\n❌ Connection Failed: {e}")
    print("Make sure 'uv run uvicorn main:app' is running in a separate terminal!")
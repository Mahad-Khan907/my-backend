import os
import cohere
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()

# 1. LOAD KEYS
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# 2. DATABASE CONFIGURATION
EMBEDDING_MODEL = "embed-english-v3.0"
QDRANT_COLLECTION_NAME = "humanoid_ai_book"

# 3. INITIALIZE CLIENTS
try:
    qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    cohere_client = cohere.Client(COHERE_API_KEY)
    print(f"✅ Clients Initialized for retrieval. Using Model: {EMBEDDING_MODEL}")
except Exception as e:
    print(f"❌ STARTUP ERROR (retrieving.py): {e}")

def retrieve_textbook_info(query: str) -> str:
    """
    Searches the Qdrant database for relevant text chunks from the textbook.
    """
    print(f"   🔎 [Tool] Searching for: '{query}'")
    
    try:
        # A. Generate Embedding
        response = cohere_client.embed(
            texts=[query],
            model=EMBEDDING_MODEL,
            input_type="search_query"
        )
        query_vector = response.embeddings[0]

        # B. Search Qdrant (Fetching 10 chunks for better context)
        result = qdrant_client.query_points(
            collection_name=QDRANT_COLLECTION_NAME,
            query=query_vector,
            limit=10 
        )
        
        # C. Handle Empty Results
        if not result.points:
            print("   ⚠️ [Tool] Search successful, but found 0 matching chunks.")
            return "No relevant information found in the textbook for this query."
            
        # D. Format Output
        contents = ""
        for point in result.points:
            source = point.payload.get("url", "Unknown Source")
            text = point.payload.get("text", "")
            contents += f"--- SOURCE: {source} ---\n{text}\n\n"
            
        print(f"   ✅ [Tool] Found {len(result.points)} relevant chunks.")
        return contents
        
    except Exception as e:
        print(f"   ❌ [CRITICAL TOOL ERROR]: {e}")
        # Return the actual error to the Agent so it knows something broke
        return f"SYSTEM ERROR: The database search failed due to: {str(e)}"
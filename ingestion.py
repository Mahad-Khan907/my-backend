import os
import requests
import xml.etree.ElementTree as ET
import trafilatura
import cohere
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

Q_URL = os.getenv("QDRANT_URL")
Q_KEY = os.getenv("QDRANT_API_KEY")
C_KEY = os.getenv("COHERE_API_KEY")

# 2. Configuration (MUST MATCH MAIN.PY)
COLLECTION_NAME = "humanoid_ai_book"  # <--- This matches your error
EMBED_MODEL = "embed-english-v3.0"    # <--- This matches your main.py log
SITEMAP_URL = "https://mahad-khan-ai-book.vercel.app/sitemap.xml"

# 3. Initialize Clients
print("--- 🚀 STARTING INGESTION ---")
try:
    qdrant = QdrantClient(url=Q_URL, api_key=Q_KEY)
    cohere_client = cohere.Client(C_KEY)
    print("✅ Clients Connected")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    exit()

# 4. Helper Functions
def get_urls():
    print(f"1. Fetching Sitemap: {SITEMAP_URL}")
    try:
        xml = requests.get(SITEMAP_URL).text
        root = ET.fromstring(xml)
        urls = [child.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text for child in root]
        print(f"   Found {len(urls)} URLs.")
        return urls
    except Exception as e:
        print(f"❌ Failed to get URLs: {e}")
        return []

def get_text(url):
    try:
        html = requests.get(url).text
        text = trafilatura.extract(html)
        return text
    except:
        return None

def chunk_text(text, size=1000):
    chunks = []
    for i in range(0, len(text), size):
        chunks.append(text[i:i+size])
    return chunks

# 5. Main Logic
def run():
    # A. Create Collection
    print(f"2. Creating Collection: {COLLECTION_NAME}")
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
    )

    # B. Process URLs
    urls = get_urls()
    total_chunks = 0
    
    for url in urls:
        print(f"   Processing: {url}...")
        text = get_text(url)
        if not text:
            continue
            
        chunks = chunk_text(text)
        
        # Embed and Upload
        points = []
        for i, chunk in enumerate(chunks):
            try:
                # Generate Embedding
                emb = cohere_client.embed(
                    texts=[chunk],
                    model=EMBED_MODEL,
                    input_type="search_document"
                ).embeddings[0]
                
                # Create Point
                points.append(PointStruct(
                    id=total_chunks + i,
                    vector=emb,
                    payload={"url": url, "text": chunk}
                ))
            except Exception as e:
                print(f"   ⚠️ Error embedding chunk: {e}")

        # Upload Batch
        if points:
            qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
            total_chunks += len(points)
            
    print(f"\n✅ DONE! Uploaded {total_chunks} chunks to '{COLLECTION_NAME}'.")

if __name__ == "__main__":
    run()

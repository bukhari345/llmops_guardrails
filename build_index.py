# build_index.py - cut the documents into chunks, turn each chunk into an embedding,
# and store them in the vector database (run again whenever the documents change)
 
from pathlib import Path
 
import chromadb
import requests
 
EMBED_URL = "http://127.0.0.1:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"
 
# 1. Chunks: every paragraph (separated by a blank line) is one chunk
chunks, sources = [], []
for file in sorted(Path("docs").glob("*.txt")):
    for paragraph in file.read_text(encoding="utf-8").split("\n\n"):
        if paragraph.strip():
            chunks.append(paragraph.strip())
            sources.append(file.name)
print(f"Cut {len(sources)} chunks from {len(set(sources))} documents")
 
# 2. Embeddings: each chunk becomes a list of numbers that captures its meaning
response = requests.post(EMBED_URL, json={"model": EMBED_MODEL, "input": chunks})
embeddings = response.json()["embeddings"]
print(f"Each embedding has {len(embeddings[0])} numbers")
 
# 3. Vector database: start fresh, then store every chunk with its embedding
client = chromadb.PersistentClient(path="vector_db")
try:
    client.delete_collection("property_docs")
except Exception:
    pass   # first run: nothing to delete yet
collection = client.create_collection("property_docs")
collection.add(
    ids=[f"chunk-{i}" for i in range(len(chunks))],
    documents=chunks,
    embeddings=embeddings,
    metadatas=[{"source": s} for s in sources],
)
print(f"Stored {collection.count()} chunks in vector_db/")

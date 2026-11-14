# ask_rag.py - ask the RAG assistant one question
#
# Usage: python ask_rag.py "What is the price per marla in Bahria Town?"
 
import sys
 
from rag import ask
 
result = ask(sys.argv[1])
 
print(result["answer"])
print("\n--- sources used:")
for src, chunk in zip(result["sources"], result["chunks"]):
    print(f"  [{src}] {chunk[:70]}...")
print(f"--- tokens in: {result['tokens_in']} | tokens out: {result['tokens_out']}")

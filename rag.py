# rag.py - the RAG assistant as one reusable function, now with guardrails
# (used by ask_rag.py for single questions and by run_evals.py for testing)

import chromadb
import requests

from guardrails import check_input, check_output

OLLAMA = "http://127.0.0.1:11434"
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama3.2"
TOP_K = 3   # how many chunks to give the LLM


def ask(question, prompt_file="prompts/rag_v2.txt"):
    # Input guardrail: stop bad questions before they reach the LLM
    problem = check_input(question)
    if problem:
        return {"answer": "I can't help with that request.", "sources": [], "chunks": [],
                "tokens_in": 0, "tokens_out": 0, "blocked": problem}

    system_prompt = open(prompt_file, encoding="utf-8").read()

    # 1. Turn the question into an embedding
    q_embedding = requests.post(f"{OLLAMA}/api/embed",
                                json={"model": EMBED_MODEL, "input": [question]}).json()["embeddings"][0]

    # 2. Retrieve the chunks closest in meaning to the question
    collection = chromadb.PersistentClient(path="vector_db").get_collection("property_docs")
    results = collection.query(query_embeddings=[q_embedding], n_results=TOP_K)
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]

    # 3. Put the chunks into the prompt as context
    context = "\n\n".join(f"[{src}] {chunk}" for src, chunk in zip(sources, chunks))
    messages = [
        {"role": "system", "content": f"{system_prompt}\n\nContext:\n{context}"},
        {"role": "user", "content": question},
    ]

    # 4. Ask the LLM
    data = requests.post(f"{OLLAMA}/api/chat", json={
        "model": CHAT_MODEL, "messages": messages, "stream": False,
        "options": {"temperature": 0},
    }).json()
    answer = data["message"]["content"]

    # Output guardrail: never let private data reach the user
    blocked = check_output(answer)
    if blocked:
        answer = "I can't share personal information."

    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks,
        "tokens_in": data["prompt_eval_count"],
        "tokens_out": data["eval_count"],
        "blocked": blocked,
    }
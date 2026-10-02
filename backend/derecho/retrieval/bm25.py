# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

import json
from pathlib import Path
from rank_bm25 import BM25Okapi


# ---------------------------------------------------------
# FIND THE DERECHO PROJECT FOLDER
# ---------------------------------------------------------

# bm25.py is located at:
# Derecho/backend/derecho/retrieval/bm25.py
#
# parents[3] gives us the Derecho project folder.
PROJECT_ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------
# FIND chunks.json
# ---------------------------------------------------------

CHUNKS_PATH = (
    PROJECT_ROOT
    / "data"
    / "legal_sources"
    / "chunks.json"
)


# ---------------------------------------------------------
# LOAD LEGAL CHUNKS
# ---------------------------------------------------------

def load_chunks(chunks_path):
    """
    Load processed legal chunks from chunks.json.
    """

    with open(chunks_path, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    return chunks


# ---------------------------------------------------------
# TOKENIZE TEXT
# ---------------------------------------------------------

def tokenize(text):
    """
    Convert text into lowercase word tokens for BM25.
    """

    # Make everything lowercase.
    text = text.lower()

    # Remove common punctuation.
    punctuation = ".,!?;:()[]{}\"'"

    for character in punctuation:
        text = text.replace(character, "")

    # Split the text into words.
    tokens = text.split()

    return tokens


# ---------------------------------------------------------
# BUILD BM25 SEARCH INDEX
# ---------------------------------------------------------

def build_bm25(chunks):
    """
    Build a BM25 search index from the legal chunks.
    """

    tokenized_corpus = []

    # Tokenize every legal chunk.
    for chunk in chunks:
        text = chunk["text"]
        tokens = tokenize(text)
        tokenized_corpus.append(tokens)

    # Create the BM25 index.
    bm25 = BM25Okapi(tokenized_corpus)

    return bm25


# ---------------------------------------------------------
# SEARCH LEGAL CHUNKS
# ---------------------------------------------------------

def search_chunks(query, chunks, bm25, top_k=5):
    """
    Search the legal chunks using BM25.

    Returns the best matching chunks along with
    their BM25 scores.
    """

    # Tokenize the user's question.
    query_tokens = tokenize(query)

    # Score every chunk.
    scores = bm25.get_scores(query_tokens)

    results = []

    # Match every score with its original chunk.
    for index, score in enumerate(scores):
        results.append({
            "score": float(score),
            "chunk": chunks[index]
        })

    # Highest BM25 score should come first.
    results.sort(
        key=lambda result: result["score"],
        reverse=True
    )

    # Return only the best results.
    return results[:top_k]


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

def main():
    """
    Test the legal BM25 retrieval system.

    This program:

    1. Loads chunks.json
    2. Builds the BM25 index
    3. Searches the legal chunks
    4. Displays the top matching results
    """

    # -----------------------------------------------------
    # CHECK FOR chunks.json
    # -----------------------------------------------------

    if not CHUNKS_PATH.exists():
        print(f"Chunks file not found: {CHUNKS_PATH}")
        return


    # -----------------------------------------------------
    # LOAD LEGAL CHUNKS
    # -----------------------------------------------------

    chunks = load_chunks(CHUNKS_PATH)

    # The number changes as more legal PDFs are added.
    print(f"Loaded {len(chunks)} legal chunks.")


    # -----------------------------------------------------
    # BUILD BM25 INDEX
    # -----------------------------------------------------

    bm25 = build_bm25(chunks)

    print("BM25 search index created successfully.")


    # -----------------------------------------------------
    # TEST BM25 SEARCH
    # -----------------------------------------------------

    test_question = "What should I do if ICE comes to my home?"

    print("\n--- BM25 SEARCH TEST ---")
    print(f"Question: {test_question}")


    # Search for the five best matching chunks.
    results = search_chunks(
        test_question,
        chunks,
        bm25,
        top_k=5
    )

    print(f"\nTop {len(results)} results:")


    # -----------------------------------------------------
    # DISPLAY RESULTS
    # -----------------------------------------------------

    for number, result in enumerate(results, start=1):

        chunk = result["chunk"]
        score = result["score"]

        print("\n" + "=" * 60)
        print(f"RESULT {number}")
        print("=" * 60)

        print(f"Score: {score:.4f}")
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Source: {chunk['source_id']}")
        print(f"Page: {chunk['page']}")

        print("\nText:")

        # Limit output so the terminal does not get too large.
        print(chunk["text"][:1000])


# ---------------------------------------------------------
# START PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    main()
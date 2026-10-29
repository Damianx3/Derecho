# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# json lets Python read our chunks.json file.
import json

# Path lets us work with file and folder locations.
from pathlib import Path

# BM25Okapi is the BM25 keyword-search algorithm.
from rank_bm25 import BM25Okapi


# ---------------------------------------------------------
# FIND THE DERECHO PROJECT FOLDER
# ---------------------------------------------------------

# This file is located at:
#
# Derecho/backend/derecho/retrieval/bm25.py
#
# parents[3] moves up to the main Derecho folder.
PROJECT_ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------
# FIND chunks.json
# ---------------------------------------------------------

# ingest.py creates this file after processing
# the legal PDFs.
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
    Load the processed legal chunks from chunks.json.

    Returns:
        A list containing all legal chunks.
    """

    with open(chunks_path, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    return chunks


# ---------------------------------------------------------
# TOKENIZE TEXT
# ---------------------------------------------------------

def tokenize(text):
    """
    Convert text into lowercase word tokens.

    Example:

    "What should I do if ICE comes to my home?"

    becomes:

    [
        "what",
        "should",
        "i",
        "do",
        "if",
        "ice",
        "comes",
        "to",
        "my",
        "home"
    ]
    """

    # Convert everything to lowercase.
    text = text.lower()

    # Remove common punctuation.
    punctuation = ".,!?;:()[]{}\"'"

    for character in punctuation:
        text = text.replace(character, "")

    # Split the text into individual words.
    tokens = text.split()

    return tokens


# ---------------------------------------------------------
# BUILD BM25 SEARCH INDEX
# ---------------------------------------------------------

def build_bm25(chunks):
    """
    Build a BM25 search index using all legal chunks.
    """

    tokenized_corpus = []

    # Tokenize every legal chunk.
    for chunk in chunks:

        text = chunk["text"]

        tokens = tokenize(text)

        tokenized_corpus.append(tokens)

    # Build the BM25 index.
    bm25 = BM25Okapi(tokenized_corpus)

    return bm25


# ---------------------------------------------------------
# SEARCH BM25
# ---------------------------------------------------------

def search_bm25(bm25, chunks, query, top_k=5):
    """
    Search the legal chunks using BM25.

    Args:
        bm25:
            The BM25 search index.

        chunks:
            The original legal chunks.

        query:
            The user's legal question.

        top_k:
            Number of results to return.

    Returns:
        A list containing the best matching chunks
        and their BM25 scores.
    """

    # Convert the user's question into tokens.
    query_tokens = tokenize(query)

    # Get a BM25 score for every legal chunk.
    scores = bm25.get_scores(query_tokens)

    # Combine each score with its chunk.
    scored_results = []

    for index, score in enumerate(scores):

        result = {
            "score": float(score),
            "chunk": chunks[index]
        }

        scored_results.append(result)

    # Sort from highest score to lowest score.
    scored_results.sort(
        key=lambda result: result["score"],
        reverse=True
    )

    # Return only the best results.
    return scored_results[:top_k]


# ---------------------------------------------------------
# DISPLAY SEARCH RESULTS
# ---------------------------------------------------------

def print_results(results):
    """
    Print BM25 search results in a readable format.
    """

    print(f"\nTop {len(results)} results:")

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

        print(chunk["text"])


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

def main():
    """
    Main program for testing our legal BM25 retriever.

    The program:

    1. Loads legal chunks
    2. Builds the BM25 index
    3. Lets the user enter a legal question
    4. Searches the legal documents
    5. Displays the top 5 matching chunks
    """

    # -----------------------------------------------------
    # CHECK FOR chunks.json
    # -----------------------------------------------------

    if not CHUNKS_PATH.exists():

        print(f"Chunks file not found: {CHUNKS_PATH}")

        print(
            "Run backend/derecho/retrieval/ingest.py "
            "before running BM25."
        )

        return


    # -----------------------------------------------------
    # LOAD LEGAL CHUNKS
    # -----------------------------------------------------

    chunks = load_chunks(CHUNKS_PATH)

    print(f"Loaded {len(chunks)} legal chunks.")


    # -----------------------------------------------------
    # MAKE SURE WE HAVE CHUNKS
    # -----------------------------------------------------

    if not chunks:

        print("No legal chunks were found.")

        return


    # -----------------------------------------------------
    # BUILD BM25 INDEX
    # -----------------------------------------------------

    bm25 = build_bm25(chunks)

    print("BM25 search index created successfully.")


    # -----------------------------------------------------
    # ASK USER FOR A QUESTION
    # -----------------------------------------------------

    print("\n--- DERECHO LEGAL SEARCH ---")

    question = input(
        "\nAsk a legal question: "
    ).strip()


    # -----------------------------------------------------
    # CHECK THE QUESTION
    # -----------------------------------------------------

    if not question:

        print("Please enter a question.")

        return


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    results = search_bm25(
        bm25=bm25,
        chunks=chunks,
        query=question,
        top_k=5
    )


    # -----------------------------------------------------
    # DISPLAY RESULTS
    # -----------------------------------------------------

    print("\n--- BM25 SEARCH RESULTS ---")

    print(f"Question: {question}")

    print_results(results)


# ---------------------------------------------------------
# START PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    main()
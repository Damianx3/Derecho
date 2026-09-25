# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# json lets Python read JSON files.
#
# We need it because ingest.py created:
# data/legal_sources/chunks.json
import json


# Path lets us work with file and folder locations.
from pathlib import Path


# BM25Okapi is the BM25 keyword-search algorithm.
#
# We will use it to compare a user's question against
# our legal-document chunks.
from rank_bm25 import BM25Okapi


# ---------------------------------------------------------
# FIND THE DERECHO PROJECT FOLDER
# ---------------------------------------------------------

# This file is located at:
#
# Derecho/backend/derecho/retrieval/bm25.py
#
# parents[3] moves up:
#
# retrieval -> derecho -> backend -> Derecho
#
# This gives us the main Derecho project folder.
PROJECT_ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------
# FIND chunks.json
# ---------------------------------------------------------

# ingest.py created chunks.json after:
#
# 1. Opening the legal PDF
# 2. Extracting the text
# 3. Cleaning the text
# 4. Splitting the text into chunks
# 5. Adding source and page metadata
#
# The final path is:
#
# Derecho/data/legal_sources/chunks.json
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
    Load our processed legal chunks from chunks.json.

    Returns a Python list containing all legal chunks.
    """

    # Open chunks.json in read mode.
    #
    # "r" means we are reading the file.
    #
    # UTF-8 lets us correctly read English, Spanish,
    # and special characters.
    with open(chunks_path, "r", encoding="utf-8") as file:

        # Convert the JSON data into Python data.
        chunks = json.load(file)

    # Give the list of chunks back to the program.
    return chunks


# ---------------------------------------------------------
# TOKENIZE TEXT
# ---------------------------------------------------------

def tokenize(text):
    """
    Convert text into clean lowercase word tokens.

    BM25 searches using these tokens.

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

    # Convert all letters to lowercase.
    #
    # This means:
    #
    # ICE
    # Ice
    # ice
    #
    # will all become:
    #
    # ice
    text = text.lower()


    # -----------------------------------------------------
    # REMOVE PUNCTUATION
    # -----------------------------------------------------

    # These are punctuation characters that we do not
    # want BM25 to consider part of a word.
    #
    # For example:
    #
    # home?
    #
    # should become:
    #
    # home
    punctuation = ".,!?;:()[]{}\"'"


    # Go through each punctuation character.
    for character in punctuation:

        # Replace that punctuation character with nothing.
        #
        # Example:
        #
        # "home?"
        #
        # becomes:
        #
        # "home"
        text = text.replace(character, "")


    # -----------------------------------------------------
    # SPLIT TEXT INTO WORDS
    # -----------------------------------------------------

    # split() separates the text wherever there
    # is whitespace.
    #
    # Example:
    #
    # "ice came to my home"
    #
    # becomes:
    #
    # [
    #     "ice",
    #     "came",
    #     "to",
    #     "my",
    #     "home"
    # ]
    tokens = text.split()

    # Return the finished list of words.
    return tokens


# ---------------------------------------------------------
# BUILD BM25 SEARCH INDEX
# ---------------------------------------------------------

def build_bm25(chunks):
    """
    Build a BM25 search index from our legal chunks.

    BM25 will eventually use this index to rank chunks
    according to how closely they match a user's question.
    """

    # This list will contain a tokenized version
    # of every legal chunk.
    tokenized_corpus = []


    # Go through every legal chunk.
    for chunk in chunks:

        # Get the legal text stored in the chunk.
        text = chunk["text"]

        # Convert the text into clean word tokens.
        tokens = tokenize(text)

        # Add those tokens to our corpus.
        tokenized_corpus.append(tokens)


    # -----------------------------------------------------
    # CREATE THE BM25 INDEX
    # -----------------------------------------------------

    # Give all of our tokenized legal chunks to BM25.
    #
    # BM25 analyzes the words that appear throughout
    # the collection.
    #
    # Later, we will give BM25 a user's question and
    # ask it which chunks are the best matches.
    bm25 = BM25Okapi(tokenized_corpus)

    # Return the finished BM25 search index.
    return bm25


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

def main():
    """
    Main starting point for our BM25 retrieval program.

    Right now this program:

    1. Loads our legal chunks
    2. Tokenizes them
    3. Builds the BM25 search index
    4. Tests our tokenizer

    Next we will make it actually search the chunks.
    """


    # -----------------------------------------------------
    # CHECK FOR chunks.json
    # -----------------------------------------------------

    # Before opening chunks.json, make sure it exists.
    if not CHUNKS_PATH.exists():

        # Show where Python expected to find the file.
        print(f"Chunks file not found: {CHUNKS_PATH}")

        # Stop the program.
        return


    # -----------------------------------------------------
    # LOAD LEGAL CHUNKS
    # -----------------------------------------------------

    # Load the chunks created by ingest.py.
    chunks = load_chunks(CHUNKS_PATH)

    # Show how many chunks were loaded.
    #
    # Right now we expect 28.
    print(f"Loaded {len(chunks)} legal chunks.")


    # -----------------------------------------------------
    # BUILD BM25 INDEX
    # -----------------------------------------------------

    # Send our 28 chunks to build_bm25().
    #
    # The process looks like:
    #
    # legal chunks
    #      ↓
    # tokenize text
    #      ↓
    # tokenized corpus
    #      ↓
    # BM25 index
    bm25 = build_bm25(chunks)

    # If we reached this point without an error,
    # the BM25 index was successfully created.
    print("BM25 search index created successfully.")


    # -----------------------------------------------------
    # TEST OUR TOKENIZER
    # -----------------------------------------------------

    # Create a sample question.
    #
    # Later, instead of using a hard-coded question,
    # the user will be able to enter their own question.
    test_question = "What should I do if ICE comes to my home?"


    # Convert the question into clean tokens.
    tokenized_question = tokenize(test_question)


    # Show the results.
    print("\n--- TOKENIZATION TEST ---")

    print(f"Original: {test_question}")

    print(f"Tokens: {tokenized_question}")


    # -----------------------------------------------------
    # SHOW FIRST LEGAL CHUNK
    # -----------------------------------------------------

    # Make sure at least one chunk exists.
    if chunks:

        print("\n--- FIRST CHUNK ---")

        # Show the unique chunk ID.
        print(f"Chunk ID: {chunks[0]['chunk_id']}")

        # Show which legal source it came from.
        print(f"Source: {chunks[0]['source_id']}")

        # Show which page of the PDF it came from.
        print(f"Page: {chunks[0]['page']}")

        # Show only the first 500 characters so our
        # Terminal output does not become too large.
        print(f"Text: {chunks[0]['text'][:500]}")


# ---------------------------------------------------------
# START PROGRAM
# ---------------------------------------------------------

# When we run:
#
# python3 backend/derecho/retrieval/bm25.py
#
# Python sets __name__ to "__main__".
#
# This tells Python to start our main() function.
if __name__ == "__main__":
    main()
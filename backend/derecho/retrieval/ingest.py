# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# json lets us save Python data into a JSON file.
import json

# Path lets us work with file and folder locations.
from pathlib import Path

# PyMuPDF lets us open PDF files and extract text.
import pymupdf


# ---------------------------------------------------------
# FIND THE DERECHO PROJECT FOLDER
# ---------------------------------------------------------

# __file__ is the location of this ingest.py file.
#
# Our file is located here:
#
# Derecho/backend/derecho/retrieval/ingest.py
#
# parents[3] moves up:
#
# retrieval -> derecho -> backend -> Derecho
#
# This gives us the main Derecho project folder.
PROJECT_ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------
# FIND THE LEGAL PDF
# ---------------------------------------------------------

# Location of our English NILC legal document.
#
# Result:
#
# Derecho/data/legal_sources/en/nilc_arrested_detained_en.pdf
PDF_PATH = (
    PROJECT_ROOT
    / "data"
    / "legal_sources"
    / "en"
    / "nilc_arrested_detained_en.pdf"
)


# ---------------------------------------------------------
# LOCATION FOR THE SAVED CHUNKS
# ---------------------------------------------------------

# This is where our processed legal chunks will be saved.
#
# Result:
#
# Derecho/data/legal_sources/chunks.json
CHUNKS_PATH = (
    PROJECT_ROOT
    / "data"
    / "legal_sources"
    / "chunks.json"
)


# ---------------------------------------------------------
# CLEAN EXTRACTED TEXT
# ---------------------------------------------------------

def clean_text(text):
    """
    Clean text extracted from a PDF.

    PDF extraction can contain extra spaces, line breaks,
    tabs, and other whitespace that we do not need.
    """

    # split() separates the text anywhere there is whitespace.
    #
    # " ".join() puts everything back together using
    # one normal space.
    #
    # Example:
    #
    # "Know   Your\nRights"
    #
    # becomes:
    #
    # "Know Your Rights"
    cleaned_text = " ".join(text.split())

    return cleaned_text


# ---------------------------------------------------------
# SPLIT TEXT INTO CHUNKS
# ---------------------------------------------------------

def chunk_text(text, chunk_size=150, overlap=30):
    """
    Split text into smaller overlapping chunks.

    chunk_size:
        Maximum number of words in each chunk.

    overlap:
        Number of words repeated between chunks.

    Overlap helps us keep context when information
    falls between two chunks.
    """

    # Turn the text into individual words.
    words = text.split()

    # Store our finished chunks here.
    chunks = []

    # Start at the first word.
    start = 0

    # Continue until we reach the end of the text.
    while start < len(words):

        # Calculate where this chunk ends.
        end = start + chunk_size

        # Get the words for this chunk.
        chunk_words = words[start:end]

        # Join the words back together.
        chunk = " ".join(chunk_words)

        # Save the chunk.
        chunks.append(chunk)

        # Move forward while keeping some overlap.
        #
        # Example:
        #
        # chunk_size = 150
        # overlap = 30
        #
        # Chunk 1 = approximately words 1-150
        # Chunk 2 = approximately words 121-270
        #
        # This means about 30 words are repeated.
        start += chunk_size - overlap

    return chunks


# ---------------------------------------------------------
# EXTRACT TEXT FROM PDF
# ---------------------------------------------------------

def extract_pdf_text(pdf_path):
    """
    Open a PDF and extract cleaned text from every page.

    Returns a list containing:
    - page number
    - cleaned page text
    """

    # Open the PDF using PyMuPDF.
    document = pymupdf.open(pdf_path)

    # Show which file was opened.
    print(f"Opened: {pdf_path.name}")

    # Show the number of pages.
    print(f"Number of pages: {len(document)}")

    # Store all extracted pages here.
    pages = []

    # Go through every page in the PDF.
    #
    # start=1 makes our page numbers begin at 1
    # instead of Python's normal 0.
    for page_number, page in enumerate(document, start=1):

        # Extract the raw text from this page.
        text = page.get_text()

        # Clean unnecessary whitespace.
        text = clean_text(text)

        # Store the page number and cleaned text.
        pages.append({
            "page": page_number,
            "text": text
        })

        # Show our progress.
        print(f"Extracted page {page_number}")

    # Close the PDF after reading it.
    document.close()

    # Return all extracted pages.
    return pages


# ---------------------------------------------------------
# CREATE SEARCHABLE RAG CHUNKS
# ---------------------------------------------------------

def create_chunks(pages, source_id):
    """
    Turn extracted PDF pages into smaller searchable chunks.

    Every chunk remembers:
    - its unique chunk ID
    - which source it came from
    - which PDF page it came from
    - the actual text

    Keeping this metadata will allow DERECHO to show
    citations later.
    """

    # Store chunks from the entire document here.
    all_chunks = []

    # Go through every extracted page.
    for page in pages:

        # Get the page number.
        page_number = page["page"]

        # Get the cleaned text.
        page_text = page["text"]

        # Split this page into smaller chunks.
        page_chunks = chunk_text(page_text)

        # Show how many chunks this page produced.
        print(f"Page {page_number}: {len(page_chunks)} chunks")

        # Go through each chunk on this page.
        for chunk_number, chunk in enumerate(page_chunks, start=1):

            # Create a unique ID for the chunk.
            #
            # Example:
            #
            # nilc_arrested_detained_en_p1_c1
            #
            # p1 = page 1
            # c1 = chunk 1
            chunk_id = (
                f"{source_id}_p{page_number}_c{chunk_number}"
            )

            # Store the chunk and its metadata.
            all_chunks.append({
                "chunk_id": chunk_id,
                "source_id": source_id,
                "page": page_number,
                "text": chunk
            })

    # Return all chunks from the document.
    return all_chunks


# ---------------------------------------------------------
# SAVE CHUNKS TO JSON
# ---------------------------------------------------------

def save_chunks(chunks, output_path):
    """
    Save all legal document chunks into a JSON file.

    This allows other parts of DERECHO to load and search
    the chunks without processing the PDF every time.
    """

    # Open/create the JSON file.
    #
    # "w" means write mode.
    #
    # encoding="utf-8" allows us to correctly save
    # English, Spanish, accents, and special characters.
    with open(output_path, "w", encoding="utf-8") as file:

        # Convert our Python list into JSON.
        #
        # ensure_ascii=False:
        # Keep characters such as á, é, ñ, etc.
        #
        # indent=2:
        # Makes the JSON easier for humans to read.
        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2
        )

    # Show where the file was saved.
    print(f"\nSaved chunks to: {output_path}")


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

def main():

    # -----------------------------------------------------
    # CHECK THAT THE PDF EXISTS
    # -----------------------------------------------------

    # Make sure the PDF exists before trying to open it.
    if not PDF_PATH.exists():

        print(f"PDF not found: {PDF_PATH}")

        return


    # -----------------------------------------------------
    # STEP 1: EXTRACT THE PDF
    # -----------------------------------------------------

    # Extract and clean text from every page.
    pages = extract_pdf_text(PDF_PATH)


    # -----------------------------------------------------
    # STEP 2: IDENTIFY THE SOURCE
    # -----------------------------------------------------

    # This ID matches the document ID stored
    # in sources.json.
    source_id = "nilc_arrested_detained_en"


    # -----------------------------------------------------
    # STEP 3: CREATE CHUNKS
    # -----------------------------------------------------

    # Turn the pages into smaller searchable chunks.
    chunks = create_chunks(pages, source_id)


    # -----------------------------------------------------
    # STEP 4: SAVE CHUNKS
    # -----------------------------------------------------

    # Save the chunks into chunks.json.
    #
    # Later, BM25 and vector retrieval will load
    # this file and search through these chunks.
    save_chunks(chunks, CHUNKS_PATH)


    # -----------------------------------------------------
    # STEP 5: SHOW RESULTS
    # -----------------------------------------------------

    # Show how many chunks were created.
    print(f"\nTotal chunks: {len(chunks)}")

    # Make sure at least one chunk exists.
    if not chunks:

        print("No chunks were created.")

        return

    # Show the first chunk so we can verify
    # that everything worked correctly.
    print("\n--- SAMPLE CHUNK ---")

    print(f"Chunk ID: {chunks[0]['chunk_id']}")

    print(f"Source: {chunks[0]['source_id']}")

    print(f"Page: {chunks[0]['page']}")

    print(f"Text: {chunks[0]['text']}")


# ---------------------------------------------------------
# START THE PROGRAM
# ---------------------------------------------------------

# If we run:
#
# python3 backend/derecho/retrieval/ingest.py
#
# Python sets __name__ to "__main__".
#
# That tells Python to run main().
if __name__ == "__main__":
    main()
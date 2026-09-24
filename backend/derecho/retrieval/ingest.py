# Path lets us work with file and folder locations in Python.
from pathlib import Path

# PyMuPDF lets us open PDF files and extract text from them.
import pymupdf


# ---------------------------------------------------------
# FIND THE DERECHO PROJECT FOLDER
# ---------------------------------------------------------

# __file__ is the location of this ingest.py file.
#
# Our file is:
# Derecho/backend/derecho/retrieval/ingest.py
#
# parents[3] moves up:
# retrieval -> derecho -> backend -> Derecho
PROJECT_ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------
# FIND THE LEGAL PDF
# ---------------------------------------------------------

# Location of our English NILC legal document.
PDF_PATH = (
    PROJECT_ROOT
    / "data"
    / "legal_sources"
    / "en"
    / "nilc_arrested_detained_en.pdf"
)


# ---------------------------------------------------------
# CLEAN EXTRACTED TEXT
# ---------------------------------------------------------

def clean_text(text):
    """
    Clean text extracted from a PDF.

    PDF extraction can contain extra spaces, line breaks,
    and other whitespace that we do not need.
    """

    # Split the text wherever there is whitespace,
    # then join it back together using one normal space.
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
        Number of words from the previous chunk that
        are repeated in the next chunk.

    The overlap helps us avoid losing context between
    two chunks.
    """

    # Turn the text into a list of words.
    words = text.split()

    # This list will contain our chunks.
    chunks = []

    # Start at the first word.
    start = 0

    # Continue until we reach the end of the text.
    while start < len(words):

        # Calculate where this chunk should end.
        end = start + chunk_size

        # Get the words for this chunk.
        chunk_words = words[start:end]

        # Join those words back into normal text.
        chunk = " ".join(chunk_words)

        # Save the chunk.
        chunks.append(chunk)

        # Move forward for the next chunk.
        #
        # With:
        # chunk_size = 150
        # overlap = 30
        #
        # Chunk 1 approximately contains words 1-150.
        # Chunk 2 starts around word 121.
        #
        # That means 30 words overlap.
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

    print(f"Opened: {pdf_path.name}")
    print(f"Number of pages: {len(document)}")

    # Store all extracted pages here.
    pages = []

    # Go through every page in the PDF.
    for page_number, page in enumerate(document, start=1):

        # Extract raw text.
        text = page.get_text()

        # Clean extra whitespace from the text.
        text = clean_text(text)

        # Store the page number and cleaned text.
        pages.append({
            "page": page_number,
            "text": text
        })

        print(f"Extracted page {page_number}")

    # Close the PDF when we're finished.
    document.close()

    return pages


# ---------------------------------------------------------
# CREATE SEARCHABLE RAG CHUNKS
# ---------------------------------------------------------

def create_chunks(pages, source_id):
    """
    Turn extracted PDF pages into smaller searchable chunks.

    Every chunk remembers:
    - its unique chunk ID
    - which legal source it came from
    - which PDF page it came from
    - the actual legal text

    This information will be important later for
    retrieval and citations.
    """

    # Store all chunks from the entire document here.
    all_chunks = []

    # Go through every extracted page.
    for page in pages:

        # Get the page number.
        page_number = page["page"]

        # Get the text from that page.
        page_text = page["text"]

        # Split the page into smaller chunks.
        page_chunks = chunk_text(page_text)

        # Show how many chunks this page created.
        print(f"Page {page_number}: {len(page_chunks)} chunks")

        # Go through every chunk from this page.
        for chunk_number, chunk in enumerate(page_chunks, start=1):

            # Create a unique ID for this chunk.
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

    # Return every chunk from the document.
    return all_chunks


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

def main():

    # Make sure our PDF exists before trying to open it.
    if not PDF_PATH.exists():
        print(f"PDF not found: {PDF_PATH}")
        return

    # -----------------------------------------------------
    # STEP 1: EXTRACT THE PDF
    # -----------------------------------------------------

    # Extract and clean text from all PDF pages.
    pages = extract_pdf_text(PDF_PATH)


    # -----------------------------------------------------
    # STEP 2: IDENTIFY THE SOURCE
    # -----------------------------------------------------

    # This ID matches the document ID we placed
    # in sources.json.
    source_id = "nilc_arrested_detained_en"


    # -----------------------------------------------------
    # STEP 3: CREATE CHUNKS
    # -----------------------------------------------------

    # Turn the extracted pages into smaller
    # searchable RAG chunks.
    chunks = create_chunks(pages, source_id)


    # -----------------------------------------------------
    # STEP 4: SHOW RESULTS
    # -----------------------------------------------------

    # Show the total number of chunks created.
    print(f"\nTotal chunks: {len(chunks)}")

    # Make sure at least one chunk exists.
    if not chunks:
        print("No chunks were created.")
        return

    # Show the first chunk so we can verify
    # that everything worked.
    print("\n--- SAMPLE CHUNK ---")

    print(f"Chunk ID: {chunks[0]['chunk_id']}")
    print(f"Source: {chunks[0]['source_id']}")
    print(f"Page: {chunks[0]['page']}")
    print(f"Text: {chunks[0]['text']}")


# ---------------------------------------------------------
# START THE PROGRAM
# ---------------------------------------------------------

# When this file is executed directly:
#
# python3 backend/derecho/retrieval/ingest.py
#
# run the main() function.
if __name__ == "__main__":
    main()
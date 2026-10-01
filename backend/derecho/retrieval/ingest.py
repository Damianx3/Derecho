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
# Our file is:
#
# Derecho/backend/derecho/retrieval/ingest.py
#
# parents[3] moves up:
#
# retrieval -> derecho -> backend -> Derecho
PROJECT_ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------
# FIND THE LEGAL DOCUMENT FOLDERS
# ---------------------------------------------------------

# Main folder containing all legal documents.
#
# Derecho/data/legal_sources/
LEGAL_SOURCES_DIR = (
    PROJECT_ROOT
    / "data"
    / "legal_sources"
)

# Folder containing English PDFs.
ENGLISH_PDF_DIR = LEGAL_SOURCES_DIR / "en"

# Folder containing Spanish PDFs.
SPANISH_PDF_DIR = LEGAL_SOURCES_DIR / "es"


# ---------------------------------------------------------
# LOCATION FOR THE SAVED CHUNKS
# ---------------------------------------------------------

# All processed chunks will eventually be saved here:
#
# Derecho/data/legal_sources/chunks.json
CHUNKS_PATH = (
    LEGAL_SOURCES_DIR
    / "chunks.json"
)


# ---------------------------------------------------------
# FIND ALL LEGAL PDF FILES
# ---------------------------------------------------------

def find_pdf_files():
    """
    Find every PDF stored in the English and Spanish
    legal source folders.

    This allows DERECHO to work with many PDFs instead
    of having one PDF hard-coded into the program.
    """

    # This list will hold all of the PDFs we find.
    pdf_files = []

    # -----------------------------------------------------
    # FIND ENGLISH PDFs
    # -----------------------------------------------------

    # Make sure the English folder exists.
    if ENGLISH_PDF_DIR.exists():

        # Find every file ending in .pdf.
        english_pdfs = list(
            ENGLISH_PDF_DIR.glob("*.pdf")
        )

        # Add them to our main list.
        pdf_files.extend(english_pdfs)


    # -----------------------------------------------------
    # FIND SPANISH PDFs
    # -----------------------------------------------------

    # Make sure the Spanish folder exists.
    if SPANISH_PDF_DIR.exists():

        # Find every file ending in .pdf.
        spanish_pdfs = list(
            SPANISH_PDF_DIR.glob("*.pdf")
        )

        # Add them to our main list.
        pdf_files.extend(spanish_pdfs)


    # Sort the files so they are processed in a
    # consistent order every time.
    pdf_files.sort()


    # -----------------------------------------------------
    # SHOW WHAT WE FOUND
    # -----------------------------------------------------

    print(f"Found {len(pdf_files)} legal PDF(s).")

    # Print each PDF filename.
    for pdf_path in pdf_files:
        print(f"  - {pdf_path.name}")


    # Return the list of PDFs.
    return pdf_files


# ---------------------------------------------------------
# CLEAN EXTRACTED TEXT
# ---------------------------------------------------------

def clean_text(text):
    """
    Clean text extracted from a PDF.

    PDF extraction can contain extra spaces, line breaks,
    tabs, and other whitespace that we do not need.
    """

    # split() separates text anywhere there is whitespace.
    #
    # " ".join() puts it back together using one space.
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

    Overlap helps preserve context between chunks.
    """

    # Turn the text into individual words.
    words = text.split()

    # Store our chunks here.
    chunks = []

    # Start at the first word.
    start = 0

    while start < len(words):

        # Calculate where this chunk ends.
        end = start + chunk_size

        # Get the words for this chunk.
        chunk_words = words[start:end]

        # Join them back into text.
        chunk = " ".join(chunk_words)

        # Save the chunk.
        chunks.append(chunk)

        # Move forward while keeping overlap.
        #
        # Example:
        #
        # chunk_size = 150
        # overlap = 30
        #
        # Chunk 1 ≈ words 1-150
        # Chunk 2 ≈ words 121-270
        start += chunk_size - overlap

    return chunks


# ---------------------------------------------------------
# EXTRACT TEXT FROM PDF
# ---------------------------------------------------------

def extract_pdf_text(pdf_path):
    """
    Open a PDF and extract cleaned text from every page.

    Returns:
        A list containing the page number and text
        from each page.
    """

    # Open the PDF.
    document = pymupdf.open(pdf_path)

    print(f"\nOpened: {pdf_path.name}")
    print(f"Number of pages: {len(document)}")

    # Store extracted pages here.
    pages = []

    # Go through every page.
    for page_number, page in enumerate(document, start=1):

        # Extract raw text.
        text = page.get_text()

        # Clean the text.
        text = clean_text(text)

        # Store the page.
        pages.append({
            "page": page_number,
            "text": text
        })

        print(f"Extracted page {page_number}")

    # Close the PDF.
    document.close()

    return pages


# ---------------------------------------------------------
# CREATE SEARCHABLE RAG CHUNKS
# ---------------------------------------------------------

def create_chunks(pages, source_id):
    """
    Turn PDF pages into smaller searchable chunks.

    Every chunk remembers:
    - its unique chunk ID
    - which document it came from
    - which page it came from
    - the legal text

    This metadata will eventually help DERECHO
    generate citations.
    """

    # Store all chunks from this document here.
    all_chunks = []

    # Go through every page.
    for page in pages:

        page_number = page["page"]
        page_text = page["text"]

        # Skip pages that contain no extracted text.
        if not page_text:
            print(f"Page {page_number}: no text found")
            continue

        # Split the page into chunks.
        page_chunks = chunk_text(page_text)

        print(
            f"Page {page_number}: "
            f"{len(page_chunks)} chunks"
        )

        # Process every chunk.
        for chunk_number, chunk in enumerate(
            page_chunks,
            start=1
        ):

            # Example:
            #
            # nilc_arrested_detained_en_p1_c1
            chunk_id = (
                f"{source_id}"
                f"_p{page_number}"
                f"_c{chunk_number}"
            )

            # Store the chunk and metadata.
            all_chunks.append({
                "chunk_id": chunk_id,
                "source_id": source_id,
                "page": page_number,
                "text": chunk
            })

    return all_chunks


# ---------------------------------------------------------
# SAVE CHUNKS TO JSON
# ---------------------------------------------------------

def save_chunks(chunks, output_path):
    """
    Save all legal chunks into a JSON file.

    BM25 and other retrieval systems can later load
    this file without processing every PDF again.
    """

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(f"\nSaved chunks to: {output_path}")


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

def main():

    # -----------------------------------------------------
    # STEP 1: FIND EVERY PDF
    # -----------------------------------------------------

    pdf_files = find_pdf_files()

    # Stop if we did not find any PDFs.
    if not pdf_files:
        print("\nNo legal PDFs were found.")
        return


    # -----------------------------------------------------
    # STEP 2: PREPARE ONE LARGE CHUNK LIST
    # -----------------------------------------------------

    # Instead of saving chunks from only one PDF,
    # this list will collect chunks from ALL PDFs.
    all_chunks = []


    # -----------------------------------------------------
    # STEP 3: PROCESS EVERY PDF
    # -----------------------------------------------------

    for pdf_path in pdf_files:

        print("\n========================================")
        print(f"Processing: {pdf_path.name}")
        print("========================================")

        # The filename without ".pdf" becomes the source ID.
        #
        # Example:
        #
        # nilc_arrested_detained_en.pdf
        #
        # becomes:
        #
        # nilc_arrested_detained_en
        source_id = pdf_path.stem

        # Extract and clean the PDF pages.
        pages = extract_pdf_text(pdf_path)

        # Create searchable chunks.
        document_chunks = create_chunks(
            pages,
            source_id
        )

        # Add this document's chunks to the main list.
        all_chunks.extend(document_chunks)

        print(
            f"Created {len(document_chunks)} chunks "
            f"from {pdf_path.name}"
        )


    # -----------------------------------------------------
    # STEP 4: SAVE ALL CHUNKS
    # -----------------------------------------------------

    save_chunks(
        all_chunks,
        CHUNKS_PATH
    )


    # -----------------------------------------------------
    # STEP 5: SHOW FINAL RESULTS
    # -----------------------------------------------------

    print("\n========================================")
    print("INGESTION COMPLETE")
    print("========================================")

    print(f"PDFs processed: {len(pdf_files)}")
    print(f"Total chunks: {len(all_chunks)}")

    # Show a sample chunk.
    if all_chunks:

        print("\n--- SAMPLE CHUNK ---")

        print(
            f"Chunk ID: "
            f"{all_chunks[0]['chunk_id']}"
        )

        print(
            f"Source: "
            f"{all_chunks[0]['source_id']}"
        )

        print(
            f"Page: "
            f"{all_chunks[0]['page']}"
        )

        print(
            f"Text: "
            f"{all_chunks[0]['text']}"
        )


# ---------------------------------------------------------
# START THE PROGRAM
# ---------------------------------------------------------

# Running:
#
# python3 backend/derecho/retrieval/ingest.py
#
# starts main().
if __name__ == "__main__":
    main()
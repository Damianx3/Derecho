# Path lets us work with file and folder locations in Python.
from pathlib import Path

# PyMuPDF lets us open PDF files and extract text from them.
import pymupdf


# ---------------------------------------------------------
# FIND THE DERECHO PROJECT FOLDER
# ---------------------------------------------------------

# __file__ is the location of this ingest.py file.
#
# Our file is located here:
# Derecho/backend/derecho/retrieval/ingest.py
#
# parents[3] moves up:
# retrieval -> derecho -> backend -> Derecho
#
# This gives us the main Derecho project folder.
PROJECT_ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------
# FIND THE LEGAL PDF
# ---------------------------------------------------------

# Build the path to our NILC English legal document.
#
# Result:
# Derecho/data/legal_sources/en/nilc_arrested_detained_en.pdf
PDF_PATH = (
    PROJECT_ROOT
    / "data"
    / "legal_sources"
    / "en"
    / "nilc_arrested_detained_en.pdf"
)


# ---------------------------------------------------------
# EXTRACT TEXT FROM PDF
# ---------------------------------------------------------

def extract_pdf_text(pdf_path):
    """
    Open a PDF and extract text from every page.

    Returns a list containing the page number
    and text from each page.
    """

    # Open the PDF using PyMuPDF.
    document = pymupdf.open(pdf_path)

    # Show which PDF was opened.
    print(f"Opened: {pdf_path.name}")

    # Show how many pages are in the PDF.
    print(f"Number of pages: {len(document)}")

    # Create an empty list.
    #
    # We will put the text from every page
    # into this list.
    pages = []

    # Go through every page in the PDF.
    #
    # enumerate() gives us:
    # - page_number = 1, 2, 3, etc.
    # - page = the actual PDF page
    #
    # start=1 means we start counting at page 1
    # instead of Python's normal starting number of 0.
    for page_number, page in enumerate(document, start=1):

        # Extract text from the current page.
        text = page.get_text()

        # Store the page number and its text together.
        #
        # Example:
        #
        # {
        #     "page": 1,
        #     "text": "Know Your Rights..."
        # }
        pages.append({
            "page": page_number,
            "text": text
        })

        # Show our progress in the Terminal.
        print(f"Extracted page {page_number}")

    # Close the PDF when we are finished with it.
    document.close()

    # Return all of the extracted pages.
    return pages


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

def main():

    # Check if the PDF actually exists before
    # trying to open it.
    if not PDF_PATH.exists():

        # If Python cannot find it, print the location
        # where it expected the PDF to be.
        print(f"PDF not found: {PDF_PATH}")

        # Stop the program.
        return

    # Call our extraction function.
    #
    # The results are stored in "pages".
    pages = extract_pdf_text(PDF_PATH)

    # Print a heading to make the Terminal
    # output easier to read.
    print("\n--- SAMPLE TEXT ---")

    # pages[0] means:
    # Get the FIRST page from our list.
    #
    # ["text"] means:
    # Get the text from that page.
    #
    # [:1000] means:
    # Only print the first 1000 characters.
    #
    # We're doing this just to verify that
    # text extraction worked correctly.
    print(pages[0]["text"][:1000])


# ---------------------------------------------------------
# START THE PROGRAM
# ---------------------------------------------------------

# When we run:
#
# python3 backend/derecho/retrieval/ingest.py
#
# Python sets __name__ to "__main__".
#
# This tells Python to start our program
# by running the main() function.
if __name__ == "__main__":
    main() #need spanish verison 
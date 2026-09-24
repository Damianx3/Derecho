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
# CLEAN EXTRACTED TEXT
# ---------------------------------------------------------

def clean_text(text):
    """
    Clean text that was extracted from a PDF.

    PDFs can contain extra spaces, new lines, and other
    whitespace that we do not need for our search system.
    """

    # text.split() separates the text wherever there is
    # whitespace such as spaces, tabs, or new lines.
    #
    # " ".join(...) puts everything back together using
    # one normal space between each piece.
    #
    # Example:
    #
    # "Know   Your\nRights"
    #
    # becomes:
    #
    # "Know Your Rights"
    cleaned_text = " ".join(text.split())

    # Send the cleaned text back to the program.
    return cleaned_text


# ---------------------------------------------------------
# EXTRACT TEXT FROM PDF
# ---------------------------------------------------------

def extract_pdf_text(pdf_path):
    """
    Open a PDF and extract text from every page.

    Returns a list containing the page number
    and cleaned text from each page.
    """

    # Open the PDF using PyMuPDF.
    document = pymupdf.open(pdf_path)

    # Show which PDF was opened.
    print(f"Opened: {pdf_path.name}")

    # Show how many pages are in the PDF.
    print(f"Number of pages: {len(document)}")

    # Create an empty list.
    #
    # We will store information about every page here.
    pages = []

    # Go through every page in the PDF.
    #
    # enumerate() gives us:
    #
    # page_number = 1, 2, 3...
    # page = the actual PDF page
    #
    # start=1 means page numbering starts at 1
    # instead of Python's normal starting value of 0.
    for page_number, page in enumerate(document, start=1):

        # Extract the raw text from the current PDF page.
        text = page.get_text()

        # Clean unnecessary spaces and line breaks
        # from the extracted text.
        text = clean_text(text)

        # Store the page number and cleaned text together.
        #
        # Example:
        #
        # {
        #     "page": 1,
        #     "text": "KNOW YOUR RIGHTS..."
        # }
        pages.append({
            "page": page_number,
            "text": text
        })

        # Show our progress in the Terminal.
        print(f"Extracted page {page_number}")

    # Close the PDF after we finish reading it.
    document.close()

    # Return all extracted pages.
    return pages


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

def main():

    # Make sure the PDF exists before trying to open it.
    if not PDF_PATH.exists():

        # Tell us where Python expected to find the PDF.
        print(f"PDF not found: {PDF_PATH}")

        # Stop the program.
        return

    # Extract and clean the text from the PDF.
    #
    # "pages" will contain a list like:
    #
    # [
    #     {
    #         "page": 1,
    #         "text": "..."
    #     },
    #     {
    #         "page": 2,
    #         "text": "..."
    #     }
    # ]
    pages = extract_pdf_text(PDF_PATH)

    # Make the Terminal output easier to read.
    print("\n--- SAMPLE CLEANED TEXT ---")

    # pages[0]
    #     gets the first page.
    #
    # ["text"]
    #     gets the text stored for that page.
    #
    # [:1000]
    #     shows only the first 1000 characters.
    #
    # This lets us check whether extraction and
    # cleaning worked correctly.
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
# That tells Python to run main().
if __name__ == "__main__":
    main()
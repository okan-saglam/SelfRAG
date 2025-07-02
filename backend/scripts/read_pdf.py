import sys
import os

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.reader.pdf_reader import PDFReader

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python read_pdf.py <path_to_pdf_file>")
        sys.exit(1)

    reader = PDFReader()
    text = reader.read(sys.argv[1])
    print("---- PDF Context ----")
    print(text)
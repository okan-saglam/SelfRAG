import fitz # PyMuPDF
from backend.reader.base_reader import BaseReader

class PDFReader(BaseReader):
    def read(self, file_path: str) -> str:
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            raise RuntimeError(f"Failed to read PDF file: {e}")
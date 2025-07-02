import fitz # PyMuPDF
from typing import List, Tuple
from backend.reader.base_reader import BaseReader

class PDFReader(BaseReader):
    def read(self, file_path: str) -> List[Tuple[int, str]]:
        doc = fitz.open(file_path)
        pages = []
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            pages.append((page_num, text))
        return pages
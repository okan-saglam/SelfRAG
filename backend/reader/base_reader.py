from abc import ABC, abstractmethod
from typing import List, Tuple

class BaseReader(ABC):
    @abstractmethod
    def read(self, file_path: str) -> List[Tuple[int, str]]:
        """
        Read the content of a file and return a list of tuples containing
        (page_number, text_content) for each page.

        :param file_path: Path to the file to be read.
        :return: List of tuples with page number and text content.
        """
        pass
from abc import ABC, abstractmethod

class BaseReader(ABC):
    @abstractmethod
    def read(self, file_path: str) -> str:
        """
        Reads the content of a file and returns it as a string.
        
        :param file_path: The path to the file to be read.
        :return: The content of the file as a string.
        """
        pass
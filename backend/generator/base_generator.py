from abc import ABC, abstractmethod

class BaseGenerator(ABC):
    @abstractmethod
    def generate_answer(self, question: str, context: str) -> str:
        """
        Generates an answer based on the provided question and context.

        :param question: The question to be answered.
        :param context: The context in which the question is asked.
        :return: The generated answer as a string.
        """
        pass
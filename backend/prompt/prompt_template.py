class PromptTemplate:
    def __init__(self, template: str):
        self.template = template

    def format(self, question: str, contexts: list[str]) -> str:
        """
        Format the prompt template with the given question and contexts.
        
        :param question: The user's question.
        :param contexts: List of context strings to include in the prompt.
        :return: Formatted prompt string.
        """
        context_str = "\n\n".join([
            f"[KAYNAK {i+1} - ÖNEMLİ BİLGİLER]\n{c}" 
            for i, c in enumerate(contexts)
        ])
        return self.template.format(context=context_str, question=question)
    
default_prompt_template = PromptTemplate(
    template=(
        """
            You are an assistant that answers questions based on the provided documents. You must provide complete and comprehensive answers using ALL the context information. The following context may include scattered but related paragraphs. Analyze all paragraphs carefully, combine relevant facts, and give a complete and comprehensive answer to the question.

            IMPORTANT INSTRUCTIONS:
            - Use ALL information from ALL provided sources
            - List every feature, characteristic, or detail mentioned
            - Do not skip any items or information
            - Be comprehensive and complete
            - If the question asks for features/characteristics, list them ALL using bullet points
            - Do not summarize or truncate the information

            Context:\n{context}\n\n"
            Question: {question}\n"

            Complete Answer (include ALL details from context):
        """
    )
)
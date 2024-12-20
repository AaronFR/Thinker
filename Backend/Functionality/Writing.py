import enum
import logging

from typing import Dict, List

from deprecated.classic import deprecated

import Personas.PersonaSpecification.WriterSpecification

from AiOrchestration.AiOrchestrator import AiOrchestrator
from AiOrchestration.ChatGptModel import ChatGptModel
from Data.Files.FileManagement import FileManagement
from Data.Files.StorageMethodology import StorageMethodology
from Personas.PersonaSpecification import PersonaConstants
from Personas.PersonaSpecification.EditorSpecification import REWRITE_EXECUTOR_SYSTEM_INSTRUCTIONS, \
    EDITOR_LINE_REPLACEMENT_FUNCTION_SCHEMA, EDITOR_LINE_REPLACEMENT_FUNCTION_INSTRUCTIONS
from Utilities import Constants
from Utilities.ExecutionLogs import ExecutionLogs




class Writing(enum.Enum):
    """Writing represents various task types used within the persona system."""

    @staticmethod
    def write_to_file_task(task_parameters: Dict[str, object]):
        """
        Repeatedly writes content to the specified number of pages. Where one page roughly corresponds to 500 words
        (2000 tokens output)

        :param task_parameters: Dict with SAVE_TO and INSTRUCTION
        """
        executor = AiOrchestrator(task_parameters.get(PersonaConstants.REFERENCE, []))
        output = executor.execute(
            ["Just write the key text, without any of the typical LLM 'would you like to know more' parts"],
            [task_parameters[PersonaConstants.INSTRUCTION]]
        )

        StorageMethodology.select().save_file(output, task_parameters[PersonaConstants.SAVE_TO], overwrite=True)
        ExecutionLogs.add_to_logs(f"Saved to {task_parameters[PersonaConstants.SAVE_TO]}")

    @staticmethod
    def write_to_file(task_parameters: Dict[str, object]):
        """Repeatedly writes content to the specified number of pages. Where one page roughly corresponds to 500 words
        (2000 tokens output)

        :param task_parameters: Dict with SAVE_TO and 'pages_to_write'
        """
        executor = AiOrchestrator(task_parameters.get(PersonaConstants.REFERENCE, []))
        pages_to_write = task_parameters.get("pages_to_write", 1)
        output = ""

        for i in range(1, pages_to_write + 1):
            text = Writing._generate_text(executor, output, task_parameters, i)
            output += text
            logging.debug(f"Page {i} written: {text}")

        StorageMethodology.select().save_file(output, task_parameters[PersonaConstants.SAVE_TO])
        ExecutionLogs.add_to_logs(f"Saved to {task_parameters[PersonaConstants.SAVE_TO]}")

    @staticmethod
    def _generate_text(
            executor_task: AiOrchestrator,
            output: str,
            task_parameters: Dict[str, object],
            page_number: int):
        """Generates text for individual pages of a document based on specified directives and prior content.

        :param executor_task: The instance of AiOrchestrator responsible for generating text
        :param output: The previously generated text to build upon
        :param task_parameters: A dictionary containing details of the task specifications
        :param page_number: The current page number being generated
        :return: The generated text for the specified page
        """
        instructions = [
            f"So far you have written: \n\n{output}",
            """Continue writing the document. Please bear in mind that you are being prompted repeatedly: 
            you don't have to write a response for everything at once."""
        ]

        return executor_task.execute(
            Personas.PersonaSpecification.WriterSpecification.WRITER_SYSTEM_INSTRUCTIONS,
            [
                f"""Write the first page of {task_parameters['pages_to_write']}, 
                    answering the following: {task_parameters[PersonaConstants.INSTRUCTION]}"""
                if page_number == 1 else instructions
            ]
        )

    @staticmethod
    def append_to_file(task_parameters: Dict[str, object]):
        """Appends generated content to a specified file_name.

        :param task_parameters: Contains task-specific directives, including the instruction and file_name path
         for saving
        """
        executor = AiOrchestrator(task_parameters.get(PersonaConstants.REFERENCE, []))
        output = executor.execute(
            Constants.EXECUTOR_SYSTEM_INSTRUCTIONS,
            ["Primary Instructions: " + str(task_parameters[PersonaConstants.INSTRUCTION])]
        )
        StorageMethodology.select().save_file(output, task_parameters[PersonaConstants.SAVE_TO])
        ExecutionLogs.add_to_logs(f"Appended content to {task_parameters[PersonaConstants.SAVE_TO]}")

    @staticmethod
    def process_replacements(file_lines: List[str], task_parameters: Dict[str, object]):
        """Performs replacements line by line in a specified file using instructions provided to an AI executor.

        :param file_lines: The lines from the file that need to be processed
        :param task_parameters: A dictionary containing directives for the task, including the file
         name to save to and the instructions for the replacements
        """
        executor = AiOrchestrator(task_parameters.get(PersonaConstants.REFERENCE, []))
        replacement_instructions = [
            ''.join(StorageMethodology.select().get_numbered_string(file_lines)),
            f"""For the specified file: {task_parameters[PersonaConstants.SAVE_TO]}, 
            perform replacements based on the following instructions: 
            {task_parameters[PersonaConstants.INSTRUCTION]}
            Additionally: Make sure to included enough necessary information for the instruction to be followed accurately
            """
        ]

        replacements = executor.execute_function(
            EDITOR_LINE_REPLACEMENT_FUNCTION_INSTRUCTIONS,
            replacement_instructions,
            EDITOR_LINE_REPLACEMENT_FUNCTION_SCHEMA,
            model=ChatGptModel.CHAT_GPT_4_OMNI_MINI
        )
        return replacements

    @staticmethod
    def rewrite_file(task_parameters: Dict[str, object],
                     approx_max_tokens=1000):
        """Split an input file into chunks based on the estimated max number of output tokens (2000 tokens) taking in
        half that number allowing the llm to either decrease word count or double it should it be required.

        :param task_parameters: A dictionary containing directives, specifically:
            - 'SAVE_TO': File path where the rewritten content will be saved
            - 'INSTRUCTION': Detailed instructions on how to modify the text
        :param approx_max_tokens: token chunk size to split the document by
        """
        executor = AiOrchestrator(task_parameters.get(PersonaConstants.REFERENCE, []))
        file_contents = StorageMethodology.select().read_file(str(task_parameters[PersonaConstants.SAVE_TO]))
        text_chunks = Writing.chunk_text(file_contents, approx_max_tokens)

        re_written_file = ""
        for text_chunk in text_chunks:  # ToDo: could be parallelised
            logging.debug(f"Rewriting: {text_chunk}")
            re_written_file += executor.execute(
                REWRITE_EXECUTOR_SYSTEM_INSTRUCTIONS,
                [f"""Rewrite this section: \n<rewrite_this>\n{text_chunk}\n</rewrite_this>\n
                    In the following way: {str(task_parameters[PersonaConstants.INSTRUCTION])}"""]
            )

        StorageMethodology.select().save_file(re_written_file,
                                 task_parameters[PersonaConstants.SAVE_TO],
                                 overwrite=True)
        ExecutionLogs.add_to_logs(f"File rewritten successfully: {task_parameters[PersonaConstants.SAVE_TO]}")

    @staticmethod
    def chunk_text(text: str, approx_max_tokens: int, char_per_token=4) -> List[str]:
        """Splits the provided text into manageable chunks based on an approximate maximum character limit.

        :param text: The text that needs to be divided into chunks according to the token count
        :param approx_max_tokens: The maximum number of tokens allowed in each chunk before a split occurs
        :param char_per_token: The estimated number of characters that correspond to a single token, typically around 4,
         but may vary depending on the model used
        :return: A list of text chunks created from the original input, each respecting the token limit
        """
        def split_into_chunks(to_chunk: str, max_chars: int) -> List[str]:
            return [to_chunk[i:i + max_chars] for i in range(0, len(to_chunk), max_chars)]

        approx_max_chars = approx_max_tokens * char_per_token
        return split_into_chunks(text, approx_max_chars)

    @deprecated("Not yet redesigned for the node based system")
    @staticmethod
    def regex_refactor(task_parameters: Dict[str, object], file_references=None):
        """Refactor files based on regex patterns provided in the task directives.
        ToDo: It would make sense to add a check of the output
         to make sure a name isn't being changed which *shouldn't*

        :param task_parameters: A dictionary containing key fields:
            - INSTRUCTION: The regex pattern and modifications to be applied
            - REWRITE_THIS: The target string or pattern that needs to be rewritten
        """
        evaluation_files = StorageMethodology.select().list_staged_files()  # defaulting to staged files
        for file in evaluation_files:
            try:
                FileManagement.regex_refactor(
                    str(task_parameters[PersonaConstants.REWRITE_THIS]),
                    str(task_parameters[PersonaConstants.INSTRUCTION]),
                    file
                )
            except ValueError:
                logging.exception(f"Failed to rewrite file {file}")

        ExecutionLogs.add_to_logs(
            f"Regex refactored {task_parameters[PersonaConstants.REWRITE_THIS]} -> {task_parameters[PersonaConstants.INSTRUCTION]}")


if __name__ == '__main__':
    pass

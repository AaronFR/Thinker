import enum
import logging
from typing import Dict, List

from Utilities import Constants
from Personas.PersonaSpecification.EditorSpecification import REWRITE_EXECUTOR_SYSTEM_INSTRUCTIONS, \
    EDITOR_LINE_REPLACEMENT_FUNCTION_SCHEMA, EDITOR_LINE_REPLACEMENT_FUNCTION_INSTRUCTIONS, \
    EDITOR_LINE_REPLACEMENT_INSTRUCTIONS
from AiOrchestration.AiOrchestrator import AiOrchestrator
from AiOrchestration.ChatGptWrapper import ChatGptModel
from Utilities.ExecutionLogs import ExecutionLogs
from Utilities.FileManagement import FileManagement
from Personas.PersonaSpecification import PersonaConstants


class Writing(enum.Enum):
    """Writing is an enumeration representing various task types used within the persona system."""
    WRITE = "WRITE"
    APPEND = "APPEND"
    REWRITE = "REWRITE"
    REWRITE_FILE = "REWRITE_FILE"
    REGEX_REFACTOR = "REGEX_REFACTOR"

    def execute(self, task_parameters: Dict[str, object]):
        """Executes a specified type of task based on the parameters provided.

        :param task_parameters: A dictionary containing directives and parameters needed
         for the task
        :raises ValueError: If an unknown task type is encountered
        """
        def get_action(task_type):
            action_map = {
                Writing.WRITE: self.write_to_file_task,
                Writing.APPEND: self.append_to_file_task,
                Writing.REWRITE: self.rewrite_file_lines,
                Writing.REWRITE_FILE: self.rewrite_file_task,
                Writing.REGEX_REFACTOR: self.refactor_task
            }
            return action_map[task_type]

        action = get_action(self)
        if action is not None:
            action(task_parameters)
        else:
            raise ValueError(f"Unknown Writing: {self}")

    @staticmethod
    def write_to_file_task(task_parameters: Dict[str, object]):
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

        FileManagement.save_file(output, task_parameters[PersonaConstants.SAVE_TO])
        ExecutionLogs.add_to_logs(f"Saved to {task_parameters[PersonaConstants.SAVE_TO]}")

    @staticmethod
    def _generate_text(
            executor_task: AiOrchestrator, output: str, task_parameters: Dict[str, object], page_number: int):
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
            PersonaConstants.WRITER_SYSTEM_INSTRUCTIONS,
            [
                f"""Write the first page of {task_parameters['pages_to_write']}, 
                    answering the following: {task_parameters[PersonaConstants.INSTRUCTION]}"""
                if page_number == 1 else instructions
            ]
        )

    @staticmethod
    def append_to_file_task(task_parameters: Dict[str, object]):
        """Appends generated content to a specified file_name.

        :param task_parameters: Contains task-specific directives, including the instruction and file_name path
         for saving
        """
        executor = AiOrchestrator(task_parameters.get(PersonaConstants.REFERENCE, []))
        output = executor.execute(
            Constants.EXECUTOR_SYSTEM_INSTRUCTIONS,
            ["Primary Instructions: " + str(task_parameters[PersonaConstants.INSTRUCTION])]
        )
        FileManagement.save_file(output, task_parameters[PersonaConstants.SAVE_TO])
        ExecutionLogs.add_to_logs(f"Appended content to {task_parameters[PersonaConstants.SAVE_TO]}")

    @staticmethod
    def rewrite_file_lines(task_parameters: Dict[str, object]):
        """Rewrite the specified lines in a file based on provided instructions and save the updated content.
        NOTE: This is especially bad, at formatting code. ChatGpt wants to fill in ANY incomplete structural elements
        i.e. if it gets a set with only one half of a pair of docstrings commas it ***WILL*** create a new docstring
        triple comma, no amount of instructions can dissuade it. (Better to instruct what TO do)

        :param task_parameters: Dict[str, object]:
            'SAVE_TO': str - The path to the file where updates should be saved
            'INSTRUCTION': str - Detailed instructions on how to process and rewrite the file lines
        """
        executor = AiOrchestrator(task_parameters.get(PersonaConstants.REFERENCE, []))
        file_path = str(task_parameters[PersonaConstants.SAVE_TO])
        file_lines = FileManagement.read_file_with_lines(file_path)

        replacements = Writing.process_replacements(file_lines, task_parameters)
        Writing.apply_replacements(executor, file_lines, replacements, file_path)

    @staticmethod
    def process_replacements(file_lines: List[str], task_parameters: Dict[str, object]):
        """Performs replacements line by line in a specified file using instructions provided to an AI executor.

        :param file_lines: The lines from the file that need to be processed
        :param task_parameters: A dictionary containing directives for the task, including the file
         name to save to and the instructions for the replacements
        """
        executor = AiOrchestrator(task_parameters.get(PersonaConstants.REFERENCE, []))
        replacement_instructions = [
            ''.join(FileManagement.get_numbered_lines(file_lines)),
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
    def apply_replacements(
            executor_task: AiOrchestrator,
            file_lines: List[str],
            replacements: Dict[str, object],
            target_file_path: str):
        """Modifies specific lines in a file based on provided replacement instructions.

        This method processes a list of replacement instructions, updating the file content
        according to the specified changes, and saves the modified content to the given file path.

        :param executor_task: An instance of AiOrchestrator that generates replacement content
        :param file_lines: A list of strings representing the original lines of the file
        :param replacements: Dict containing 'changes', a list of replacement instructions with:
         'start', 'end', and 'replacement'
        :param target_file_path: The file path where the updated content will be saved
        """
        new_content = []
        current_line = 0
        for change in sorted(replacements['changes'], key=lambda x: x['start']):
            start = change['start'] - 1  # Adjust for zero-based indexing
            end = change['end']

            instruction = change['instruction']
            text_to_rewrite = "".join(file_lines[start:end])
            replacement = executor_task.execute(
                [EDITOR_LINE_REPLACEMENT_INSTRUCTIONS, instruction],
                [text_to_rewrite],
                4,
                [f"""\n<original>\n{text_to_rewrite}\n</original>\n
                Given the original text, write as is the rewrite I gave you in accordance with these instructions: 
                {instruction}
                <rules>
                Do NOT try and conclude the original text, if its incomplete leave it *EXACTLY* as incomplete as it was.
                If you have the start to a docstring but not the end just leave it as is, don't the remaining pair.
                DO not select any answer that would break the coherency of the document. E.g. breaking indentation
                Adding things which should not be added, removing things that may be needed, etc.
                DO NOT STRUCTURAL ELEMENTS WHICH ARE NOT PRESENT IN THE ORIGINAL.
                
                Do not add code block delimiters or language identifiers.</rules>"""]
            )
            # Ensure the replacement ends with a newline
            if not replacement.endswith('\n'):
                replacement += '\n'

            ExecutionLogs.add_to_logs(
                f"""Replacing {target_file_path}[{change['start']}:{change['end']}]:
                {text_to_rewrite}
                With -> :
                {replacement}"""
            )

            new_content.extend(file_lines[current_line:start])
            new_content.extend(replacement.splitlines(keepends=True))
            current_line = end

        new_content.extend(file_lines[current_line:])

        FileManagement.save_file(''.join(new_content), target_file_path, overwrite=True)
        ExecutionLogs.add_to_logs(f"Saved to {target_file_path}")

    @staticmethod
    def rewrite_file_task(task_parameters: Dict[str, object],
                          approx_max_tokens=1000):
        """Split an input file into chunks based on the estimated max number of output tokens (2000 tokens) taking in
        half that number allowing the llm to either decrease word count or double it should it be required.

        :param task_parameters: A dictionary containing directives, specifically:
            - 'SAVE_TO': File path where the rewritten content will be saved
            - 'INSTRUCTION': Detailed instructions on how to modify the text
        :param approx_max_tokens: token chunk size to split the document by
        """
        executor = AiOrchestrator(task_parameters.get(PersonaConstants.REFERENCE, []))
        file_contents = FileManagement.read_file(str(task_parameters[PersonaConstants.SAVE_TO]))
        text_chunks = Writing.chunk_text(file_contents, approx_max_tokens)

        re_written_file = ""
        for text_chunk in text_chunks:  # ToDo: could be parallelised
            logging.debug(f"Rewriting: {text_chunk}")
            re_written_file += executor.execute(
                REWRITE_EXECUTOR_SYSTEM_INSTRUCTIONS,
                [f"""Rewrite this section: \n<rewrite_this>\n{text_chunk}\n</rewrite_this>\n
                    In the following way: {str(task_parameters[PersonaConstants.INSTRUCTION])}"""]
            )

        FileManagement.save_file(re_written_file,
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

    @staticmethod
    def refactor_task(task_parameters: Dict[str, object]):
        """Refactor files based on regex patterns provided in the task directives.
        # ToDo: It would make sense to add a check of the output
         to make sure a name isn't being changed which *shouldn't*

        :param task_parameters: A dictionary containing key fields:
            - INSTRUCTION: The regex pattern and modifications to be applied
            - REWRITE_THIS: The target string or pattern that needs to be rewritten
        """
        evaluation_files = FileManagement.list_file_names()
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
    numbered_lines = FileManagement.read_file("Writing.py", return_numbered_lines=True)
    print(numbered_lines)

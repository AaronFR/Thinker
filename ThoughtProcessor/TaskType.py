import enum
import logging
from typing import Dict, List

import Constants
from ThoughtProcessor.ExecutionLogs import ExecutionLogs
from ThoughtProcessor.FileManagement import FileManagement
from ThoughtProcessor.AiWrapper import AiWrapper
from ThoughtProcessor.Personas import PersonaConstants


class TaskType(enum.Enum):
    """
    TaskType is an enumeration for various task types utilized within the persona system.

    Overview:
        It encapsulates the logic for executing different types of tasks for file manipulation and content management.

    Methods:
        - WRITING: Used for writing new content to files.
        - APPENDING: Used for appending content to the end of existing files.
        - REWRITING_LINES: Used for rewriting specific lines in files.
        - FULL_REWRITE: Used for completely rewriting the content of a file.
        - REGEX_REFACTORING: Used for refactoring file contents based on regex patterns.
    """
    #ToDo: should be seperated to its own enum class with the task logic tied to the persona's -> clearer structure
    WRITE = "WRITE"
    APPEND = "APPEND"
    REWRITE = "REWRITE"
    REWRITE_FILE = "REWRITE_FILE"
    REGEX_REFACTOR = "REGEX_REFACTOR"

    def execute(self, executor_task: AiWrapper, task_parameters: Dict[str, object]):
        """
        Overview:
        Executes a specified task type.

        Parameters:
        executor_task (AiWrapper): The task wrapper object that contains the details of the task to be executed.
        task_parameters (Dict[str, object]): A dictionary containing directives and parameters needed for the task.

        Raises:
        ValueError: If an unknown TaskType is encountered.
        """

        def get_action(task_type):
            action_map = {
                TaskType.WRITE: self.write_to_file_task,
                TaskType.APPEND: self.append_to_file_task,
                TaskType.REWRITE: self.rewrite_file_lines,
                TaskType.REWRITE_FILE: self.rewrite_file_task,
                TaskType.REGEX_REFACTOR: self.refactor_task
            }
            return action_map.get(task_type)

        action = get_action(self)
        if action is not None:
            action(executor_task, task_parameters)
        else:
            raise ValueError(f"Unknown TaskType: {self}")

    @staticmethod
    def rewrite_file_lines(executor_task: AiWrapper, task_parameters: Dict[str, object]):
        """
        Rewrite the specified lines in the given file_name based on the provided instructions and save the updated content.

        :param executor_task: AiWrapper - An initialized AI wrapper responsible for executing the rewrite directives.
        :param task_parameters: Dict[str, object] - A dictionary containing:
            'SAVE_TO': str - The file_name path where updates should be saved.
            'INSTRUCTION': str - Detailed instructions on how to process and rewrite the lines.

        The function takes the rewrite instructions from 'task_parameters', locates the specified lines in the file_name
        indicated by 'SAVE_TO', processes the instructions using the 'executor_task', and saves the modified file_name.
        This ensures the original file_name's consistency is maintained with the integrated changes.
        """
        file_path = str(task_parameters.get(PersonaConstants.SAVE_TO))
        file_lines = FileManagement.read_file_with_lines(file_path)

        replacements = TaskType.process_replacements(executor_task, file_lines, task_parameters)
        TaskType.apply_replacements(executor_task, file_lines, replacements, file_path)

    @staticmethod
    def process_replacements(executor_task: AiWrapper, file_lines: List[str], task_parameters: Dict[str, object]):
        """
        Performs line-by-line replacements in a provided file_name using directives given to an AI executor.

        Parameters:
            executor_task (AiWrapper): An instance of AiWrapper to execute the replacement instructions.
            file_lines (List[str]): A list of strings, each representing a line of the file_name to be processed.
            task_parameters (Dict[str, object]): A dictionary containing directives for the task, including the file_name to
            save to and the primary instructions for replacement.
        """
        def get_numbered_lines(lines):
            return [f"{i + 1}: {line}" for i, line in enumerate(lines)]

        replacement_instructions = [
                ''.join(get_numbered_lines(file_lines)),
                f"""For the given file_name: {task_parameters.get(PersonaConstants.SAVE_TO)}, 
                replace sections with the following primary instructions: {task_parameters.get(PersonaConstants.INSTRUCTION)}"""
            ]

        replacements = executor_task.execute_function(
            PersonaConstants.EDITOR_LINE_REPLACEMENT_FUNCTION_INSTRUCTIONS,
            replacement_instructions,
            PersonaConstants.EDITOR_LINE_REPLACEMENT_FUNCTION_SCHEMA,
            model=Constants.MODEL_NAME
        )
        return replacements

    @staticmethod
    def apply_replacements(executor_task: AiWrapper, file_lines: List[str], replacements: Dict[str, object], target_file_path: str):
        """
        Process and replace specific lines in a file based on the given replacement instructions.

        This method iterates through the specified replacements, updates the content of the file accordingly,
        and then saves the modified content back to the specified location.

        Workflow:
        1. Initialize an empty list 'new_content' to store the updated file content.
        2. Set 'current_line' to 0 to track the current index in the original file lines.
        3. Sort the replacement instructions by their starting line number.
        4. For each replacement:
           - Extract the 'start' and 'end' line numbers and adjust for zero-based indexing.
           - Log the replacement operation to the execution logs.
           - Append all lines before the current replacement block to 'new_content'.
           - Replace the specified lines with the new content provided in the replacement instruction.
           - Update 'current_line' to the 'end' line number to skip over replaced lines.
        5. Append any remaining lines after the last replacement to 'new_content'.
        6. Save 'new_content' to the specified file path, overwriting the original file.

        :param executor_task: Task executor for generating replacement content.
        :param file_lines: List of lines representing the file content to be modified.
        :param replacements: Dict containing 'changes', a list of replacement instructions with 'start', 'end', and 'replacement'.
        :param target_file_path: Path to the file to write the updated content.
        """
        new_content = []
        current_line = 0
        for change in sorted(replacements.get('changes'), key=lambda x: x['start']):
            start = change['start'] - 1  # Adjust for zero-based indexing
            end = change['end']

            instruction = change['instruction']
            text_to_rewrite = "".join(file_lines[start:end])
            replacement = executor_task.execute(
                [PersonaConstants.EDITOR_LINE_REPLACEMENT_INSTRUCTIONS],
                [f"""For the given text: \n<input_text>\n{text_to_rewrite}\n</input_text>, 
                "re-write the text with the given instructions in mind WHILE ensuring consistency of the original file is maintained: {instruction}"""]
            )
            # Ensure the replacement ends with a newline
            if not replacement.endswith('\n'):
                replacement += '\n'

            ExecutionLogs.add_to_logs(f"""Replacing {target_file_path}[{change['start']}:{change['end']}]:
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
    def write_to_file_task(executor_task: AiWrapper, task_parameters: Dict[str, object]):
        """
        Repeatedly write content to the specified number of pages to write. Where one page roughly corresponds to
        500 words (2000 tokens output)

        :param executor_task: Initialized LLM wrapper
        :param task_parameters: Dict with SAVE_TO and 'pages_to_write'
        """
        pages_to_write = task_parameters.get("pages_to_write", 1)
        output = ""

        for i in range(1, pages_to_write + 1):
            text = TaskType._generate_text(executor_task, output, task_parameters, i)
            output += text
            logging.debug(f"Page {i} written: {text}")

        FileManagement.save_file(output, task_parameters.get(PersonaConstants.SAVE_TO))
        ExecutionLogs.add_to_logs(f"Saved to {task_parameters.get(PersonaConstants.SAVE_TO)}")

    @staticmethod
    def _generate_text(executor_task: AiWrapper, output: str, task_parameters: Dict[str, object], page_number: int):
        """
        Generates text for individual pages of a document based on given task directives and previously generated output.

        Returns:
        str: The generated text for the specified page.
        :param executor_task: The task executor instance responsible for text generation.
        :param output: Previously generated output to continue from.
        :param task_parameters: A dictionary of directives detailing the task specifics.
        :param page_number: The current page number being generated.
        """
        instructions = [
            f"So far you have written: \n\n{output}",
            """Continue writing the document. Please bear in mind that you are being prompted repeatedly: 
            you don't have to write a response for everything at once."""
        ]

        return executor_task.execute(
            PersonaConstants.WRITER_SYSTEM_INSTRUCTIONS,
            [
                f"Write the first page of {task_parameters.get('pages_to_write')}, answering the following: {task_parameters.get(PersonaConstants.INSTRUCTION)}"
                if page_number == 1 else instructions
            ]
        )

    @staticmethod
    def append_to_file_task(executor_task: AiWrapper, task_parameters: Dict[str, object]):
        """
        Appends generated content to a specified file_name and logs the operation.

        :param executor_task: The AI executor tasked with generating content.
        :param task_parameters: Contains task-specific directives, including the instruction and file_name path for saving.
        """
        output = executor_task.execute(
            Constants.EXECUTOR_SYSTEM_INSTRUCTIONS,
            ["Primary Instructions: " + str(task_parameters.get(PersonaConstants.INSTRUCTION))]
        )
        FileManagement.save_file(output, task_parameters.get(PersonaConstants.SAVE_TO))
        ExecutionLogs.add_to_logs(f"Appended content to {task_parameters.get(PersonaConstants.SAVE_TO)}")

    @staticmethod
    def refactor_task(executor_task: AiWrapper, task_parameters: Dict[str, object]):
        """
        Refactor files based on regex patterns provided in the task directives.

        :param executor_task: Initialized LLM wrapper. Although this is a pure code task, this argument
         is required as per implementation.
        :return:
        """
        evaluation_files = FileManagement.list_file_names()
        for file in evaluation_files:
            try:
                FileManagement.regex_refactor(
                    str(task_parameters.get('rewrite_this')),
                    str(task_parameters.get(PersonaConstants.INSTRUCTION)),
                    file
                )
            except ValueError:
                logging.exception(f"Failed to rewrite file {file}")

        ExecutionLogs.add_to_logs(
            f"Regex refactored {task_parameters.get('rewrite_this')} -> {task_parameters.get(PersonaConstants.INSTRUCTION)}")

    @staticmethod
    def rewrite_file_task(executor_task: AiWrapper, task_parameters: Dict[str, object],
                          approx_max_tokens=1000):
        """
        Split an input file into chunks based on the estimated max number of output tokens (2000 tokens) taking in
        half that number allowing the llm to either decrease word count or double it should it be required.

        :param executor_task: Initialized LLM wrapper
        :param task_parameters: directives including 'file_to_rewrite' and INSTRUCTION
        :param approx_max_tokens: token chunk size to split the document by
        """
        file_contents = FileManagement.read_file(str(task_parameters.get('file_to_rewrite')))
        text_chunks = TaskType.chunk_text(file_contents, approx_max_tokens)

        re_written_file = ""
        for text_chunk in text_chunks:  # ToDo: could be parallelised
            logging.debug(f"Rewriting: {text_chunk}")
            re_written_file += executor_task.execute(
                PersonaConstants.REWRITE_EXECUTOR_SYSTEM_INSTRUCTIONS,
                [f"""Rewrite this section: \n<rewrite_this>\n{text_chunk}\n</rewrite_this>\n
                    In the following way: {str(task_parameters[PersonaConstants.INSTRUCTION])}"""]
            )

        FileManagement.save_file(re_written_file,
                                 task_parameters[PersonaConstants.SAVE_TO],
                                 overwrite=True)
        ExecutionLogs.add_to_logs(f"File rewritten successfully: {task_parameters[PersonaConstants.SAVE_TO]}")

    @staticmethod
    def chunk_text(text: str, approx_max_tokens: int, char_per_token=4) -> List[str]:
        """
        Correctly split file_contents into chunks based on approx_max_chars

        :param text: text to be split apart based on token count
        :param approx_max_tokens: token limit before splitting input text into another chunk
        :param char_per_token: approximate number of characters to token's, typically 4 but can vary based on model
        :return:
        """
        def split_into_chunks(text: str, max_chars: int) -> List[str]:
            return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]

        approx_max_chars = approx_max_tokens * char_per_token
        return split_into_chunks(text, approx_max_chars)

if __name__ == '__main__':
    file_lines = FileManagement.read_file_with_lines("TaskType.py")
    numbered_lines = [f"{i + 1}: {line}" for i, line in enumerate(file_lines)]
    print(numbered_lines)
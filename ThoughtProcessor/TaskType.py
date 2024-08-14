import enum
import logging
from typing import Dict, List

import Constants
from ThoughtProcessor.ExecutionLogs import ExecutionLogs
from ThoughtProcessor.FileManagement import FileManagement
from ThoughtProcessor.AiWrapper import AiWrapper
from ThoughtProcessor.Personas import PersonaConstants


class TaskType(enum.Enum):
    #ToDo: should be seperated to its own enum class with the task logic tied to the persona's -> clearer structure
    WRITE = "WRITE"
    APPEND = "APPEND"
    REWRITE = "REWRITE"
    REWRITE_FILE = "REWRITE_FILE"
    REGEX_REFACTOR = "REGEX_REFACTOR"

    def execute(self, executor_task: AiWrapper, task_directives: Dict[str, object]):
        action_map = {
            TaskType.WRITE: self.write_to_file_task,
            TaskType.APPEND: self.append_to_file_task,
            TaskType.REWRITE: self.rewrite_file_lines,
            TaskType.REWRITE_FILE: self.rewrite_file_task,
            TaskType.REGEX_REFACTOR: self.refactor_task
        }

        action = action_map.get(self)
        if action is not None:
            action(executor_task, task_directives)
        else:
            raise ValueError(f"Unknown TaskType: {self}")

    @staticmethod
    def rewrite_file_lines(executor_task: AiWrapper, task_directives: Dict[str, object]):
        """
        Refactor file lines based on directives.

        :param executor_task: Initialized LLM wrapper
        :param task_directives: Contains SAVE_TO and INSTRUCTION
        """
        file_path = str(task_directives.get(PersonaConstants.SAVE_TO))
        file_lines = FileManagement.read_file_with_lines(file_path)
        replacements = TaskType.process_replacements(executor_task, file_lines, task_directives)
        TaskType.apply_replacements(file_lines, replacements, file_path)

    @staticmethod
    def process_replacements(executor_task: AiWrapper, file_lines: List[str], task_directives: Dict[str, object]):
        def get_numbered_lines(lines):
            return [f"{i + 1}: {line}" for i, line in enumerate(lines)]

        replacement_instructions = [
                ''.join(get_numbered_lines(file_lines)),
                f"""For the given file: {task_directives.get(PersonaConstants.SAVE_TO)}, 
                replace sections with the following primary instructions: {task_directives.get(PersonaConstants.INSTRUCTION)}"""
            ]

        replacements = executor_task.execute_function(
            PersonaConstants.EDITOR_LINE_REPLACEMENT_FUNCTION_INSTRUCTIONS,
            replacement_instructions,
            PersonaConstants.EDITOR_LINE_REPLACEMENT_FUNCTION_SCHEMA,
            model=Constants.MODEL_NAME
        )
        return replacements

    @staticmethod
    def apply_replacements(file_lines: List[str], replacements: Dict[str, object], file_path: str):
        """
        Process and replace specific lines in a file based on the given replacement instructions.

        This method iterates through the specified replacements, updates the content of the file accordingly,
        and then saves the modified content back to the specified location.

        The method first adds all lines before the current replacement block to the new content.
        It then replaces the specified lines with the new content provided in the replacement instructions.
        After processing each replacement, it updates the current line index to skip over the replaced lines.
        Finally, it appends any remaining lines after the last replacement to the new content.

        :param file_lines: A list of lines representing the content of the file to be modified.
        :param replacements: A dictionary containing a 'changes' key, which holds a list of replacement instructions.
         Each instruction is a dictionary with 'start', 'end', and 'replacement' keys.
         - 'start': The starting line number (1-based index) for the replacement.
         - 'end': The ending line number (inclusive, 1-based index) for the replacement.
         - 'replacement': The string content to replace the specified lines with.
        :param file_path: The file to write to.
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
    def write_to_file_task(executor_task: AiWrapper, task_directives: Dict[str, object]):
        """
        Repeatedly write content to the specified number of pages to write. Where one page roughly corresponds to
        500 words (2000 tokens output)

        :param executor_task: Initialized LLM wrapper
        :param task_directives: Dict with SAVE_TO and 'pages_to_write'
        """
        pages_to_write = task_directives.get("pages_to_write", 1)
        output = ""

        for i in range(1, pages_to_write + 1):
            text = TaskType._generate_text(executor_task, output, task_directives, i)
            output += text
            logging.debug(f"Page {i} written: {text}")

        FileManagement.save_file(output, task_directives.get(PersonaConstants.SAVE_TO))
        ExecutionLogs.add_to_logs(f"Saved to {task_directives.get(PersonaConstants.SAVE_TO)}")

    @staticmethod
    def _generate_text(executor_task: AiWrapper, output: str, task_directives: Dict[str, object], page_number: int):
        if page_number == 1:
            return executor_task.execute(
                PersonaConstants.WRITER_SYSTEM_INSTRUCTIONS,
                [f"""Write the first page of {task_directives.get('pages_to_write')}, 
                answering the following: {task_directives.get(PersonaConstants.INSTRUCTION)}"""]
            )
        else:
            return executor_task.execute(
                PersonaConstants.WRITER_SYSTEM_INSTRUCTIONS,
                [
                    f"So far you have written: \n\n{output}",
                    """Continue writing the document. Please bear in mind that you are being prompted repeatedly: 
                    you don't have to write a response for everything at once."""
                ]
            )

    @staticmethod
    def append_to_file_task(executor_task: AiWrapper, task_directives: Dict[str, object]):
        output = executor_task.execute(
            Constants.EXECUTOR_SYSTEM_INSTRUCTIONS,
            ["Primary Instructions: " + str(task_directives.get(PersonaConstants.INSTRUCTION))]
        )
        FileManagement.save_file(output, task_directives.get(PersonaConstants.SAVE_TO))
        ExecutionLogs.add_to_logs(f"Appended content to {task_directives.get(PersonaConstants.SAVE_TO)}")

    @staticmethod
    def refactor_task(executor_task: AiWrapper, task_directives: Dict[str, object]):
        """
        Refactor files based on regex patterns.

        :param executor_task: initialised LLM wrapper, this is a pure code task but for as implemented we must declare
        this argument anyway
        :param task_directives: key fields: INSTRUCTION, 'rewrite_this',
        :return:
        """
        files_for_evaluation = FileManagement.list_files()
        for file in files_for_evaluation:
            try:
                FileManagement.regex_refactor(
                    str(task_directives.get('rewrite_this')),
                    str(task_directives.get(PersonaConstants.INSTRUCTION)),
                    file
                )
            except ValueError:
                logging.exception(f"Failed to rewrite file {task_directives.get('rewrite_this')}")

        ExecutionLogs.add_to_logs(
            f"Regex refactored {task_directives.get('rewrite_this')} -> {task_directives.get(PersonaConstants.INSTRUCTION)}")

    @staticmethod
    def rewrite_file_task(executor_task: AiWrapper, task_directives: Dict[str, object], current_thought_id=1,
                          approx_max_tokens=1000):
        """
        Split a input file into chunks based on the estimated max number of output tokens (2000 tokens) taking in
        half that number allowing the llm to either decrease word count or double it should it be required.

        :param executor_task: Initialized LLM wrapper
        :param task_directives: Dict containing 'file_to_rewrite' and INSTRUCTION
        :param current_thought_id: Unique identifier for the current processing thought
        :param approx_max_tokens: token chunk size to split the document by
        """
        file_contents = FileManagement.read_file(str(task_directives.get('file_to_rewrite')))
        text_chunks = TaskType.chunk_text(file_contents, approx_max_tokens)

        re_written_file = ""
        for text_chunk in text_chunks:  # ToDo: could be parallelised
            logging.debug(f"Rewriting: {text_chunk}")
            re_written_file += executor_task.execute(
                PersonaConstants.REWRITE_EXECUTOR_SYSTEM_INSTRUCTIONS,
                [f"""Rewrite this section: \n<rewrite_this>\n{text_chunk}\n</rewrite_this>\n
                    In the following way: {str(task_directives.get(PersonaConstants.INSTRUCTION))}"""]
            )

        FileManagement.save_file(re_written_file,
                                 task_directives.get(PersonaConstants.SAVE_TO),
                                 overwrite=True)
        ExecutionLogs.add_to_logs(f"File rewritten successfully: {task_directives.get(PersonaConstants.SAVE_TO)}")

    @staticmethod
    def chunk_text(text: str, approx_max_tokens: int, char_per_token=4) -> List[str]:
        """
        Correctly split file_contents into chunks based on approx_max_chars

        :param text: text to be split apart based on token count
        :param approx_max_tokens: token limit before splitting input text into another chunk
        :param char_per_token: approximate number of characters to token's, typically 4 but can vary based on model
        :return:
        """
        approx_max_chars = approx_max_tokens * char_per_token
        return [text[i:i + approx_max_chars] for i in range(0, len(text), approx_max_chars)]

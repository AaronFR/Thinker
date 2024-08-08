import enum
import logging
from typing import Dict, List

import Constants
from ThoughtProcessor.FileManagement import FileManagement
from ThoughtProcessor.AiWrapper import AiWrapper
from ThoughtProcessor.Personas import PersonaConstants


class TaskType(enum.Enum):
    WRITE = "WRITE"
    APPEND = "APPEND"
    REWRITE = "REWRITE"
    REWRITE_FILE = "REWRITE_FILE"

    def execute(self, executor_task: AiWrapper, task_directives: Dict[str, object]):
        action_map = {
            TaskType.WRITE: self.write_to_file_task,
            TaskType.APPEND: self.append_to_file_task,
            TaskType.REWRITE: self.rewrite_part_task,
            TaskType.REWRITE_FILE: self.rewrite_file_task,
        }

        action = action_map.get(self)
        if action is not None:
            action(executor_task, task_directives)
        else:
            raise ValueError(f"Unknown TaskType: {self}")

    @staticmethod
    def write_to_file_task(executor_task: AiWrapper, task_directives: Dict[str, object], current_thought_id=1):
        pages_to_write = task_directives.get("pages_to_write", 1)
        output = ""

        for i in range(1, pages_to_write + 1):
            text = TaskType._generate_text(executor_task, output, task_directives, i)
            output += text
            logging.debug(f"Page {i} written: {text}")

        FileManagement.save_file(output, task_directives.get('where_to_do_it'), str(current_thought_id))

    @staticmethod
    def _generate_text(executor_task: AiWrapper, output: str, task_directives: Dict[str, object], page_number: int):
        if page_number == 1:
            return executor_task.execute(
                PersonaConstants.WRITER_SYSTEM_INSTRUCTIONS,
                [f"""Write the first page of {task_directives.get('pages_to_write')}, 
                answering the following: {task_directives.get('what_to_do')}"""]
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
    def append_to_file_task(executor_task: AiWrapper, task_directives: Dict[str, object], current_thought_id=1):
        output = executor_task.execute(
            Constants.EXECUTOR_SYSTEM_INSTRUCTIONS,
            ["Primary Instructions: " + str(task_directives.get('what_to_do'))]
        )
        FileManagement.save_file(output, task_directives.get('where_to_do_it'), str(current_thought_id))

    @staticmethod
    def rewrite_part_task(executor_task: AiWrapper, task_directives: Dict[str, object], current_thought_id=1):
        output = executor_task.execute(
            PersonaConstants.REWRITE_EXECUTOR_SYSTEM_INSTRUCTIONS,
            [f"""Just rewrite <rewrite_this>\n{task_directives.get('rewrite_this')}\n</rewrite_this>\n
            In the following way: {str(task_directives.get('what_to_do'))}"""]
        )
        FileManagement.re_write_section(
            str(task_directives.get('rewrite_this')),
            output,
            task_directives.get('where_to_do_it'),
            str(current_thought_id))

    @staticmethod
    def rewrite_file_task(executor_task: AiWrapper, task_directives: Dict[str, object], current_thought_id=1,
                          approx_max_tokens=1000):
        file_contents = FileManagement.read_file(str(task_directives.get('file_to_rewrite')))
        text_chunks = TaskType.chunk_text(file_contents, approx_max_tokens)

        re_written_file = ""
        for text_chunk in text_chunks:  # ToDo: could be parallelised
            logging.debug(f"Rewriting: {text_chunk}")
            re_written_file += executor_task.execute(
                PersonaConstants.REWRITE_EXECUTOR_SYSTEM_INSTRUCTIONS,
                [f"""Rewrite this section: \n<rewrite_this>\n{text_chunk}\n</rewrite_this>\n
                    In the following way: {str(task_directives.get('what_to_do'))}"""]
            )

        FileManagement.save_file(re_written_file,
                                 task_directives.get('where_to_do_it'),
                                 str(current_thought_id),
                                 overwrite=True)
        logging.info(f"File rewritten successfully: {task_directives.get('where_to_do_it')}")

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

import enum
import logging
from typing import Dict

import Constants
from ThoughtProcessor.ErrorHandler import ErrorHandler
from ThoughtProcessor.FileManagement import FileManagement
from ThoughtProcessor.AiWrapper import AiWrapper


class TaskType(enum.Enum):
    APPEND = "APPEND"
    REWRITE = "REWRITE"
    REWRITE_FILE = "REWRITE_FILE"

    def execute(self, executor_task: AiWrapper, task_directives: Dict[str, object]):
        ErrorHandler.setup_logging()
        if self == TaskType.APPEND:
            self.append_to_file_task(executor_task, task_directives)
        elif self == TaskType.REWRITE:
            self.rewrite_part_task(executor_task, task_directives)
        elif self == TaskType.REWRITE_FILE:
            self.rewrite_file_task(executor_task, task_directives)
        else:
            raise ValueError(f"Unknown TaskType: {self}")

    @staticmethod
    def append_to_file_task(executor_task: AiWrapper, task_directives: Dict[str, object], current_thought_id=1):
        output = executor_task.execute(
            Constants.EXECUTOR_SYSTEM_INSTRUCTIONS,
            "Primary Instructions: " + str(task_directives.get('what_to_do'))
        )
        FileManagement.save_file(output, task_directives.get('where_to_do_it'), str(current_thought_id))

    @staticmethod
    def rewrite_part_task(executor_task: AiWrapper, task_directives: Dict[str, object], current_thought_id=1):
        output = executor_task.execute(
            Constants.REWRITE_EXECUTOR_SYSTEM_INSTRUCTIONS,
            f"""Just rewrite <rewrite_this>\n{task_directives.get('rewrite_this')}\n</rewrite_this>\n
            In the following way: {str(task_directives.get('what_to_do'))}"""
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

        re_written_file = ""
        char_per_token = 4  # Rough estimate of characters per token
        approx_max_chars = approx_max_tokens * char_per_token

        # Correctly split file_contents into chunks based on approx_max_chars
        text_chunks = [file_contents[i:i + approx_max_chars] for i in range(0, len(file_contents), approx_max_chars)]
        print(f"HELLO WORLD: {len(text_chunks)}, text_length = {len(file_contents)}")
        for text_chunk in text_chunks:  # ToDo: could be parralised
            logging.info(f"Rewriting: {text_chunk}")
            re_written_file += executor_task.execute(
                Constants.REWRITE_EXECUTOR_SYSTEM_INSTRUCTIONS,
                f"""Rewrite this section: \n<rewrite_this>\n{text_chunk}\n</rewrite_this>\n
                    In the following way: {str(task_directives.get('what_to_do'))}"""
            )
            print(re_written_file)

        FileManagement.save_file(re_written_file, task_directives.get('where_to_do_it'), str(current_thought_id),
                                 overwrite=True)
        logging.info(f"File rewritten successfully: {task_directives.get('where_to_do_it')}")

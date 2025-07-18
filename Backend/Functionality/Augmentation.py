import logging
from enum import Enum
from typing import Dict, List

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.Configuration import Configuration
from Constants.Instructions import AUTO_ENGINEER_PROMPT_SYSTEM_MESSAGE, QUESTION_PROMPT_SYSTEM_MESSAGE, \
    AUTO_SELECT_WORKFLOW_SYSTEM_MESSAGE, AUTO_SELECT_WORKER_SYSTEM_MESSAGE
from Utilities.Decorators.Decorators import return_for_error
from Workers.BaseWorker import BaseWorker
from Workers.Default import Default
from Workers.WorkerManagement import get_selected_worker, WORKER_MAPPING, DEFAULT_WORKER


class Workflow(Enum):
    CHAT = "chat"
    WRITE = "write"
    AUTO = "auto"
    LOOP = "loop"


DEFAULT_WORKFLOW = Workflow.CHAT


class Augmentation:
    @staticmethod
    @return_for_error(Default)
    def select_worker(user_prompt: str) -> str:
        """
        Provides a string representing a worker based on the user prompt.

        :param user_prompt: The initial prompt provided by the user.
        :returns Worker: The selected worker based on the content of the user prompt.
        """
        config = Configuration.load_config()
        worker_selection_system_message = config.get('system_messages', {}).get(
            "worker_selection_message",
            AUTO_SELECT_WORKER_SYSTEM_MESSAGE
        ) + "\nRespond with only the worker name in lowercase."

        llm_response = AiOrchestrator().execute(
            [worker_selection_system_message],
            [f"user prompt: \"\"\"\n{user_prompt}\n\"\"\""]
        ).strip().lower()

        logging.info(f"LLM selected worker: {llm_response}")

        if not WORKER_MAPPING.get(llm_response.lower(), False):
            return DEFAULT_WORKER

        return llm_response.lower()

    @staticmethod
    @return_for_error(DEFAULT_WORKFLOW)
    def select_workflow(user_prompt: str, tags: Dict[str, str] = None, selected_files: List[Dict[str, str]] = None) -> Workflow:
        """
        Automatically selects a workflow based on the user prompt using AI deliberation.

        :param user_prompt: The initial prompt provided by the user.
        :param tags: User supplied tags that can be used to automatically select a workflow based on appropriateness
        :param selected_files: List of supplied files, used to disqualify FOR EACH workflow if no files are actually
         present. (Otherwise a FOR EACH workflow would fail)
        :returns Workflow: The selected workflow based on the content of the user prompt.
        """
        if tags:
            # this basically serves as a system on the backend to ensure that if you send any tags that only apply to a
            # particular workflow - it will give you only that workflow.
            if tags.get("write"):
                return Workflow.WRITE
            if tags.get("pages"):
                return Workflow.WRITE
            if tags.get("auto") and selected_files:
                return Workflow.AUTO

        config = Configuration.load_config()
        workflow_selection_system_message = config.get('system_messages', {}).get(
            "workflow_selection_message",
            AUTO_SELECT_WORKFLOW_SYSTEM_MESSAGE
        ) + "\nRespond with only the workflow name in lowercase."

        # Execute the LLM call to determine the workflow
        llm_response = AiOrchestrator().execute(
            [workflow_selection_system_message],
            [f"user prompt: \"\"\"\n{user_prompt}\n\"\"\""]
        ).strip().lower()

        logging.info(f"LLM selected workflow: {llm_response}")

        # Validate the response and map it to the Workflow enum
        if llm_response == Workflow.CHAT.value:
            return Workflow.CHAT
        elif llm_response == Workflow.WRITE.value:
            return Workflow.WRITE
        elif llm_response == Workflow.AUTO.value and selected_files:
            return Workflow.AUTO
        else:
            logging.warning(
                f"Unexpected workflow '{llm_response}' returned by LLM. Defaulting to '{DEFAULT_WORKFLOW}'.")
            return DEFAULT_WORKFLOW

    @staticmethod
    def augment_prompt(initial_prompt: str):
        config = Configuration.load_config()

        # ToDo: It shouldn't be possible to inject code by mal-forming a string in a compiled process right?
        #  You should check.
        prompt_augmentation_system_message = config.get('system_messages', {}).get(
            "prompt_augmentation_message",
            AUTO_ENGINEER_PROMPT_SYSTEM_MESSAGE
        )

        # ToDo: Indepth study of prompt engineering principles and testing to optimise this prompt
        result = AiOrchestrator().execute(
            [prompt_augmentation_system_message],
            ["user prompt: \"\"\"\n" + initial_prompt + "\n\"\"\""]
        )

        return result

    @staticmethod
    def question_user_prompt(initial_prompt: str, reference_messages: list = None, reference_files: list = None):
        config = Configuration.load_config()

        # Initial prompt first in the list
        final_payload = [initial_prompt]
        if reference_messages:
            final_payload.extend(reference_messages)
        if reference_files:
            final_payload.extend(reference_files)

        prompt_questioning_system_message = config.get('system_messages', {}).get(
            "prompt_questioning_message",
            QUESTION_PROMPT_SYSTEM_MESSAGE
        )

        result = AiOrchestrator().execute(
            [prompt_questioning_system_message],
            final_payload
        )
        return result


if __name__ == '__main__':
    Augmentation.augment_prompt("Whats the best way to go from paris to london?")
    # Augmentation.augment_prompt("Can you recommend me a good tech stack for my chatGpt wrapper application?")

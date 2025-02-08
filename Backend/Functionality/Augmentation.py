import logging
from enum import Enum
from typing import Dict

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Constants.Exceptions import FAILURE_TO_SELECT_PERSONA, FAILURE_TO_SELECT_WORKFLOW
from Data.Configuration import Configuration
from Constants.Instructions import AUTO_ENGINEER_PROMPT_SYSTEM_MESSAGE, QUESTION_PROMPT_SYSTEM_MESSAGE, \
    AUTO_SELECT_WORKFLOW_SYSTEM_MESSAGE, AUTO_SELECT_PERSONA_SYSTEM_MESSAGE
from Utilities.Decorators import return_for_error


class Persona(Enum):
    CODER = "coder"
    WRITER = "writer"


DEFAULT_PERSONA = Persona.CODER


class Workflow(Enum):
    CHAT = "chat"
    WRITE = "write"
    AUTO = "auto"


DEFAULT_WORKFLOW = Workflow.CHAT


class Augmentation:
    @staticmethod
    @return_for_error(DEFAULT_PERSONA)
    def select_persona(user_prompt: str) -> Persona:
        """
        Selects a persona based on the user prompt.

        :param user_prompt: The initial prompt provided by the user.
        :returns Persona: The selected persona based on the content of the user prompt.
        """
        config = Configuration.load_config()
        persona_selection_system_message = config.get('systemMessages', {}).get(
            "personaSelectionMessage",
            AUTO_SELECT_PERSONA_SYSTEM_MESSAGE
        )

        llm_response = AiOrchestrator().execute(
            [persona_selection_system_message],
            [f"user prompt: \"\"\"\n{user_prompt}\n\"\"\""]
        ).strip().lower()

        logging.info(f"LLM selected persona: {llm_response}")

        if llm_response == Persona.CODER.value:
            return Persona.CODER
        elif llm_response == Persona.WRITER.value:
            return Persona.WRITER
        else:
            logging.warning(f"Unexpected persona '{llm_response}' returned by LLM. Defaulting to {DEFAULT_PERSONA}.")
            return DEFAULT_PERSONA

    @staticmethod
    @return_for_error(DEFAULT_WORKFLOW)
    def select_workflow(user_prompt: str, tags: Dict[str, str] = None) -> Workflow:
        """
        Automatically selects a workflow based on the user prompt using AI deliberation.

        :param user_prompt: The initial prompt provided by the user.
        :param tags: User supplied tags that can be used to automatically select a workflow based on appropriateness
        :returns Workflow: The selected workflow based on the content of the user prompt.
        """
        if tags:
            if tags.get("write"):
                return Workflow.WRITE
            if tags.get("auto"):
                return Workflow.AUTO

        config = Configuration.load_config()
        workflow_selection_system_message = config.get('systemMessages', {}).get(
            "workflowSelectionMessage",
            AUTO_SELECT_WORKFLOW_SYSTEM_MESSAGE
        )

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
        elif llm_response == Workflow.AUTO.value:
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
        prompt_augmentation_system_message = config.get('systemMessages', {}).get(
            "promptAugmentationMessage",
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

        final_payload = []
        if reference_messages:
            final_payload.extend(reference_messages)
        if reference_files:
            final_payload.extend(reference_files)

        # Append the initial prompt at the end
        final_payload.append(initial_prompt)

        prompt_questioning_system_message = config.get('systemMessages', {}).get(
            "promptQuestioningMessage",
            QUESTION_PROMPT_SYSTEM_MESSAGE
        )

        # ToDo: Indepth study of what makes for the best questions (after graph database has been developed)
        result = AiOrchestrator().execute(
            [prompt_questioning_system_message],
            final_payload
        )
        return result


if __name__ == '__main__':
    Augmentation.augment_prompt("Whats the best way to go from paris to london?")
    # Augmentation.augment_prompt("Can you recommend me a good tech stack for my chatGpt wrapper application?")

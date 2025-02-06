import logging
from typing import Callable, Optional, List, Dict
from flask_socketio import emit

from AiOrchestration.ChatGptModel import ChatGptModel
from Utilities.Contexts import add_to_expensed_nodes, get_message_context
from Utilities.Decorators import return_for_error
from Utilities.models import find_model_enum_value
from Workflows.BaseWorkflow import BaseWorkflow, UPDATE_WORKFLOW_STEP
from Workflows.Workflows import generate_loop_workflow


class LoopWorkflow(BaseWorkflow):
    """
    Workflow that automates repeated prompts on the same file iteration based on user-defined tags.

    It iterates the same prompt multiple times to apply various qualities like refactoring, readability,
    and performance enhancement, as defined by the user.
    """

    # Define maximum number of loops
    MAX_LOOPS = 5

    # Define enhancement qualities for each loop iteration
    ENHANCEMENT_QUALITIES = [
        "refactor the code for better structure and efficiency.",
        "improve readability and maintainability with clear comments and documentation.",
        "optimize performance to reduce execution time and resource usage.",
        "enhance security by identifying and mitigating potential vulnerabilities.",
        "ensure compliance with coding standards and best practices."
    ]

    @return_for_error("An error occurred during the loop workflow.", debug_logging=True)
    def execute(
        self,
        process_prompt: Callable[[str, List[str], Dict[str, str]], str],
        initial_message: str,
        file_references: Optional[List[str]] = None,
        selected_message_ids: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Executes the loop workflow for the specified number of iterations, based on the user's input.

        :param process_prompt: Function to process user prompts. It should take in a prompt string, list of file references,
                               and tags, and return the AI's response as a string.
        :param initial_message: The user's prompt to be repeated and enhanced.
        :param file_references: Optional list of file references to process.
        :param selected_message_ids: Optional list of selected message IDs for context.
        :param tags: Dictionary of additional metadata including loop details.
        :return: Aggregated summary of AI responses from the loop executions.
        """
        # Determine the number of loops from tags, defaulting to 2
        n_loops = int(tags.get("loops", 2))
        n_loops = min(n_loops, self.MAX_LOOPS)  # Enforce maximum number of loops

        model = find_model_enum_value(tags.get("model")) if tags and "model" in tags else ChatGptModel.CHAT_GPT_4_OMNI_MINI
        best_of = int(tags.get("best of", 1))

        workflow_data = generate_loop_workflow(
            file_references=file_references or [],
            selected_messages=selected_message_ids or [],
            model=model.value,
            n_loops=n_loops,
        )
        emit("send_workflow", {"workflow": workflow_data})

        for iteration in range(1, n_loops + 1):
            enhancement_quality = self.ENHANCEMENT_QUALITIES[iteration - 1] if iteration <= len(self.ENHANCEMENT_QUALITIES) else "enhance the code as needed."
            logging.info(f"Iteration {iteration}: with prompt enhancement.")

            prompt_message = f"{initial_message}\n\nSpecifically focus on {enhancement_quality} for iteration #{iteration}'."

            add_to_expensed_nodes(get_message_context())
            self._chat_step(
                iteration=iteration,
                process_prompt=process_prompt,
                message=prompt_message,
                file_references=file_references or [],
                selected_message_ids=selected_message_ids or [],
                best_of=best_of,
                streaming=False,
                model=model,
            )

        final_prompt = (
            "Review your prior outputs and generate a final version of the output taking into account the user prompt"
            f"Initial user prompt: {initial_message}"
        )
        add_to_expensed_nodes(get_message_context())
        response = self._chat_step(
            iteration=n_loops + 1,
            process_prompt=process_prompt,
            message=final_prompt,
            file_references=file_references or [],
            selected_message_ids=selected_message_ids or [],
            best_of=best_of,
            streaming=True,
            model=model,
        )

        return response

import logging
from typing import List, Dict, Tuple

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Functionality.Organising import Organising
from Personas.PersonaSpecification.PersonaConstants import SELECT_WORKFLOW_INSTRUCTIONS
from Utilities.ErrorHandler import ErrorHandler
from Utilities.Utility import Utility


class BasePersona:
    """
    Base class for creating personas that execute tasks.

    Subclasses must implement the following methods:
    - execute_task(task): Define how the persona performs a specific task.
    - execute_task_parameters(task_parameters): Execute specific instructions contained in the task directives.
    """
    MAX_HISTORY = 5

    def __init__(self, name):
        self.name = name

        ErrorHandler.setup_logging()
        self.history: List[Tuple[str, str]] = []  # question-response pairs
        self.workflows = []
        self.instructions = ""
        self.configuration = ""

    def query_user_for_input(self):
        """Continuously prompts the user for questions until they choose to exit. """
        while True:
            new_question = input("Please enter your task (or type 'exit' to quit): ")
            if Utility.is_exit_command(new_question):
                print("Exiting the question loop.")
                break
            elif new_question.lower() == 'history':
                self.display_history()
            elif Utility.is_valid_question(new_question):
                self.select_workflow(new_question)
            else:
                print("Invalid input. Please ask a clear and valid question.")

    def display_history(self):
        """Display the conversation history to the user."""
        if not self.history:
            print("No interaction history available.")
            return
        print("Interaction History:")
        for i, (question, response) in enumerate(self.history):
            print(f"{i + 1}: Q: {question}\n    A: {response}")

    def select_workflow(self, initial_message: str):
        executor = AiOrchestrator()
        output = executor.execute_function(
            f"""Given what my next task which of the following workflows is the most appropriate?
            Just select which workflow is most appropriate.
            Workflows: {self.workflows}""",
            initial_message,
            SELECT_WORKFLOW_INSTRUCTIONS)
        selection = output['selection']

        logging.info(f"Selection: {selection}")
        if selection in self.workflows.keys():
            if selection == "write":
                self.write_workflow(initial_message)
            if selection == "re_write":
                self.re_write_workflow(initial_message)

    def write_workflow(self, initial_message: str):
        raise NotImplementedError("This method should be overridden by subclasses")

    def re_write_workflow(self, initial_message: str):
        raise NotImplementedError("This method should be overridden by subclasses")

    def process_question(self, question: str):
        """Process and store the user's question."""
        response = self.think([question])
        self.history.append((question, response))
        return response

    def think(self, user_messages: List[str]) -> str:
        """Process the input question and think through a response.

        :param user_messages: List of existing user message
        :return The generated response or error message
        """
        logging.info("Processing user messages: %s", user_messages)

        selected_files = Organising.get_relevant_files(user_messages)
        executor = AiOrchestrator(selected_files)

        # ToDo: How the application accesses and gives history to the llm will need to be optimised
        recent_history = [entry[1] for entry in self.history[-self.MAX_HISTORY:]]

        try:
            output = executor.execute(
                [self.instructions, self.configuration],
                user_messages,
                assistant_messages=recent_history
            )
        except Exception as e:
            logging.exception("An error occurred while thinking: %s", e)
            return f"An error occurred while processing: {e}"

        return output


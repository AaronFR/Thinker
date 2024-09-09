import logging
from typing import List, Tuple

from AiOrchestration.AiOrchestrator import AiOrchestrator

from Data.EncyclopediaManagement import EncyclopediaManagement
from Functionality.Organising import Organising
from Personas.PersonaSpecification.PersonaConstants import SELECT_WORKFLOW_INSTRUCTIONS
from Utilities.ErrorHandler import ErrorHandler
from Utilities.Utility import Utility


class BasePersona:
    """
    Base class for creating personas that execute tasks.
    """
    MAX_HISTORY = 5

    def __init__(self, name):
        self.name = name
        self.history: List[Tuple[str, str]] = []  # question-response pairs
        self.workflows = {}
        self.instructions = ""
        self.configuration = ""

        ErrorHandler.setup_logging()

    def query_user_for_input(self):
        """Continuously prompts the user for questions until they choose to exit. """
        while True:
            user_input = input("Please enter your task (or type 'exit' to quit): ")
            if Utility.is_exit_command(user_input):
                print("Exiting the question loop.")
                break
            elif user_input.lower() == 'history':
                self.display_history()
            elif Utility.is_valid_question(user_input):
                self.select_workflow(user_input)
            else:
                print("Invalid input. Please ask a clear and valid question.")

    def display_history(self):
        """Display the conversation history to the user.
        If there is no history available, a message is shown.
        """
        if not self.history:
            print("No interaction history available.")
            return
        print("Interaction History:")
        for i, (question, response) in enumerate(self.history):
            print(f"{i + 1}: Q: {question}\n    A: {response}")

    def select_workflow(self, initial_message: str):
        """Determine and run the appropriate workflow based on the user's query"""
        executor = AiOrchestrator()
        output = executor.execute_function(
            [
                f"Given what my next task is, which of the following workflows is the most appropriate? "
                f"Just select which workflow is most appropriate.\nWorkflows: {self.workflows}"
            ],
            [initial_message],
            SELECT_WORKFLOW_INSTRUCTIONS
        )
        selected_workflow = output['selection']

        logging.info(f"Selection: {selected_workflow}")
        self.run_workflow(selected_workflow, initial_message)

    def run_workflow(self, selected_workflow: str, initial_message: str):
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
        encyclopedia_manager = EncyclopediaManagement()

        # ToDo: this will be called multiple times redundantly in a workflow, user_messages are small however and the
        #  context can change from step to step so its not a priority
        additional_context = encyclopedia_manager.search_encyclopedia(user_messages)
        #user_context = encyclopedia_manager.search_encyclopedia(user_messages, "UserEncyclopedia")
        user_context = ""
        # ToDo: How the application accesses and gives history to the llm will need to be optimised
        recent_history = [f"{entry[0]}: {entry[1]}" for entry in self.history[-self.MAX_HISTORY:]]

        try:
            output = executor.execute(
                [self.instructions, self.configuration, additional_context, user_context],
                user_messages,
                assistant_messages=recent_history
            )
            return output
        except Exception as e:
            logging.exception("An error occurred while thinking: %s", e)
            return f"An error occurred while processing: {e}"

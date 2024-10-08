import ast
import logging
from typing import List, Tuple

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.CategoryManagement import CategoryManagement
from Data.Configuration import Configuration

from Data.EncyclopediaManagement import EncyclopediaManagement
from Data.UserEncyclopediaManagement import UserEncyclopediaManagement
from Functionality.Organising import Organising
from Personas.PersonaSpecification.PersonaConstants import SELECT_WORKFLOW_INSTRUCTIONS
from Utilities.ErrorHandler import ErrorHandler
from Utilities.Utility import Utility


class BasePersona:
    """
    Base class for creating personas that execute tasks.

    history: Note that history is written first on the left, latest on the right, but openAi uses latest on
    the left, first on the right. So it must be reversed if put into openAi API as messages
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
            elif Utility.is_valid_prompt(user_input):
                category_management = CategoryManagement()
                category_management.stage_files(user_input)

                #ToDo adding to the user_encyclopedia needs to be influenced by context category
                user_encyclopedia_manager = UserEncyclopediaManagement()
                user_encyclopedia_manager.add_to_encyclopedia([user_input])
                
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

        logging.info(f"Selected workflow: {selected_workflow}")
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
        ToDo: this will be called multiple times redundantly in a workflow, user_messages are small however and the
         context can change from step to step so its not a priority
        ToDo: split additional_context lists up before sending on
        ToDo: How the application accesses and gives history to the llm will need to be optimised

        :param user_messages: List of existing user message
        :return The generated response or error message
        """
        logging.info("Processing user messages: %s", user_messages)

        selected_files = Organising.get_relevant_files(user_messages)
        executor = AiOrchestrator(selected_files)
        config = Configuration.load_config()

        system_messages = [self.instructions, self.configuration]

        if config['encyclopedias']['encyclopedia_enabled']:
            encyclopedia_manager = EncyclopediaManagement()
            additional_context = encyclopedia_manager.search_encyclopedia(user_messages)
            system_messages.append(additional_context)

        if config['encyclopedias']['user_encyclopedia_enabled']:
            user_encyclopedia_manager = UserEncyclopediaManagement()
            user_context = user_encyclopedia_manager.search_encyclopedia(user_messages)
            system_messages.append(user_context)

        if config['optimization']['message_history']:
            recent_history = [f"{entry[0]}: {entry[1]}" for entry in self.history[-self.MAX_HISTORY:]]
        else:
            recent_history = self.detect_relevant_history(user_messages)

        try:
            output = executor.execute(
                system_messages,
                user_messages,
                assistant_messages=recent_history
            )
            return output
        except Exception as e:
            logging.exception("An error occurred while thinking: %s", e)
            return f"An error occurred while processing: {e}"

    def detect_relevant_history(self, user_messages: List[str]):
        """
        Uses an ai call to actually determine which prompt - response pairs to send on

        ToDo: latter this project would probably be better suited extracting 'concepts' from prompts, these concepts
         would be keywords that can then relate *back* to the knowledge base, user knowledge, history, configuration,
         persona, workflow, etc. With contexts having different strengths based on the input prompt and response

        :param user_messages:
        :return:
        """
        numbered_prompts = "Prompt History: " + "\n".join(
            [f"{idx}: {entry[0]}" for idx, entry in enumerate(self.history)]
        )

        executor = AiOrchestrator()
        relevant_history_list = executor.execute(
            ["Review the messages I've entered and am about to enter, check them against the Prompt History, write a "
             "list of number ids for the prompts."
             "Be very harsh only include a message from the history if it DIRECTLY relates to the user message, "
             "Otherwise include NOTHING. "
             "Just the list of numbers in square brackets, no commentary",
             numbered_prompts],
            user_messages
        )
        logging.info(f"Relevant messages detected in history: {relevant_history_list}")

        relevant_history = []
        try:
            relevant_history_list = ast.literal_eval(relevant_history_list)
            if relevant_history_list:
                for id in relevant_history_list:
                    relevant_history.append(str(self.history[int(id)]))
        except Exception as e:
            logging.warning(f"Failed to Retrieve relevant history!")

        return relevant_history

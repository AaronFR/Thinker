import logging
from typing import List, Dict, Tuple

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Functionality.Organising import Organising
from Personas.PersonaSpecification.PersonaConstants import SELECT_WORKFLOW_INSTRUCTIONS
from Utilities import Constants
from Utilities.ExecutionLogs import ExecutionLogs
from Utilities.ErrorHandler import ErrorHandler
from Personas.PersonaSpecification import PersonaConstants
from Utilities.Utility import Utility


class BasePersona:
    """
    Base class for creating personas that execute tasks.

    Subclasses must implement the following methods:
    - execute_task(task): Define how the persona performs a specific task.
    - execute_task_parameters(task_parameters): Execute specific instructions contained in the task directives.
    """

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

    def write_workflow(self, initial_message: str):
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

    """
    <---Seperator--->
    """

    def execute_task(self, task):
        """
        Execute a given task.

        :param task: A dictionary containing details of the task to be performed
        :raises NotImplementedError: If not overridden by a subclass
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    @staticmethod
    def execute_task_parameters(task_parameters: Dict[str, object]):
        """
        Execute instructions contained in task directives.

        :param task_parameters: A dictionary containing directives for task execution.
        :raises NotImplementedError: If not overridden by a subclass
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def _process_task(self, task_parameters: Dict[str, object]):
        """
        Processes a task and handles any exceptions that occur during execution

        :param task_parameters: A dictionary containing task information
        """
        try:
            self.execute_task_parameters(task_parameters)
        except Exception:
            failed_task = task_parameters[PersonaConstants.INSTRUCTION]
            logging.exception(f"Task failed: {failed_task}")
            ExecutionLogs.add_to_logs(f"Task failed: {failed_task}\n")

    @staticmethod
    def valid_function_output(
            executive_plan: Dict[str, object]) -> bool:
        """
        Validate the structure and content of a task.

        :param executive_plan: A dictionary containing task information
        :return: True if the task is valid, False otherwise
        """
        tasks = executive_plan[PersonaConstants.TASKS]
        for task in tasks:
            if task[PersonaConstants.TYPE] == "REGEX_REFACTOR":
                required_keys = PersonaConstants.DEFAULT_REQUIRED_KEYS + [PersonaConstants.REWRITE_THIS]
            else:
                required_keys = PersonaConstants.DEFAULT_REQUIRED_KEYS

            for key in required_keys:
                if key not in task:
                    logging.error(f"Missing required key: {key} in task: {task}")
                    return False

        logging.info(f"Task validated successfully: {executive_plan}")
        return True

    @staticmethod
    def generate_function(
            evaluation_files: List[str],
            extra_user_inputs: List[str],
            task: str,
            function_instructions: str,
            function_schema: str,
            max_retries: int = Constants.MAX_SCHEMA_RETRIES) -> Dict[str, object]:
        """
        Generate a function based on provided evaluation files and instructions.

        Executes an LLM function to evaluate the provided files and returns an
        executive plan. Includes a maximum retry mechanism with exponential backoff
        for failure cases.

        :param evaluation_files: List of file_name paths to be evaluated
        :param extra_user_inputs: Any additional messages to provide context
        :param task: The main task to be performed
        :param function_instructions: Instructions on how to perform the function
        :param function_schema: Schema that the function output must adhere to
        :param max_retries: Maximum number of retries for generating a valid executive plan
        :return: A dictionary representing the executive plan generated by the LLM
        :raises Exception: If the generated output does not conform to the expected schema after retries
        """

        existing_files = f"Existing files: [{', '.join(str(file) for file in evaluation_files)}]"
        ai_wrapper = AiOrchestrator(evaluation_files)

        for attempt in range(max_retries + 1):
            executive_plan = ai_wrapper.execute_function(
                [existing_files, function_instructions],
                extra_user_inputs + [task],
                function_schema
            )

            if BasePersona.valid_function_output(executive_plan):
                return executive_plan

            else:
                logging.error("Exceeded maximum retries for generating a valid executive plan.")
                raise Exception("SCHEMA FAILURE after maximum retries")

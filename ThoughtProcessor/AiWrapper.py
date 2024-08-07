import logging
from typing import List, Dict
import Constants
import Globals
from Prompter import Prompter
from ThoughtProcessor.ErrorHandler import ErrorHandler
from Utility import Utility





class AiWrapper:
    """Manages interactions with a large language model (LLM), specifically designed for processing user input and
        generating appropriate responses.
    """

    def __init__(self, input_files: List[str]):
        """Initializes a llm wrapper instance that handles the interaction with the OpenAI API.

        :param input_files: A list of file names that users provide for analysis or reference in generating responses.
        :param prompter: An instance of the Prompter class, responsible for creating the prompts sent to the OpenAI API.
        :param open_ai_client: The OpenAI API client instance.
        """
        self.input_files = input_files

        ErrorHandler.setup_logging()

    def execute(self, system_prompts: List[str] | str, user_prompts: List[str] | str) -> str:
        """Generate a response based on system and user prompts.

        This method constructs messages to be sent to the OpenAI API and retrieves a response.
        ToDo: At some point actions other than writing will be needed, e.g. 'web search'
         output and get confused into writing an unironic answer
        #Solved if executive files only review summaries of input files

        :param system_prompts: The system prompts to guide the thinking process.
        :param user_prompts: The user prompts representing supplied material and instructions
        :return: The response generated by OpenAI or an error message.
        """
        messages = Prompter.generate_messages(self.input_files, system_prompts, user_prompts)

        response = Utility.execute_with_retries(lambda: Globals.prompter.get_open_ai_response(messages))
        if not response:
            logging.error("No response from OpenAI API.")
            raise Exception("Failed to get response from OpenAI API.")

        logging.info(f"Executor Task Finished")
        return response

    def execute_function(self,
                         system_prompts: List[str] | str,
                         user_prompts: List[str] | str,
                         function_schema: str) -> Dict[str, object]:
        """Generates a structured response based on system and user prompts.
        ToDo: At some point actions other than writing will be needed, e.g. 'web search'
        #Solved if executive files only review summaries of input files

        :param system_prompts: The system prompts to guide the thinking process.
        :param user_prompts: The specific task to address.
        :param function_schema: the specified function schema to output
        :return: The response generated by OpenAI or an error message.
        """
        if not function_schema:
            logging.error("No function schema found")
        messages = Prompter.generate_messages(self.input_files, system_prompts, user_prompts)

        response = Utility.execute_with_retries(
            lambda: Globals.prompter.get_open_ai_function_response(messages, function_schema)
        )

        if not response:
            logging.error("No response from OpenAI API.")
            raise Exception("Failed to get response from OpenAI API.")

        logging.info(f"Executive Task Finished")
        return response


if __name__ == '__main__':
    ai_wrapper = AiWrapper(["solution.txt"])

    print(ai_wrapper.execute(
        Constants.EXECUTIVE_SYSTEM_INSTRUCTIONS,
        """
        rewrite solution.txt to be more concise"""))


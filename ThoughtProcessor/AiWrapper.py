import logging
from pprint import pformat
from typing import List, Dict
import Constants
from Prompter import Prompter, ChatGptRole
from ThoughtProcessor.ErrorHandler import ErrorHandler
from ThoughtProcessor.FileManagement import FileManagement
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
        self.prompter = Prompter()

        ErrorHandler.setup_logging()

    def execute(self,
                system_prompts: List[str] | str,
                user_prompts: List[str] | str,
                n: int = 1,
                judgement_criteria: List[str] = None) -> str:
        """Generate a response based on system and user prompts.

        This method constructs messages to be sent to the OpenAI API and retrieves a response.
        ToDo: At some point actions other than writing will be needed, e.g. 'web search'
         output and get confused into writing an unironic answer
        #Solved if executive files only review summaries of input files

        :param system_prompts: The system prompts to guide the thinking process.
        :param user_prompts: The user prompts representing supplied material and instructions
        :param n: number of times the LLM is to be queried
        :param judgement_criteria: the criteria on which multiple output responses are judged
        :return: The response generated by OpenAI or an error message.
        """
        messages = AiWrapper.generate_messages(self.input_files, system_prompts, user_prompts)

        if n == 1:
            response = Utility.execute_with_retries(lambda: self.prompter.get_open_ai_response(messages))
        else:
            responses = Utility.execute_with_retries(lambda: self.prompter.get_open_ai_response(messages, n=n))
            logging.debug(f"Messages({n}: \n" + pformat(responses, width=500))

            messages = AiWrapper.generate_messages("", judgement_criteria, responses)
            response = Utility.execute_with_retries(lambda: self.prompter.get_open_ai_response(messages))

        if not response:
            logging.error("No response from OpenAI API.")
            raise Exception("Failed to get response from OpenAI API.")

        logging.info(f"Executor Task Finished")
        return response

    def execute_function(self,
                         system_prompts: List[str] | str,
                         user_prompts: List[str] | str,
                         function_schema: str,
                         model: str=Constants.MODEL_NAME) -> Dict[str, object]:
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
            raise ValueError("Function schema cannot be empty.")
        messages = AiWrapper.generate_messages(self.input_files, system_prompts, user_prompts)

        response = Utility.execute_with_retries(
            lambda: self.prompter.get_open_ai_function_response(messages, function_schema, model)
        )

        if response is None:
            logging.error("Failed to obtain a valid response from OpenAI API.")
            raise RuntimeError("OpenAI API returned no response.")

        logging.info(f"Executive Task Finished")
        return response

    @staticmethod
    def generate_messages(input_files, system_prompts: List[str] | str, user_prompts: List[str]) -> List[Dict[str, str]]:
        logging.debug(f"Thinking...{pformat(user_prompts, width=180)}")
        system_prompts = Utility.ensure_string_list(system_prompts)
        user_prompts = Utility.ensure_string_list(user_prompts)

        messages = AiWrapper.generate_role_messages(system_prompts, input_files, user_prompts)

        logging.debug(f"Messages: {pformat(messages)}")
        logging.info(f"Tokens used (limit 128k): {Utility.calculate_tokens_used(messages)}")

        #ToDo should be a warning message if messages exceed 100: probably means a string has been decomposed
        return messages

    @staticmethod
    def generate_role_messages(system_prompts: List[str], input_files: List[str], user_prompts: List[str]) -> List[Dict[str, str]]:
        """
        :param system_prompts: list of instructions to be saved as system info
        :param input_files: input file content for reference: taking the form of previous user input
        :param user_prompts: primary initial instruction and other supplied material
        :return:
        """
        role_messages = []

        # Add input file contents as user messages
        for file in input_files:
            try:
                content = FileManagement.read_file(file)
                role_messages.append((ChatGptRole.USER, f"{file}: \n{content}"))
            except FileNotFoundError:
                logging.error(f"File not found: {file}. Please ensure the file exists.")
                role_messages.append((ChatGptRole.USER, f"File not found: {file}"))
            except Exception as e:
                logging.error(f"Error reading file {file}: {e}")
                role_messages.append((ChatGptRole.USER, f"Error reading file {file}. Exception: {e}"))

        role_messages.extend({"role": ChatGptRole.USER.value, "content": prompt} for prompt in user_prompts)
        role_messages.extend({"role": ChatGptRole.SYSTEM.value, "content": prompt} for prompt in system_prompts)

        return role_messages


if __name__ == '__main__':
    ai_wrapper = AiWrapper(["solution.txt"])

    print(ai_wrapper.execute(
        Constants.EXECUTIVE_SYSTEM_INSTRUCTIONS,
        """
        rewrite solution.txt to be more concise"""))


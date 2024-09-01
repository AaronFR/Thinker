import logging
from pprint import pformat
from typing import List, Dict

from AiOrchestration.ChatGptWrapper import ChatGptModel, ChatGptWrapper, ChatGptRole
from Utilities import Constants
from Utilities.ErrorHandler import ErrorHandler
from Utilities.FileManagement import FileManagement
from Utilities.Utility import Utility


class AiOrchestrator:
    """Manages interactions with a given large language model (LLM), specifically designed for processing user input and
    generating appropriate responses.
    """

    def __init__(self, input_files: List[str]=[]):
        """Initializes a llm wrapper instance that can make call to a given model (currently only OpenAi models).

        :param input_files: A list of file names that users provide for analysis or reference in generating responses
        """
        self.input_files = input_files
        self.prompter = ChatGptWrapper()

        ErrorHandler.setup_logging()

    def execute(self,
                system_prompts: List[str] | str,
                user_prompts: List[str] | str,
                n: int = 1,
                judgement_criteria: List[str] = None,
                model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI,
                assistant_messages: List[str] = []) -> str:
        """Generate a response based on system and user prompts.

        This method constructs messages to be sent to the OpenAI API and retrieves a response.
        ToDo: At some point actions other than writing will be needed, e.g. 'web search'
         output and get confused into writing an unironic answer
         Solved if executive files only review summaries of input files

        :param system_prompts: The system prompts to guide the thinking process
        :param user_prompts: The user prompts representing supplied material and instructions
        :param n: number of times the LLM is to be queried
        :param judgement_criteria: the criteria on which multiple output responses are judged
        :param model: Preferred llm model to be used
        :param assistant_messages: history for the current conversation
        :return: The response generated by OpenAI or an error message
        """
        messages = AiOrchestrator.generate_messages(self.input_files, system_prompts, user_prompts, assistant_messages)

        if n == 1:
            response = Utility.execute_with_retries(lambda: self.prompter.get_open_ai_response(messages, model))
        else:
            responses = Utility.execute_with_retries(lambda: self.prompter.get_open_ai_response(messages, model, n=n))
            logging.info(f"Messages({n}: \n" + pformat(responses, width=500))

            messages = AiOrchestrator.generate_messages("", judgement_criteria, responses)
            response = Utility.execute_with_retries(lambda: self.prompter.get_open_ai_response(messages, model))

        if not response:
            logging.error("No response from OpenAI API.")
            raise Exception("Failed to get response from OpenAI API.")

        logging.info(f"Executor Task Finished, with response:\n{response}")
        return response

    def execute_function(self,
                         system_prompts: List[str] | str,
                         user_prompts: List[str] | str,
                         function_schema: str,
                         model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI) -> Dict[str, object]:
        """Generates a structured response based on system and user prompts.
        ToDo: At some point actions other than writing will be needed, e.g. 'web search'
         Solved if executive files only review summaries of input files

        :param system_prompts: The system prompts to guide the thinking process
        :param user_prompts: The specific task to address
        :param function_schema: the specified function schema to output
        :param model: Preferred llm model to be used
        :return: The response generated by OpenAI or an error message
        """
        if not function_schema:
            logging.error("No function schema found")
            raise ValueError("Function schema cannot be empty.")
        messages = AiOrchestrator.generate_messages(self.input_files, system_prompts, user_prompts)

        response = Utility.execute_with_retries(
            lambda: self.prompter.get_open_ai_function_response(messages, function_schema, model)
        )

        if response is None:
            logging.error("Failed to obtain a valid response from OpenAI API.")
            raise RuntimeError("OpenAI API returned no response.")

        logging.info(f"Function evaluated with response {response}")
        return response

    @staticmethod
    def generate_messages(input_files,
                          system_prompts: List[str] | str,
                          user_prompts: List[str],
                          assistant_messages: List[str] = None) -> List[Dict[str, str]]:
        logging.debug(f"Thinking...{pformat(user_prompts, width=180)}")
        system_prompts = Utility.ensure_string_list(system_prompts)
        user_prompts = Utility.ensure_string_list(user_prompts)
        if assistant_messages:
            assistant_messages = Utility.ensure_string_list(assistant_messages)

        messages = AiOrchestrator.generate_role_messages(system_prompts, input_files, user_prompts, assistant_messages)

        logging.debug(f"Messages: {pformat(messages)}")
        logging.info(f"Tokens used (limit 128k): {Utility.calculate_tokens_used(messages)}")

        # ToDo:should be a warning message if messages exceed 100: probably means a string has been decomposed
        return messages

    @staticmethod
    def generate_role_messages(
            system_prompts: List[str],
            input_files: List[str],
            user_prompts: List[str],
            assistant_messages: List[str] = None) -> List[Dict[str, str]]:
        """Creates a list of messages to be handled by the ChatGpt API, first the system messages then user messages
        with any input files at the end. Prioritising the instructions of the system messages

        :param system_prompts: list of instructions to be saved as system info
        :param input_files: input file content for reference: taking the form of previous user input
        :param user_prompts: primary initial instruction and other supplied material
        :param assistant_messages: messages which represent the prior course of the conversation
        :return:
        """
        role_messages = []

        role_messages.extend({"role": ChatGptRole.SYSTEM.value, "content": prompt} for prompt in system_prompts)
        role_messages.extend({"role": ChatGptRole.USER.value, "content": prompt} for prompt in user_prompts)

        # Add input file contents as user messages
        for file in input_files:
            try:
                content = FileManagement.read_file(file)
                role_messages.append({"role": ChatGptRole.SYSTEM.value, "content": content})
            except FileNotFoundError:
                logging.error(f"File not found: {file}. Please ensure the file exists.")
                role_messages.append((ChatGptRole.SYSTEM, f"File not found: {file}"))
            except Exception as e:
                logging.error(f"Error reading file {file}: {e}")
                role_messages.append((ChatGptRole.SYSTEM, f"Error reading file {file}. Exception: {e}"))

        if assistant_messages:
            role_messages.extend(
                {"role": ChatGptRole.ASSISTANT.value, "content": prompt} for prompt in assistant_messages)

        return role_messages


if __name__ == '__main__':
    ai_wrapper = AiOrchestrator(["solution.txt"])

    print(ai_wrapper.execute(
        Constants.EXECUTIVE_SYSTEM_INSTRUCTIONS,
        """
        rewrite solution.txt to be more concise"""))

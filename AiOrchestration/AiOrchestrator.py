import logging
from pprint import pformat
from typing import List, Dict

from AiOrchestration.ChatGptWrapper import ChatGptWrapper, ChatGptRole
from AiOrchestration.ChatGptModel import ChatGptModel
from Utilities.ErrorHandler import ErrorHandler
from Data.FileManagement import FileManagement
from Utilities.Utility import Utility


class AiOrchestrator:
    """Manages interactions with a given large language model (LLM), specifically designed for processing user input and
    generating appropriate responses.
    """

    def __init__(self, input_files: List[str] = None):
        """Initializes a llm wrapper instance that can make call to a given model (currently only OpenAi models).

        :param input_files: A list of file names that users provide for analysis or reference in generating responses
        """
        self.input_files = input_files or []
        self.prompter = ChatGptWrapper()

        ErrorHandler.setup_logging()

    def execute(self,
                system_prompts: List[str] | str,
                user_prompts: List[str] | str,
                rerun_count: int = 1,
                judgement_criteria: List[str] = None,
                model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI,
                assistant_messages: List[str] = None,
                streaming: bool = False) -> str:
        """Generate a response based on system and user prompts.

        This method constructs messages to be sent to the OpenAI API and retrieves a response.

        :param system_prompts: Messages providing contextual guidance to the LLM
        :param user_prompts: The user prompts representing instructions
        :param rerun_count: number of times to rerun outputs
        :param judgement_criteria: Criteria for evaluating multiple output responses
        :param model: Preferred LLM model to be used
        :param assistant_messages: History for the current interaction
        :return: The response generated by OpenAI or an error message
        """
        assistant_messages = assistant_messages or []
        messages = self.generate_messages(system_prompts, user_prompts, assistant_messages)
        logging.info(f"Executing LLM call with messages: \n{pformat(messages, width=500)}")

        if streaming:
            logging.info("Executing streaming response")
            response = Utility.execute_with_retries(lambda: self.prompter.get_open_ai_streaming_response(messages, model))
        else:
            logging.info("Executing non-streaming response")
            if rerun_count == 1:
                response = Utility.execute_with_retries(lambda: self.prompter.get_open_ai_response(messages, model))
            else:
                responses = Utility.execute_with_retries(lambda: self.prompter.get_open_ai_response(
                    messages,
                    model,
                    rerun_count=rerun_count)
                )
                logging.info(f"Messages({rerun_count}: \n" + pformat(responses, width=500))

                messages = self.generate_messages("", judgement_criteria, responses)
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

        :param system_prompts: The system prompts to guide the thinking process
        :param user_prompts: The specific task to address
        :param function_schema: the specified function schema to output
        :param model: Preferred llm model to be used
        :return: The response generated by OpenAI or an error message
        """
        if not function_schema:
            logging.error("No function schema found")
            raise ValueError("Function schema cannot be empty.")

        messages = self.generate_messages(system_prompts, user_prompts)
        response = Utility.execute_with_retries(
            lambda: self.prompter.get_open_ai_function_response(messages, function_schema, model)
        )

        if response is None:
            logging.error("Failed to obtain a valid response from OpenAI API.")
            raise RuntimeError("OpenAI API returned no response.")

        logging.info(f"Function evaluated with response: {pformat(response)}")
        return response

    def generate_messages(self,
                          system_prompts: List[str] | str,
                          user_prompts: List[str],
                          assistant_messages: List[str] = None) -> List[Dict[str, str]]:
        """Generates the list of messages by composing user and system prompts.

        :param system_prompts: Messages providing contextual guidance to the LLM
        :param user_prompts: User prompts representing instructions
        :param assistant_messages: History of the current interaction
        :return: List of formatted messages for LLM processing
        """
        logging.debug(f"Composing messages with user prompts: {pformat(user_prompts, width=280)}")

        system_prompts = Utility.ensure_string_list(system_prompts)
        user_prompts = Utility.ensure_string_list(user_prompts)
        if assistant_messages:
            assistant_messages = Utility.ensure_string_list(assistant_messages)

        messages = self.build_role_messages(system_prompts, user_prompts, assistant_messages)
        logging.debug(f"Messages: {pformat(messages)}")
        logging.info(f"Tokens used (limit 128k): {Utility.calculate_tokens_used(messages)}")
        return messages

    def build_role_messages(self,
                            system_prompts: List[str],
                            user_prompts: List[str],
                            assistant_messages: List[str] = None) -> List[Dict[str, str]]:
        """Creates a list of messages to be handled by the ChatGpt API, the most important messages is the very last
        'latest' message in the list

        :param system_prompts: list of instructions to be saved as system info
        :param user_prompts: primary initial instruction and other supplied material
        :param assistant_messages: messages which represent the prior course of the conversation
        :return:
        """
        role_messages = []
        if assistant_messages:
            role_messages.extend({
                "role": ChatGptRole.ASSISTANT.value,
                "content": prompt
            } for prompt in assistant_messages)

        logging.info(f"Number of input files: {self.input_files}")
        for file in self.input_files:
            try:
                content = FileManagement.read_file(file)
                role_messages.append({"role": ChatGptRole.USER.value, "content": f"<{file}>{content}</{file}>"})
            except FileNotFoundError:
                logging.error(f"File not found: {file}. Please ensure the file exists.")
                role_messages.append({"role": ChatGptRole.SYSTEM.value, "content": f"File not found: {file}"})
            except Exception as e:
                logging.error(f"Error reading file {file}: {e}")
                role_messages.append(
                    {"role": ChatGptRole.SYSTEM.value, "content": f"Error reading file {file}. Exception: {e}"}
                )

        role_messages += [
            {"role": ChatGptRole.SYSTEM.value, "content": prompt} for prompt in system_prompts
        ] + [
            {"role": ChatGptRole.USER.value, "content": prompt} for prompt in user_prompts
        ]

        return role_messages


if __name__ == '__main__':
    ai_wrapper = AiOrchestrator(["example.txt"])

    # print(ai_wrapper.execute(
    #     Constants.EXECUTIVE_SYSTEM_INSTRUCTIONS,
    #     ["rewrite solution.txt to be more concise"]
    # ))
    print(ai_wrapper.execute(
        ["""Given the following user prompt what are your questions, be concise and targeted. 
        What would you like to know before proceeding"""],
        ["rewrite solution.txt to be more concise"]
    ))
import logging
from typing import List, Dict, Optional

from deprecated.classic import deprecated

from AiOrchestration.AiModel import AiModel
from AiOrchestration.ChatGptModel import ChatGptModel
from AiOrchestration.GeminiModel import GeminiModel
from AiOrchestration.ChatGptMessageBuilder import generate_messages
from Constants.Exceptions import AI_RESOURCE_FAILURE, FUNCTION_SCHEMA_EMPTY, NO_RESPONSE_OPEN_AI_API
from Data.Configuration import Configuration
from Utilities.Decorators.Decorators import handle_errors, specify_functionality_context
from Utilities.LogsHandler import LogsHandler
from Utilities.Utility import Utility
from Utilities.models import determine_llm_client, find_model_enum_value


class AiOrchestrator:
    """
    Manages interactions with a large language model (LLM), processing user input and generating responses.
    """

    # ToDo Re-implement differentiated re-runs
    RERUN_SYSTEM_MESSAGES = [
        "",  # First rerun: no additions.
        "prioritize coherency",
        "prioritize creativity",
        "prioritize intelligent and well thought out solutions",
        "prioritize thinking out your response FIRST and responding LAST",
        "prioritize non-linear thinking, utilise niche deductions to make an unusual but possibly insightful solution"
    ]
    chat_gpt_models = {model.value for model in ChatGptModel}
    gemini_models = {model.value for model in GeminiModel}

    def __init__(self):
        """
        Initializes an LLM wrapper instance that can call a given supported model.
        """
        self.llm_client = None
        self.default_background_model = ChatGptModel.CHAT_GPT_4_OMNI_MINI

    @staticmethod
    def _load_default_model() -> AiModel:
        """
        Retrieves the default model from configuration if one is not provided.
        """
        config = Configuration.load_config()
        default_model_str = config.get('models', {}).get(
            "default_background_model",
            ChatGptModel.CHAT_GPT_4_OMNI_MINI.value
        )
        return find_model_enum_value(default_model_str)

    @handle_errors(raise_errors=True)
    def execute(
        self,
        system_prompts: List[str] | str,
        user_prompts: List[str] | str,
        rerun_count: int = 1,
        judgement_criteria: Optional[List[str]] = None,
        model: Optional[AiModel] = None,
        assistant_messages: Optional[List[str]] = None,
        streaming: bool = False
    ) -> str:
        """
        Generates an LLM response based on given system and user prompts.

        :param system_prompts: Contextual instructions for the AI.
        :param user_prompts: The user's instructions.
        :param rerun_count: Number of times to run the LLM
        :param judgement_criteria: Criteria to evaluate the best response after multiple runs
        :param model: Preferred AI model; falls back to default if not provided.
        :param assistant_messages: History of prior assistant responses.
        :param streaming: Flag for streaming vs. standard singular response.
        :return: Generated LLM response.
        :raises Exception: If no response is received from the AI API.
        """
        if not model:
            model = self._load_default_model()

        self.llm_client = determine_llm_client(model.value)
        assistant_messages = assistant_messages or []
        messages = generate_messages(system_prompts, user_prompts, assistant_messages, model)
        logging.info(f"Executing LLM call with messages:\n{messages}")

        response = self._handle_rerun(messages, model, rerun_count, judgement_criteria, streaming)
        if not response:
            logging.error(f"No response from AI API: {self.llm_client}")
            raise Exception(AI_RESOURCE_FAILURE)

        logging.info(f"Execution finished with response:\n{response}")
        return response

    def _handle_rerun(
        self,
        messages: List[Dict[str, str]],
        model: AiModel,
        rerun_count: int,
        judgement_criteria: Optional[List[str]],
        streaming: bool = False
    ) -> str:
        """
        Executes the API call. If rerun_count is more than one, it delegates to the method that
        handles multiple, parallel re-run calls.

        :param messages: The list of message dictionaries to send.
        :param model: The selected AI model.
        :param rerun_count: Number of execution attempts.
        :param judgement_criteria: Criteria for response evaluation if multiple responses are produced.
        :param streaming: Whether to use the streaming API endpoint.
        :return: The AI response.
        """
        logging.info("EXECUTING PROMPT")
        if rerun_count == 1:
            response_call = (
                lambda: self.llm_client.get_ai_streaming_response(messages, model)
                if streaming else self.llm_client.get_ai_response(messages, model)
            )
            return Utility.execute_with_retries(response_call)

        # For multiple attempts, execute parallel re-run logic.
        logging.info("Parallel reruns enabled: executing multiple API calls.")
        return self._handle_multiple_reruns(messages, model, rerun_count, judgement_criteria, streaming)

    @specify_functionality_context("best_of")
    def _handle_multiple_reruns(
        self,
        messages: List[Dict[str, str]],
        model: AiModel,
        rerun_count: int,
        judgement_criteria: Optional[List[str]],
        streaming: bool = False
    ) -> str:
        """
        Handles multiple API calls in parallel (for re-run attempts) and then aggregates the results
        using the judgement criteria provided.

        :param messages: Original messages used for the AI prompt.
        :param model: The selected AI model.
        :param rerun_count: The number of re-run attempts.
        :param judgement_criteria: Evaluation criteria for the multiple responses.
        :param streaming: Whether to use the streaming endpoint for the final call.
        :return: The aggregated AI response.
        """
        # Execute multiple calls to generate various responses.
        responses = Utility.execute_with_retries(
            lambda: self.llm_client.get_ai_response(messages, model, rerun_count=rerun_count)
        )
        logging.info(f"Re-run responses ({rerun_count}) : \n{responses}")

        combined_messages = generate_messages("", judgement_criteria, responses, model)
        response_call = (
            lambda: self.llm_client.get_ai_streaming_response(combined_messages, model)
            if streaming else self.llm_client.get_ai_response(combined_messages, model)
        )
        return Utility.execute_with_retries(response_call)

    @deprecated
    @handle_errors(raise_errors=True)
    def execute_function(
        self,
        system_prompts: List[str] | str,
        user_prompts: List[str] | str,
        function_schema: str,
        model: AiModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI
    ) -> Dict[str, object]:
        """
        Generates a structured response that adheres to the provided function schema.

        :param system_prompts: System messages guiding the function.
        :param user_prompts: User input.
        :param function_schema: The schema that defines the structure of the expected function output.
        :param model: The LLM model that will be used to execute the function
        :return: The generated structured response as a dictionary.
        :raises ValueError: If no function schema is provided.
        :raises RuntimeError: If the API fails to return a valid function response.
        """
        self.llm_client = determine_llm_client(model.value)
        if not function_schema:
            logging.error("No function schema provided.")
            raise ValueError(FUNCTION_SCHEMA_EMPTY)

        # Generate messages without additional assistant context.
        messages = generate_messages(system_prompts, user_prompts, model=model)
        response = Utility.execute_with_retries(
            lambda: self.llm_client.get_ai_function_response(messages, function_schema, model)
        )
        if response is None:
            logging.error("Failed to receive a valid response from the AI API.")
            raise RuntimeError(NO_RESPONSE_OPEN_AI_API)

        logging.info(f"Function executed successfully with response: {response}")
        return response


if __name__ == '__main__':
    try:
        ai_orchestrator = AiOrchestrator()
        result = ai_orchestrator.execute(
            system_prompts=[(
                "Given the following user prompt, what are your questions? "
                "Be concise and targeted. What would you like to know before proceeding?"
            )],
            user_prompts=["rewrite solution.txt to be more concise"],
            model=ChatGptModel.CHAT_GPT_O1_MINI
        )
        print(result)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

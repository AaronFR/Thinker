import logging
from typing import List, Dict, Optional

from deprecated.classic import deprecated

from AiOrchestration.AiModel import AiModel
from AiOrchestration.ChatGptModel import ChatGptModel
from AiOrchestration.GeminiModel import GeminiModel
from AiOrchestration.ChatGptMessageBuilder import generate_messages
from Constants.Exceptions import AI_RESOURCE_FAILURE, FUNCTION_SCHEMA_EMPTY, NO_RESPONSE_OPEN_AI_API
from Data.Configuration import Configuration
from Utilities.Contexts import set_functionality_context
from Utilities.Decorators.Decorators import handle_errors, specify_functionality_context
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
        system_prompts: list[str] | str,
        user_prompts: list[str] | str,
        rerun_count: int = 1,
        loop_count: int = 1,
        judgement_criteria: list[str] | None = None,
        model: AiModel | None = None,
        assistant_messages: list[str] | None = None,
        streaming: bool = False
    ) -> str:
        """
        Generates an LLM response based on the given prompts while supporting both parallel best-of and iterative loops.

        This function always runs a loop (even for loop_count == 1). On the first iteration the original
        user prompt is used; on subsequent iterations, an improved answer is generated using the previous response
        and the judgement criteria.

        :param system_prompts: Contextual instructions for the AI.
        :param user_prompts: The user's instructions.
        :param rerun_count: Number of parallel responses to generate per iteration.
        :param loop_count: Number of sequential loop iterations.
        :param judgement_criteria: Criteria to judge and consolidate responses.
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

        loop_responses = []
        previous_answer = None

        for iteration in range(1, loop_count + 1):
            if iteration == 1:
                prompt_content = user_prompts
            else:
                set_functionality_context("loops")
                prompt_content = (
                    "Review your previous answer and provide an improved solution to the user's original request.\n"
                    f"User prompt: {user_prompts}\n"
                    f"Previous output: {previous_answer}\n"
                    f"{judgement_criteria}"
                )

            messages = generate_messages(system_prompts, prompt_content, assistant_messages, model)
            logging.info(f"Iteration {iteration} messages:\n{messages}")

            # Use streaming only on the final iteration if requested.
            iteration_streaming = streaming if iteration == loop_count else False
            iteration_response = self._handle_rerun(
                messages,
                model,
                rerun_count,
                judgement_criteria + system_prompts if judgement_criteria else system_prompts,
                iteration_streaming
            )

            if not iteration_response:
                logging.error(f"No response from AI API during iteration {iteration} using client {self.llm_client}")
                raise Exception(AI_RESOURCE_FAILURE)

            logging.info(f"Iteration {iteration} completed with response")
            loop_responses.append(iteration_response)
            previous_answer = iteration_response

        if loop_count > 1:
            set_functionality_context(None)

        logging.info(f"Final consolidated response:\n{previous_answer}")
        return previous_answer

    def _handle_rerun(
        self,
        messages: List[Dict[str, str]],
        model: AiModel,
        rerun_count: int,
        judgement_criteria: Optional[List[str]],
        streaming: bool = False
    ) -> str:
        """
        Executes the LLM API call. If rerun_count is more than one, it delegates to the method that
        handles multiple, parallel re-run calls.

        :param messages: The list of message dictionaries as reference.
        :param model: The selected AI model.
        :param rerun_count: Number of parallel responses to generate.
        :param judgement_criteria: Criteria for evaluating multiple responses.
        :param streaming: Whether to use the streaming endpoint.
        :return: The AI response.
        """
        logging.info("EXECUTING PROMPT")
        if rerun_count == 1:
            response_call = (
                lambda: self.llm_client.get_ai_streaming_response(messages, model)
                if streaming else self.llm_client.get_ai_response(messages, model)
            )
            return Utility.execute_with_retries(response_call)

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

        :param messages: The original messages used for the prompt.
        :param model: The LLM model to be used.
        :param rerun_count: Number of parallel runs.
        :param judgement_criteria: Criteria used to evaluate and merge responses.
        :param streaming: Whether the final call should be streamed.
        :return: The aggregated AI response.
        """
        responses = Utility.execute_with_retries(
            lambda: self.llm_client.get_ai_response(messages, model, rerun_count=rerun_count)
        )
        logging.info(f"Re-run responses ({rerun_count}) : \n{responses}")

        # ToDo: Could add a system message to detail how to select a best of response
        # ToDo: messages is added to specifically handle the case where the user refers to a prior message/file
        #  There may be some filtering that can be performed, for better performance.
        combined_messages = generate_messages("", judgement_criteria, responses, model) + messages
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
        Generates a structured response adhering to the provided function schema.

        :param system_prompts: System messages guiding the function.
        :param user_prompts: User input.
        :param function_schema: The schema defining the expected output structure.
        :param model: The LLM model that will be used to execute the function
        :return: The generated function response as a dictionary.
        :raises ValueError: If no function schema is provided.
        :raises RuntimeError: If no valid response is received from the API.
        """
        self.llm_client = determine_llm_client(model.value)
        if not function_schema:
            logging.error("No function schema provided.")
            raise ValueError(FUNCTION_SCHEMA_EMPTY)

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
        # Example: 2 loops with each loop running 3 parallel best-of responses.
        result = ai_orchestrator.execute(
            system_prompts=[(
                "Given the following user prompt, what are your follow-up questions? "
                "Be concise and targeted."
            )],
            user_prompts=["rewrite solution.txt to be more concise"],
            model=ChatGptModel.CHAT_GPT_4_OMNI_MINI,
            rerun_count=3,
            loop_count=2,
            streaming=True  # Use streaming for the final consolidated response
        )
        print(result)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

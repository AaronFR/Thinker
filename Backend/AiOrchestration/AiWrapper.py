import abc
import logging
from typing import List, Dict, Union, Generator

from AiOrchestration.AiModel import AiModel
from AiOrchestration.GeminiModel import GeminiModel
from Constants import Globals
from Data.NodeDatabaseManagement import NodeDatabaseManagement as NodeDB
from Utilities.Contexts import get_message_context, get_functionality_context


class AiWrapper(abc.ABC):
    """
    Abstract base class that defines a common interface for AI API wrappers.
    Both GeminiWrapper and ChatGptWrapper must implement the following methods:
      - get_ai_response: Get a complete answer (or list of answers) from the underlying API.
      - get_ai_streaming_response: Get streaming responses as a generator.
      - get_ai_function_response: Get a structured (function) response.
      - calculate_prompt_cost: Calculate cost based on tokens and perform accounting.
    """

    @abc.abstractmethod
    def get_ai_response(
            self,
            messages: List[Dict[str, str]],
            model,
            rerun_count: int = 1
    ) -> Union[str, List[str]]:
        """Request a full AI response based on a list of messages."""
        pass

    @abc.abstractmethod
    def get_ai_streaming_response(
            self,
            messages: List[Dict[str, str]],
            model
    ) -> Generator[Dict, None, str]:
        """Request a streaming AI response."""
        pass

    @abc.abstractmethod
    def get_ai_function_response(
            self,
            messages: List[Dict[str, str]],
            function_schema,
            model
    ) -> Dict:
        """Request a structured function call response from the API."""
        pass

    @staticmethod
    def calculate_prompt_cost(input_tokens: int, output_tokens: int, model: AiModel):
        """
        Calculates the estimated cost of a call to an individual AI API
        Gemini models will also expense a SYSTEM budget parameter to track total costs for the application

        :param input_tokens: prompt tokens
        :param output_tokens: response tokens from the openAi model
        :param model: the specific OpenAI model being used, the non Mini version is *very* expensive,
        and should be used rarely
        """
        input_cost = input_tokens * model.input_cost
        output_cost = output_tokens * model.output_cost
        total_cost = (input_cost + output_cost)

        Globals.current_request_cost += total_cost

        NodeDB().deduct_from_user_balance(total_cost)
        if type(model) == GeminiModel:
            NodeDB().deduct_from_system_gemini_balance(total_cost)

        message_id = get_message_context()
        if message_id:
            logging.info(f"Expensing ${total_cost} to USER_PROMPT Node[{message_id}]")
            NodeDB().expense_node(message_id, total_cost)

        functionality = get_functionality_context()
        if functionality:
            logging.info(f"Expensing ${total_cost} against {functionality} functionality.")
            NodeDB().expense_functionality(functionality, total_cost)

        logging.info(
            f"Request cost [{model}] - Input tokens: {input_tokens} ${input_cost}, "
            f"Output tokens: {output_tokens}, ${output_cost} \n"
            f"Total cost: ${total_cost:.4f}"
        )

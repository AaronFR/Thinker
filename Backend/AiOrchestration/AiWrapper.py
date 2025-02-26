import abc
import logging
from typing import List, Dict, Union, Generator

from deprecated.classic import deprecated

from AiOrchestration.AiModel import AiModel
from AiOrchestration.GeminiModel import GeminiModel
from Constants import Globals
from Data.NodeDatabaseManagement import NodeDatabaseManagement as NodeDB
from Utilities.Contexts import get_message_context, get_functionality_context
from Utilities.Utility import Utility


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
    ) -> str:
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

    @deprecated
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
    def can_afford_request(model: AiModel, messages: List[Dict[str, str]], rerun_count: int = 1) -> bool:
        cost_estimate = AiWrapper._cost_guesstimate(model, messages, rerun_count)
        user_balance = NodeDB().get_user_balance()

        # 3 cents is the point where a possible overdraft is basically negligible
        if user_balance - cost_estimate < -0.03:
            return False
        NodeDB().earmark_from_user_balance(cost_estimate)

        return True

    @staticmethod
    def _cost_guesstimate(
            model: AiModel,
            messages: List[Dict[str, str]],
            rerun_count: int = 1
    ) -> float:
        """
        Estimates cost based on token usage. This is a rough estimation since the final output length is unknown.

        The advantage of estimating is that we can tell the user their request can't be completed with a rough degree of
        certainty, but a user would only deal with this uncertainty when making expensive requests with a close to
        exhausted budget.

        We could exactly calculate each output cost as it occurs in a stream but this would slow down output and
        potentially lead to malformed output
        - the user paying for content and not actually getting it, which isn't acceptable.

        :param model: The chosen AI model.
        :param messages: The list of message dictionaries.
        :param rerun_count: The number of reruns requested.
        :return: The estimated cost as a float.
        """
        input_tokens = Utility().calculate_tokens_used(messages, model)
        estimated_output_tokens = 2000

        input_cost = input_tokens * model.input_cost
        output_costs = estimated_output_tokens * model.output_cost
        total_costs = input_cost + output_costs
        if rerun_count > 1:
            total_costs *= rerun_count

        logging.info(f"Total guesstimated cost: {total_costs}")
        return total_costs

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

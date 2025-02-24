import enum
import os
from typing import Optional, Type, TypeVar

from Constants.Exceptions import NOT_IMPLEMENTED_IN_INTERFACE

# Define a TypeVar constrained to subclasses of AiModel
T = TypeVar('T', bound='AiModel')


class AiModel(enum.Enum):
    """
    Base Enum class for AI Models.
    """

    def __init__(self, model_str: str, default_input_cost: float, default_output_cost: float):
        # Allow environment variables to override default costs
        env_input = os.environ.get(f'INPUT_COST_{self.name}')
        env_output = os.environ.get(f'OUTPUT_COST_{self.name}')
        self._model_str = model_str
        self.input_cost = float(env_input) if env_input is not None else default_input_cost  # $/token
        self.output_cost = float(env_output) if env_output is not None else default_output_cost   # $/token

    @property
    def value(self) -> str:
        """Return the underlying model identifier required by the API."""
        return self._model_str

    @classmethod
    def find_enum_value(cls: Type[T], model_name: Optional[str] = None) -> T:
        """
        Search for the corresponding enum value based on the model name string provided.
        Otherwise, default to the subclass-specific default model.

        :param model_name: The model name to search for.
        :return: Corresponding enum member if found; otherwise, the default member.
        """
        if model_name is None:
            return cls.get_default()

        for model in cls:
            if model.value == model_name:
                return model

        return cls.get_default()

    @classmethod
    def get_default(cls: Type[T]) -> T:
        """
        Return the default enum member.
        Must be implemented by each subclass.

        :return: Default enum member.
        :rtype: T
        """
        raise NotImplementedError(NOT_IMPLEMENTED_IN_INTERFACE)

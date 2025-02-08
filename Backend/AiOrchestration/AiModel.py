import enum
from typing import Optional, Type, TypeVar

from Constants.Exceptions import NOT_IMPLEMENTED_IN_INTERFACE

# Define a TypeVar constrained to subclasses of AiModel
T = TypeVar('T', bound='AiModel')


class AiModel(enum.Enum):
    """
        Base Enum class for AI Models.
        """

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

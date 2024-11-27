import logging
from pprint import pformat
from typing import List, Dict

from AiOrchestration.ChatGptWrapper import ChatGptRole
from AiOrchestration.ChatGptModel import ChatGptModel
from Data.FileManagement import FileManagement
from Utilities.Utility import Utility


def generate_messages(
    system_prompts: List[str] | str,
    user_prompts: List[str],
    assistant_messages: List[str] = None,
    input_files: List[str] = None,
    model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI
) -> List[Dict[str, str]]:
    """Generates the list of messages by composing user and system prompts.

    :param system_prompts: Messages providing contextual guidance to the LLM
    :param user_prompts: User prompts representing instructions
    :param assistant_messages: History of the current interaction
    :param input_files: selected file paths as reference for the prompt
    :param model: The selected model
    :return: List of formatted messages for LLM processing
    """
    logging.debug(f"Composing messages with user prompts: {pformat(user_prompts, width=280)}")

    system_prompts = Utility.ensure_string_list(system_prompts)
    user_prompts = Utility.ensure_string_list(user_prompts)
    if assistant_messages:
        assistant_messages = Utility.ensure_string_list(assistant_messages)

    messages = build_role_messages(input_files, system_prompts, user_prompts, assistant_messages, model)
    logging.debug(f"Messages: {pformat(messages)}")
    logging.info(f"Tokens used (limit 128k): {Utility.calculate_tokens_used(messages)}")
    return messages


def build_role_messages(
    input_files: List[str],
    system_prompts: List[str],
    user_prompts: List[str],
    assistant_messages: List[str] = None,
    model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI
) -> List[Dict[str, str]]:
    """Creates a list of messages to be handled by the ChatGpt API, the most important messages is the very last
    'latest' message in the list

    :param input_files: selected file paths as reference for the prompt
    :param system_prompts: list of instructions to be saved as system info
    :param user_prompts: primary initial instruction and other supplied material
    :param assistant_messages: messages which represent the prior course of the conversation
    :param model: The selected model, defaulting to the economical ChatGpt 4o mini. o1 models will trigger a
     reformat of system_prompts into user_prompts
    :return:
    """
    role_messages = []
    if assistant_messages:
        role_messages.extend(
            _format_message(ChatGptRole.ASSISTANT, prompt) for prompt in assistant_messages)

    logging.info(f"Number of input files: {input_files}")
    for file in input_files:
        try:
            content = FileManagement.read_file(file)
            role_messages.append(
                _format_message(ChatGptRole.USER, f"<{file}>{content}</{file}>"))
        except FileNotFoundError:
            logging.error(f"File not found: {file}. Please ensure the file exists.")
            role_messages.append(
                _format_message(ChatGptRole.SYSTEM, f"File not found: {file}"))
        except Exception as e:
            logging.error(f"Error reading file {file}: {e}")
            role_messages.append(
                _format_message(ChatGptRole.SYSTEM, f"Error reading file {file}. Exception: {e}"))

    role_messages += [
         _format_message(ChatGptRole.SYSTEM, prompt) for prompt in system_prompts
     ] + [
         _format_message(ChatGptRole.USER, prompt) for prompt in user_prompts
     ]

    if model == ChatGptModel.CHAT_GPT_O1_MINI or model == ChatGptModel.CHAT_GPT_O1_PREVIEW:
        role_messages = _handle_o1_model_messages(role_messages)

    logging.info(f"Generated role messages - [{model}] : {role_messages}")

    return role_messages


def _format_message(role: ChatGptRole, content: str) -> Dict[str, str]:
    """Format a message for OpenAI API."""
    return {"role": role.value, "content": content}


def _handle_o1_model_messages(role_messages: List[Dict[str, str]]):
    """
    For the time being 01 models are in beta and cannot process system prompts
    (I honestly have no idea how that's remotely possible but whatever,
    I'm not the one being paid $150,000+ to muck about)
    """
    non_system_messages = [
        role_message for role_message in role_messages if
        role_message.get("role") != ChatGptRole.SYSTEM.value
    ]

    system_messages = [
        {**role_message, "role": ChatGptRole.USER.value}
        for role_message in role_messages
        if role_message.get("role") == ChatGptRole.SYSTEM.value
    ]
    # Reassemble the list with system messages first, i.e. first in the message log history
    role_messages = system_messages + non_system_messages
    return role_messages

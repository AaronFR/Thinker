import logging
import os
from typing import List, Dict

from AiOrchestration.ChatGptWrapper import ChatGptRole
from AiOrchestration.ChatGptModel import ChatGptModel
from Data.Files.StorageMethodology import StorageMethodology
from Utilities.Utility import Utility


def generate_messages(
    system_prompts: List[str] | str,
    user_prompts: List[str],
    assistant_messages: List[str] = None,
    model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI
) -> List[Dict[str, str]]:
    """Generates the list of messages by composing user and system prompts.

    :param system_prompts: Messages providing contextual guidance to the LLM
    :param user_prompts: User prompts representing instructions
    :param assistant_messages: History of the current interaction
    :param model: The selected model
    :return: List of formatted messages for LLM processing
    """
    logging.debug(f"Composing messages with user prompts: {user_prompts}")

    system_prompts = Utility.ensure_string_list(system_prompts)
    user_prompts = Utility.ensure_string_list(user_prompts)
    if assistant_messages:
        assistant_messages = Utility.ensure_string_list(assistant_messages)

    messages = build_role_messages(system_prompts, user_prompts, assistant_messages, model)
    logging.debug(f"Messages: {messages}")
    logging.info(f"Tokens used (limit 128k): {Utility.calculate_tokens_used(messages)}")
    return messages


def build_role_messages(
    system_prompts: List[str],
    user_prompts: List[str],
    assistant_messages: List[str] = None,
    model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI
) -> List[Dict[str, str]]:
    """Creates a list of messages to be handled by the ChatGpt API, the most important messages is the very last
    'latest' message in the list

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
            format_message(ChatGptRole.ASSISTANT, prompt) for prompt in assistant_messages)

    role_messages += [
         format_message(ChatGptRole.SYSTEM, prompt) for prompt in system_prompts
     ] + [
         format_message(ChatGptRole.USER, prompt) for prompt in user_prompts
     ]

    if model == ChatGptModel.CHAT_GPT_O1_MINI or model == ChatGptModel.CHAT_GPT_O1_PREVIEW:
        role_messages = _handle_o1_model_messages(role_messages)

    logging.info(f"Generated role messages - [{model}] : {role_messages}")

    return role_messages


def format_message(role: ChatGptRole, content: str) -> Dict[str, str]:
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

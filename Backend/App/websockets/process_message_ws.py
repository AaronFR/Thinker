import logging

import shortuuid
from flask_socketio import emit, SocketIO
from flask import abort

from App.extensions import socket_rate_limit, user_key_func
from Constants.Constants import BASE_LIMIT
from Data.CategoryManagement import CategoryManagement
from Functionality.Organising import Organising
from Personas.Coder import Coder
from Personas.Writer import Writer
from Utilities.AuthUtils import login_required_ws
from Utilities.Contexts import set_message_context, get_message_context, get_category_context, set_streaming
from Utilities.CostingUtils import balance_required
from Utilities.Routing import parse_and_validate_data

ERROR_NO_PROMPT = "No prompt found"
PROCESS_MESSAGE_SCHEMA = {
    "prompt": {"required": True},
    "additionalQA": {"required": False, "default": None},
    "tags": {"required": False, "default": {}, "type": dict},
    "files": {"required": False, "default": [], "type": list},
    "messages": {"required": False, "default": [], "type": list},
}


def init_process_message_ws(socketio: SocketIO):
    """
    Initializes the SocketIO event handlers for processing and terminating messages.

    :param socketio: The Flask-SocketIO instance.
    """

    @socketio.on('connect')
    def handle_connect():
        logging.info(f"🟢 Client connected")

    @socketio.on('disconnect_from_request')
    @login_required_ws
    def disconnect_from_request():
        logging.info(f"🔴 Client disconnected")

        # Send acknowledgment back to client
        return {'status': 'Disconnecting from request'}

    @socketio.on('start_stream')
    @login_required_ws
    @balance_required
    @socket_rate_limit(key_func=user_key_func, limit=BASE_LIMIT, period=86400)  # 1 per day (86400 seconds)
    def process_message(data):
        """
        Accept a user prompt and process it through the selected persona.

        ToDo: refresh tokens on streams are a bit difficult. Implement if its possible in the release
         to not hit a regular automatically-refreshing request
        ToDo: user input sanitization needs to be employed.

        :param data: A dictionary containing the user prompt and additional parameters.
        :raises ValueError: If the prompt or persona is invalid.
        """
        logging.info(f"process_message triggered with data: {data}")
        try:
            set_streaming(True)

            message_uuid = str(shortuuid.uuid())
            set_message_context(message_uuid)
            parsed_data = parse_and_validate_data(data, PROCESS_MESSAGE_SCHEMA)

            user_prompt = parsed_data["prompt"]
            if not user_prompt:
                abort(400)

            if parsed_data["additionalQA"]:
                user_prompt += f"\nAdditional Q&A context: \n{parsed_data['additionalQA']}"

            tags = parsed_data["tags"]
            files = parsed_data["files"]
            messages = parsed_data["messages"]

            selected_persona = get_selected_persona(data)

            file_references = Organising.process_files(files)

            category = CategoryManagement.determine_category(user_prompt, tags.get("category"))
            CategoryManagement.create_initial_user_prompt_and_possibly_new_category(category, user_prompt)

            response_message = selected_persona.query(
                user_prompt,
                file_references,
                [message["id"] for message in messages],
                tags
            )
            logging.info(f"Response generated [%s]: %s", get_message_context(), response_message)

            chunk_content = []
            for chunk in response_message:
                if 'content' in chunk:
                    content = chunk['content']
                    chunk_content += content
                    emit('response', {'content': content})
                elif 'stream_end' in chunk:
                    emit('stream_end', {
                        "prompt": user_prompt,
                        "message_id": get_message_context()
                    })
                    emit("update_workflow", {"status": "finished"})
                    break  # Exit the loop after emitting 'stream_end

            full_message = "".join(chunk_content)

            Organising.store_prompt_data(user_prompt, full_message, category)

            logging.info(f"response message: {response_message}")

            emit('trigger_refresh', {
                "category_name": category,
                "category_id": get_category_context(),
                "prompt": user_prompt
            })

            # ToDo: termination needed for closing flask request?

        except ValueError as ve:
            logging.error("Value error: %s", str(ve))
            emit('error', {"error": str(ve)})
        except Exception as e:
            logging.exception("Failed to process message")
            emit('error', {"error": str(e)})


def get_selected_persona(data):
    """ Determine the selected persona or default to 'coder'. """
    persona_selection = data.get("persona")
    if persona_selection == 'coder':
        persona = Coder("Coder")
    if persona_selection == 'writer':
        persona = Writer("Writer")
    if persona_selection not in ['coder', 'writer']:
        logging.warning("Invalid persona selected, defaulting to coder")
        return Coder("Default")
    return persona

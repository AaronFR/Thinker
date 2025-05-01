import logging
import time

import shortuuid
from flask_socketio import emit, SocketIO

from App.extensions import socket_rate_limit, user_key_func, system_key_func
from Constants.Constants import BASE_LIMIT, USER_BASE_LIMIT
from Data.CategoryManagement import CategoryManagement
from Functionality.Organising import Organising
from Workers.Coder import Coder
from Workers.Writer import Writer
from Utilities.Decorators.AuthorisationDecorators import login_required_ws
from Utilities.Contexts import set_message_context, get_message_context, get_category_context, set_streaming, \
    set_functionality_context
from Utilities.Decorators.PaymentDecorators import balance_required
from Utilities.Routing import parse_and_validate_data

ERROR_NO_PROMPT = "No prompt found"
PROCESS_MESSAGE_SCHEMA = {
    "prompt": {"required": True, "type": str},
    "additionalQA": {"required": False, "default": None},
    "tags": {"required": False, "default": {}, "type": dict},
    "files": {"required": False, "default": [], "type": list},
    "messages": {"required": False, "default": [], "type": list},
    "worker": {"required": False, "default": "coder"}
}

WORKER_MAPPING = {
    "coder": Coder,
    "writer": Writer,
}
DEFAULT_WORKER = "coder"


def init_process_message_ws(socketio: SocketIO):
    """Initializes SocketIO event handlers for message processing."""

    @socketio.on('connect')
    def handle_connect():
        logging.info("🟢 Client connected")

    @socketio.on('disconnect_from_request')
    @login_required_ws
    def disconnect_from_request():
        logging.info("🔴 Client disconnected")
        return {'status': 'Disconnecting from request'}

    @socketio.on('start_stream')
    @login_required_ws
    @balance_required
    @socket_rate_limit(key_func=system_key_func, limit=BASE_LIMIT, period=86400)  # 1 day (86400 seconds)
    @socket_rate_limit(key_func=user_key_func, limit=USER_BASE_LIMIT, period=86400)
    def process_message(data):
        """
        Accept a user prompt and process it through the selected worker.

        :param data: A dictionary containing the user prompt and additional parameters.
        :raises ValueError: If the prompt or worker is invalid.
        """
        start_time = time.time()
        message_uuid = str(shortuuid.uuid())
        set_message_context(message_uuid)
        logging.info(f"process_message triggered [{message_uuid}] with data: {data}")

        try:
            set_streaming(True)
            parsed_data = parse_and_validate_data(data, PROCESS_MESSAGE_SCHEMA)

            user_prompt = parsed_data["prompt"]
            if not user_prompt:
                raise ValueError(ERROR_NO_PROMPT)

            additional_qa = parsed_data.get("additionalQA")
            if additional_qa:
                user_prompt += f"\nAdditional Q&A context:\n{additional_qa}"

            tags = parsed_data["tags"]
            files = parsed_data["files"]
            messages = parsed_data["messages"]
            worker_name = tags.get("worker")

            selected_worker = get_selected_worker(worker_name)
            file_references = Organising.process_files(files)

            category = CategoryManagement.determine_category(user_prompt, tags.get("category"))
            CategoryManagement.create_initial_user_prompt_and_possibly_new_category(category, user_prompt)

            response_stream = selected_worker.query(
                user_prompt,
                file_references,
                [message["id"] for message in messages],
                tags
            )
            logging.info(f"[{message_uuid}] Response generated, streaming...")

            full_message = stream_response(response_stream, message_uuid)
            Organising.store_prompt_data(user_prompt, full_message, category)

            emit('trigger_refresh', {
                "category_name": category,
                "category_id": get_category_context(),
                "prompt": user_prompt
            })

        except ValueError as ve:
            logging.exception(f"[{message_uuid}] Validation error {str(ve)}")
            emit('error', {"error": str(ve)})
        except Exception as e:
            logging.exception(f"[{message_uuid}] Failed to process message")
            emit('error', {"error": str(e)})
        finally:
            finish_time = time.time()
            job_duration = finish_time - start_time
            logging.info(f"[{message_uuid}] Request completed in {job_duration:.2f}s", )

            emit('stream_end', {
                "prompt": user_prompt,
                "message_id": get_message_context()
            })
            emit("update_workflow", {
                "status": "finished",
                "duration": job_duration
            })


def stream_response(response_stream, message_uuid: str) -> str:
    """
    Iterates over the streaming response from the worker and emits events.
    Combines all content parts and ensures a stream_end event is sent.
    :param response_stream: Generator yielding response chunks.
    :return: The full concatenated response message.

    """
    full_message_parts = []
    try:
        for chunk in response_stream:
            if 'content' in chunk:
                content = chunk['content']
                full_message_parts.append(content)
                emit('response', {'content': content})
    except Exception as e:
        logging.exception(f"[{message_uuid}] Streaming error {e}")
        emit('error', {"error": "Streaming interrupted."})
    finally:
        set_functionality_context(None)  # Wiping any previously set context for a stream
        return "".join(full_message_parts)


def get_selected_worker(worker_name: str):
    """
    Determines the selected worker based on the provided name, defaulting to Coder if the worker name is invalid.
    """
    if not worker_name:
        return WORKER_MAPPING[DEFAULT_WORKER]("default")

    worker_class = WORKER_MAPPING.get(worker_name.lower(), WORKER_MAPPING[DEFAULT_WORKER])
    return worker_class(worker_name)

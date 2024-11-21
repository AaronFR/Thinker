import json
import logging

from flask_socketio import emit

from Data.CategoryManagement import CategoryManagement
from Functionality.Organising import Organising
from Personas.Coder import Coder
from Utilities.auth_utils import login_required

ERROR_NO_PROMPT = "No prompt found"


def init_process_message_ws(socketio):
    @socketio.on('start_stream')
    @login_required
    def process_message(data):
        """
        Accept a user prompt and process it through the selected persona.

        ToDo: refresh tokens on streams are a bit difficult. Implement if its possible in the release
         to not hit a regular automatically-refreshing request

        :param data: A dictionary containing the user prompt and additional parameters.
        :raises ValueError: If the prompt or persona is invalid.
        """
        logging.info(f"process_message triggered with data: {data}")

        try:
            user_prompt = data.get("prompt")
            if user_prompt is None:
                emit('error', {"error": ERROR_NO_PROMPT})
                return

            additional_qa = data.get("additionalQA")
            if additional_qa:
                user_prompt = f"{user_prompt}\nAdditional Q&A context: \n{additional_qa}"

            tags = data.get('tags', {})
            if isinstance(tags, str):
                tags = json.loads(tags)
                if "tags" in tags:
                    tags = tags["tags"]
            logging.info(f"Loading the following tags while processing the prompt: {tags}")

            files = data.get("files")
            file_references = Organising.process_files(files)

            messages = data.get("messages")
            selected_message_ids = [message["id"] for message in messages]

            category_management = CategoryManagement()
            tag_category = tags.get("category")
            if tag_category:
                logging.info(f"tag specified category: {tag_category}")
                category = tag_category
            else:
                category = category_management.categorise_prompt_input(user_prompt)
                tags["category"] = category

            selected_persona = get_selected_persona(data)
            response_message = selected_persona.query(user_prompt, file_references, selected_message_ids, tags)
            logging.info("Response generated: %s", response_message)

            chunk_content = []
            for chunk in response_message:
                if 'content' in chunk:
                    content = chunk['content']
                    chunk_content += content
                    emit('response', {'content': content})
                elif 'stream_end' in chunk:
                    emit('stream_end')
                    break  # Exit the loop after emitting 'stream_end

            full_message = "".join(chunk_content)
            # ToDo: should be an ancillary side job, currently slows down receiving a response if the database doesn't respond quickly
            Organising.categorize_and_store_prompt(user_prompt, full_message, category)

            logging.info(f"response message: {response_message}")

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
    if persona_selection not in ['coder']:
        logging.warning("Invalid persona selected, defaulting to coder")
        return Coder("Default")
    return persona

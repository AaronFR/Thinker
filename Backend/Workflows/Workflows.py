from typing import List, Dict

from AiOrchestration.GeminiModel import GeminiModel
from Data.Configuration import Configuration
from Data.Files.StorageMethodology import StorageMethodology

UPDATE_WORKFLOW_STEP = "update_workflow_step"


def display_parameters(
    initial_message: str = None,
    model: str = None,
    file_references: List[str] = None,
    selected_messages: List[str] = None,
    best_of: int = 1,
    loops: int = 1,
) -> Dict[str, str]:
    """
    Construct a consistent dictionary of parameters for workflow steps.
    If no value exists for the value the key will not be included in the returned dictionary.
    """
    params = {
        "Prompt": initial_message,
        "Model": model,
        "Files referenced": "\n".join(file_references) if file_references else None,
        "Messages referenced": "\n".join(selected_messages) if selected_messages else None,
        "Parallel runs": best_of if best_of > 1 else None,
        "Sequential runs": loops if loops > 1 else None,
    }
    return {key: value for key, value in params.items() if value is not None}


def create_step(
    step_id: int,
    module: str,
    description: str,
    parameters: Dict[str, str],
    status: str = "pending",
    response: Dict = None
) -> Dict:
    """
    Create a standardized workflow step.
    """
    return {
        "step_id": step_id,
        "module": module,
        "description": description,
        "parameters": parameters,
        "status": status,
        "response": response or {}
    }


def build_workflow_base(workflow_name: str, version: str, steps: List[Dict]) -> Dict:
    """
    Wrap a set of steps into a complete workflow dictionary.
    """
    return {
        "version": version,
        "workflow_name": workflow_name,
        "steps": steps,
        "status": "pending"
    }


def get_background_model() -> str:
    """
    Retrieve the default background model from configuration.
    """
    config = Configuration.load_config()
    return config.get("models", {}).get("default_background_model", GeminiModel.GEMINI_2_FLASH.value)


# Workflow Generators

def generate_chat_workflow(
    initial_message: str,
    file_references: List[str],
    selected_messages: List[str],
    model: str,
    best_of: int = 1,
    loops: int = 1,
) -> Dict:
    """
    Generate a workflow dictionary for chat-based interactions.
    """
    step = create_step(
        step_id=1,
        module="Chat",
        description="Respond to the prompt and any additional files or reference messages",
        parameters=display_parameters(initial_message, model, file_references, selected_messages, best_of, loops)
    )
    return build_workflow_base("Chat Workflow", "1.0", [step])


def generate_write_workflow(
    initial_message: str,
    file_references: List[str],
    selected_messages: List[str],
    model: str,
    best_of: int = 1,
    loops: int = 1,
) -> Dict:
    """
    Generate a workflow dictionary for writing operations.
    """
    config = Configuration.load_config()
    steps = [
        create_step(
            step_id=1,
            module="Planning Response",
            description="Plan out a Response",
            parameters=display_parameters(initial_message, model, file_references, selected_messages, best_of, loops)
        ),
        create_step(
            step_id=2,
            module="Writing to File",
            description="Write out solution as a valid file",
            parameters={"file_name": "pending...", "model": model}
        )
    ]
    if config.get("workflows", {}).get("summarise", False):
        steps.append(
            create_step(
                step_id=3,
                module="Summarise",
                description="Quickly summarise the workflow's results",
                parameters={"model": get_background_model()}
            )
        )
    return build_workflow_base("Write Workflow", "1.1", steps)


def generate_write_pages_workflow(
    initial_message: str,
    page_count: int,
    file_references: List[str],
    selected_messages: List[str],
    model: str,
    best_of: int = 1,
    loops: int = 1,
) -> Dict:
    """
    Generate a workflow dictionary for writing pages with dynamic steps.
    """
    steps = []
    step_id = 1

    # Define Pages step
    steps.append(create_step(
        step_id,
        module="Plan document",
        description="Writes out a list of instructions for each individual page",
        parameters=display_parameters(initial_message, model, file_references, selected_messages, best_of, loops)
    ))
    step_id += 1

    # Dynamic Steps: Append to File per page iteration
    for i in range(1, page_count + 1):
        steps.append(create_step(
            step_id,
            module=f"Page {i}",
            description=f"Append content to the specified file for page {i}.",
            parameters=display_parameters(
                initial_message=None,
                model=model,
                file_references=file_references,
                selected_messages=selected_messages,
                best_of=best_of,
                loops=loops
            )
        ))
        step_id += 1

    config = Configuration.load_config()
    if config.get("workflows", {}).get("summarise", False):
        steps.append(create_step(
            step_id,
            module="Summarise",
            description="Quickly summarise the workflow",
            parameters=display_parameters(
                initial_message=None,
                model=get_background_model(),
                file_references=file_references,
                selected_messages=selected_messages
            )
        ))
    return build_workflow_base("Write Pages Workflow", "1.1", steps)


def generate_auto_workflow(
    file_references: List[str],
    selected_messages: List[str],
    model: str,
    best_of: int = 1,
    loops: int = 1,
) -> Dict:
    """
    Generate a workflow dictionary for automatic processing of multiple files.
    """
    steps = []
    step_id = 1

    # Create a processing step for each file reference.
    for file_reference in file_references:
        file_name = StorageMethodology().extract_file_name(file_reference)
        steps.append(create_step(
            step_id,
            module=f"Process {file_name}",
            description="Processing file in accordance with user's initial message.",
            parameters=display_parameters(
                initial_message=None,
                model=model,
                file_references=file_references,
                selected_messages=selected_messages,
                best_of=best_of,
                loops=loops
            )
        ))
        step_id += 1

    config = Configuration.load_config()
    if config.get("workflows", {}).get("summarise", False):
        steps.append(create_step(
            step_id,
            module="Summarise",
            description="Quickly summarise the workflow",
            parameters=display_parameters(
                initial_message=None,
                model=get_background_model(),
                file_references=file_references,
                selected_messages=selected_messages
            )
        ))
    return build_workflow_base("Auto Workflow", "1.2", steps)

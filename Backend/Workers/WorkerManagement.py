import logging

from Workers.BaseWorker import BaseWorker
from Workers.Coder import Coder
from Workers.Default import Default
from Workers.Writer import Writer


WORKER_MAPPING = {
    "default": Default,
    "coder": Coder,
    "writer": Writer,
}
DEFAULT_WORKER = "default"


def get_selected_worker(worker_name: str) -> BaseWorker:
    """
    Determines the selected worker based on the provided name, defaulting if the worker name is invalid.
    """
    if not worker_name:
        return WORKER_MAPPING[DEFAULT_WORKER]("default")

    worker_class = WORKER_MAPPING.get(worker_name.lower(), False)

    if not worker_class:
        logging.warning(f"Invalid worker '{worker_name}'. Defaulting to {DEFAULT_WORKER}.")
        return WORKER_MAPPING[DEFAULT_WORKER]

    return worker_class(worker_name)

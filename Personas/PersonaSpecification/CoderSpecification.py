from Utilities.Configuration import Configuration


def load_configuration():
    config = Configuration.load_config()

    return f"""Following the following guidelines when writing code.
    All docstrings and class definitions must be written in the following style: {config['documentation']['style']}
    indentation: {config['code_style']['indentation']}
    line length: {config['code_style']['line_length']}
    imports_order: {config['code_style']['imports_order']}
    """


CODER_INSTRUCTIONS = "Just think through the question, step by step, prioritizing the most recent user prompt."

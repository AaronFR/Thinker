```markdown

# The Thinker

## Objectives
The primary objective of this project is to create an intelligent system that can evaluate tasks iteratively using machine learning techniques, providing automated solutions based on user-defined instructions and available resources. It aims to enhance decision-making processes by leveraging AI capabilities.

- Automate Problem-Solving: To provide a system that can evaluate and generate solutions for various tasks without extensive manual intervention.
- Modular-Architecture: That can explore and evaluate a wide range of tasks using AI-based thought processing, with flexibility and adaptability.

## Current Limitations

- The process can be slow due to the iterative nature of evaluations, as well as potential network call dependencies with the language model.
- While it can handle structured tasks, unexpected inputs may lead to ineffective results or erratic outputs.
- Parallel processing is not yet implemented, which could expedite task completion.


## Features
- **Iterative Task Evaluation**: Breaks down a user input task/prompt into individual parts to query iteratively.
- **Executive Thought Processing**: Uses an executive reasoning layer to determine action plans based on user tasks and available context files.

## Architecture
The project's architecture is designed with modularity in mind, allowing for the easy addition of new features and components. The key modules are structured as follows:

- **ThoughtProcess**: Coordinates the overall workflow. It initializes the thought process, evaluates tasks iteratively, manages logs, and saves outputs.
- **Thought**: Represents an individual call to a LLM api, the current state of a task and provides methods for interacting with the AI model to generate responses.
- **Prompter**: Interfaces with the AI model, sending requests and retrieving outputs based on specified prompts.


## Features to implement
- Ability for executive thoughts to demand a *section* of text be over-written and for an executor thought to act on such a plan
- Enhancements to the executive reasoning layer to handle more complex decision-making.
  - Improve the executive thought generation mechanism for more precise outputs.
- Utilise multiple outputs n= in Thought.py/get_openai_response
  - Introduce parallel processing for handling multiple tasks simultaneously to enhance performance.
- Implement a Directed Acyclic Graph (DAG) structure for task management to improve decision-making efficiency.
- Integrating additional AI models to enhance capability and accuracy.
- Ability to search wikipedia through api
  - ability to search web


```
`ThoughtProcess`
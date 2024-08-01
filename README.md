```markdown

# The Thinker

## Objectives
The primary objective of this project is to create an intelligent system that can evaluate tasks iteratively using machine learning techniques, providing automated solutions based on user-defined instructions and available resources. It aims to enhance decision-making processes by leveraging AI capabilities.

- Automate Problem-Solving: To provide a system that can evaluate and generate solutions for various tasks without extensive manual intervention.
- Modular-Architecture: That can explore and evaluate a wide range of tasks using AI-based thought processing, with flexibility and adaptability.

## Current Limitations

- ***Capability***The ThoughtProcessor operates like a public works department with its allocated budget of iterations: spend it all! The system can generate long reports but due to the inability to re-write text, the answers are not succinct.
- **Performance**: Iterating through a sequential series of LLM api calls takes time for each request, as the output data to review grows larger the time to process each executive thought grows larger.
- **Input Handling**: While the system manages structured tasks well, unexpected inputs can result in suboptimal or erratic outputs.
- **Lack of Parallel Processing**: The absence of parallel task management capabilities can hinder efficiency in completing tasks.

## Features
- **Iterative Task Evaluation**: The system decomposes user input tasks into individual components, allowing for progressive querying and processing.
- **Executive Thought Processing**: An executive reasoning layer formulates action plans based on provided tasks and relevant context files.

## Architecture
The project's architecture is designed with modularity in mind, allowing for the easy addition of new features and components. The key modules are structured as follows:

- **ThoughtProcess**: Coordinates the overall workflow. It initializes the thought process, evaluates tasks iteratively, manages logs, and saves outputs.
- **Thought**: Represents an individual call to a LLM api, the current state of a task and provides methods for interacting with the AI model to generate responses.
- **Prompter**: Interfaces with the AI model, sending requests and retrieving outputs based on specified prompts.


## Features to implement
To enhance the system's capabilities and efficiency, several features are planned for implementation:
- **Overwrite Capability**: Enable executive thoughts to dictate the overwriting of specific text sections, with executor thoughts carrying out those plans.
- **Enhanced Executive Reasoning**: Develop improvements to the executive thought generation for more accurate and complex decision-making.
- **Multiple Output Handling**: Allow `Thought.py/get_openai_response` to support multiple outputs 'n=' to enhance response versatility.
- **Refactor class hierarchy**: Move away from 'Thoughts' structure to a system of tasks and tasks_loops
- **Parallel Processing**: Implement parallel processing to handle multiple tasks simultaneously, improving performance and reducing task completion time.
- **DAG Structure for Task Management**: Introduce a Directed Acyclic Graph (DAG) structure to optimize decision-making efficiency in task management.
- **API Integrations**: Integrate additional AI models for improved capability and accuracy, along with the ability to search resources like Wikipedia and the web.


```
`ThoughtProcess`
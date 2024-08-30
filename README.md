```markdown

# The Thinker

## Objectives
The primary objective of this project is to create an intelligent system that can evaluate tasks iteratively using machine learning techniques, providing automated solutions based on user-defined instructions and available resources. It aims to enhance decision-making processes by leveraging AI capabilities.

- Automate Problem-Solving: To provide a system that can evaluate and generate solutions for various tasks without extensive manual intervention.
- Modular-Architecture: That can explore and evaluate a wide range of tasks using AI-based thought processing, with flexibility and adaptability.

## Current Limitations

- **Intelligence**: currently the program can alter and distort a files formatting or forget it entirely, occasionally making erratic decisions. Degrading usable output.
- **Cost Effectiveness**: The Program operates like a public works department with its allocated budget of iterations: spend it all!
- **Input Handling**: While the system manages structured tasks well, unexpected inputs can result in suboptimal or erratic outputs.
- **Lack of Parallel Processing**: The absence of parallel task management capabilities can hinder efficiency in completing tasks.

## Features
- **Iterative Task Evaluation**: The system decomposes user input tasks into individual components, allowing for progressive querying and processing.
- **Task pre-planning**: An executive reasoning layer formulates action plans based on provided tasks and relevant context files.

## Architecture
The project's architecture is designed with modularity in mind, allowing for the easy addition of new features and components. The key modules are structured as follows:

- **PersonaSystem**: Coordinates the overall workflow. It initializes the task driven process, evaluates tasks iteratively, manages logs, and saves outputs.
- **AiOrchestrator**: Represents an individual call to a LLM api, the current state of a task and provides methods for interacting with the AI model to generate responses.
    - **ChatGptWrapper**: Interfaces with the Chat Gpt API, sending requests and retrieving outputs based on specified prompts.


## Features to implement
To refine the system's architecture and enhance its capabilities and efficiency, several key features are intended for implementation:
- **Enhanced Executive Reasoning**: Advance the executive planning processes to enable more accurate and sophisticated decision-making that aligns closely with user needs.
- **Build from Blueprint**: Executor classes should follow clearly outlined blueprints, which will guide the construction of documents, ensuring internal consistency and coherence.
- **Coder**: Develop a defined persona for code files that emphasizes maintaining consistency while minimizing unnecessary commentary, fostering a cleaner code environment.- **Parallel Processing**: Implement parallel processing to handle multiple tasks simultaneously, improving performance and reducing task completion time.
- **Parallel Processing**: Introduce mechanisms for parallel processing to facilitate the simultaneous handling of multiple tasks, thereby enhancing overall performance and reducing time for task completion.
- **n-shot prompting**: Give the AI models examples of how it should answer roughly similar tasks.
- **DAG Structure for Task Management**: Introduce a Directed Acyclic Graph (DAG) framework to streamline decision-making efficiency, enabling better organization and oversight of tasks.
- **API Integrations**: Integrate additional AI models for improved capability and accuracy, along with the ability to search resources like Wikipedia and the web.


```
`UserInterface`
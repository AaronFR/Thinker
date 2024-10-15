# Performance Tests

## Initial testing

User Prompt:
Can we talk about the performance of these two files? AiOrchestrator and the api interface it uses ChatGptWrapper? When the application is run a query takes a lot of time and my suspicion is these classes are to blame

```commandline
Please enter your task (or type 'exit' to quit): Can we talk about the performance of these two files? AiOrchestrator and the api interface it uses ChatGptWrapper? When the application is run a query takes a lot of time and my suspicion is these classes are to blame
2024-09-13 11:25:55,545 [INFO] (EncyclopediaManagementInterface.py:59) Encyclopedia and redirects loaded successfully
2024-09-13 11:25:55,559 [WARNING] (Utility.py:52) Had to reformat a string into a list, this can lead to strings being decomposed into 
                            individual characters if not correctly handled
2024-09-13 11:25:56,026 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 109
2024-09-13 11:25:58,040 [INFO] (_client.py:1026) HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2024-09-13 11:25:58,048 [INFO] (ChatGptWrapper.py:120) Input tokens: 272, Input cost: $0.0000, Output tokens: 193, Output cost: $0.0001, Total cost: $0.0002
2024-09-13 11:25:58,048 [INFO] (AiOrchestrator.py:95) Function evaluated with response {'terms': [{'term': 'AiOrchestrator', 'content': 'A class responsible for coordinating AI tasks, executing queries, and managing interactions with underlying APIs. Might include methods for handling task scheduling, response processing, and error management.'}, {'term': 'ChatGptWrapper', 'content': 'An interface that abstracts the calls to the ChatGPT API, handling request formation, response parsing, and error handling. Responsible for managing API limits, retries, and formatting data for the application.'}, {'term': 'Performance Issues', 'content': 'Concerns regarding slow response times during query execution that could stem from inefficient code, long processing times, or network delays. Potential areas to investigate include API call limits, serialization overhead, and handling of asynchronous operations.'}, {'term': 'Query Execution Time', 'content': 'The duration it takes for a query to be processed, which can be affected by several factors like the efficiency of the classes involved, network latency, and the complexity of the data being processed.'}]}
2024-09-13 11:25:58,048 [INFO] (UserEncyclopediaManagement.py:73) Extracted terms for UserEncyclopedia: [{'term': 'AiOrchestrator', 'content': 'A class responsible for coordinating AI tasks, executing queries, and managing interactions with underlying APIs. Might include methods for handling task scheduling, response processing, and error management.'}, {'term': 'ChatGptWrapper', 'content': 'An interface that abstracts the calls to the ChatGPT API, handling request formation, response parsing, and error handling. Responsible for managing API limits, retries, and formatting data for the application.'}, {'term': 'Performance Issues', 'content': 'Concerns regarding slow response times during query execution that could stem from inefficient code, long processing times, or network delays. Potential areas to investigate include API call limits, serialization overhead, and handling of asynchronous operations.'}, {'term': 'Query Execution Time', 'content': 'The duration it takes for a query to be processed, which can be affected by several factors like the efficiency of the classes involved, network latency, and the complexity of the data being processed.'}]
2024-09-13 11:25:58,055 [INFO] (UserEncyclopediaManagement.py:116) Adding to UserEncyclopedia - aiorchestrator: A class responsible for coordinating AI tasks, executing queries, and managing interactions with underlying APIs. Might include methods for handling task scheduling, response processing, and error management.
2024-09-13 11:25:58,055 [INFO] (UserEncyclopediaManagement.py:116) Adding to UserEncyclopedia - chatgptwrapper: An interface that abstracts the calls to the ChatGPT API, handling request formation, response parsing, and error handling. Responsible for managing API limits, retries, and formatting data for the application.
2024-09-13 11:25:58,055 [INFO] (UserEncyclopediaManagement.py:116) Adding to UserEncyclopedia - performance issues: Concerns regarding slow response times during query execution that could stem from inefficient code, long processing times, or network delays. Potential areas to investigate include API call limits, serialization overhead, and handling of asynchronous operations.
2024-09-13 11:25:58,056 [INFO] (UserEncyclopediaManagement.py:116) Adding to UserEncyclopedia - query execution time: The duration it takes for a query to be processed, which can be affected by several factors like the efficiency of the classes involved, network latency, and the complexity of the data being processed.
2024-09-13 11:25:58,072 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 117
2024-09-13 11:26:01,208 [INFO] (_client.py:1026) HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2024-09-13 11:26:01,209 [INFO] (ChatGptWrapper.py:120) Input tokens: 199, Input cost: $0.0000, Output tokens: 5, Output cost: $0.0000, Total cost: $0.0000
2024-09-13 11:26:01,209 [INFO] (AiOrchestrator.py:95) Function evaluated with response {'selection': 'chat'}
2024-09-13 11:26:01,209 [INFO] (BasePersona.py:70) Selected workflow: chat
2024-09-13 11:26:01,209 [INFO] (BasePersona.py:92) Processing user messages: ['Can we talk about the performance of these two files? AiOrchestrator and the api interface it uses ChatGptWrapper? When the application is run a query takes a lot of time and my suspicion is these classes are to blame']
2024-09-13 11:26:01,210 [INFO] (FileManagement.py:61) Found the following files in Thought space: ['AiOrchestrator.py', 'ChatGptWrapper.py']
2024-09-13 11:26:01,210 [INFO] (FileManagement.py:84) Loading file_name content from: C:\Users\DELL\Documents\Programing\AI\Thinker\Data\..\thoughts\1\ChatGptWrapper.py
2024-09-13 11:26:01,226 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 1291
2024-09-13 11:26:04,665 [INFO] (_client.py:1026) HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2024-09-13 11:26:04,666 [INFO] (ChatGptWrapper.py:120) Input tokens: 1306, Input cost: $0.0002, Output tokens: 368, Output cost: $0.0002, Total cost: $0.0004
2024-09-13 11:26:04,666 [INFO] (AiOrchestrator.py:66) Executor Task Finished, with response: ...[ChatGptWrapper]
2024-09-13 11:26:04,666 [INFO] (FileManagement.py:140) File overwritten: C:\Users\DELL\Documents\Programing\AI\Thinker\Data\..\thoughts\1\ChatGptWrapper_summary.txt
2024-09-13 11:26:04,667 [INFO] (ExecutionLogs.py:21) Summariser: Summary for ChatGptWrapper.py written and saved as ChatGptWrapper_summary.txt
2024-09-13 11:26:04,667 [INFO] (FileManagement.py:84) Loading file_name content from: C:\Users\DELL\Documents\Programing\AI\Thinker\Data\..\thoughts\1\AiOrchestrator.py
2024-09-13 11:26:04,684 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 1535
2024-09-13 11:26:08,179 [INFO] (_client.py:1026) HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2024-09-13 11:26:08,180 [INFO] (ChatGptWrapper.py:120) Input tokens: 1550, Input cost: $0.0002, Output tokens: 396, Output cost: $0.0002, Total cost: $0.0005
2024-09-13 11:26:08,180 [INFO] (AiOrchestrator.py:66) Executor Task Finished, with response: ...[AiOrchestrator_summary]
2024-09-13 11:26:08,181 [INFO] (FileManagement.py:140) File overwritten: C:\Users\DELL\Documents\Programing\AI\Thinker\Data\..\thoughts\1\AiOrchestrator_summary.txt
2024-09-13 11:26:08,181 [INFO] (ExecutionLogs.py:21) Summariser: Summary for AiOrchestrator.py written and saved as AiOrchestrator_summary.txt
2024-09-13 11:26:08,182 [INFO] (FileManagement.py:61) Found the following files in Thought space: ['AiOrchestrator.py', 'AiOrchestrator_summary.txt', 'ChatGptWrapper.py', 'ChatGptWrapper_summary.txt']
2024-09-13 11:26:08,196 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 118
2024-09-13 11:26:08,836 [INFO] (_client.py:1026) HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2024-09-13 11:26:08,838 [INFO] (ChatGptWrapper.py:120) Input tokens: 256, Input cost: $0.0000, Output tokens: 16, Output cost: $0.0000, Total cost: $0.0000
2024-09-13 11:26:08,838 [INFO] (AiOrchestrator.py:95) Function evaluated with response {'files': ['AiOrchestrator.py', 'ChatGptWrapper.py']}
2024-09-13 11:26:08,838 [INFO] (Organising.py:38) Selected: ['AiOrchestrator.py', 'ChatGptWrapper.py'], 
from: ['AiOrchestrator.py', 'ChatGptWrapper.py']
2024-09-13 11:26:10,168 [INFO] (EncyclopediaManagementInterface.py:59) Encyclopedia and redirects loaded successfully
2024-09-13 11:26:10,184 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 102
2024-09-13 11:26:10,967 [INFO] (_client.py:1026) HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2024-09-13 11:26:10,968 [INFO] (ChatGptWrapper.py:120) Input tokens: 244, Input cost: $0.0000, Output tokens: 37, Output cost: $0.0000, Total cost: $0.0001
2024-09-13 11:26:10,968 [INFO] (AiOrchestrator.py:95) Function evaluated with response {'terms': [{'term': 'AiOrchestrator', 'specifics': 'performance analysis and optimization techniques'}, {'term': 'ChatGptWrapper', 'specifics': 'api efficiency and latency issues'}]}
2024-09-13 11:26:10,968 [INFO] (EncyclopediaManagementInterface.py:86) terms to search for in To Define: [{'term': 'AiOrchestrator', 'specifics': 'performance analysis and optimization techniques'}, {'term': 'ChatGptWrapper', 'specifics': 'api efficiency and latency issues'}]
2024-09-13 11:26:12,300 [INFO] (__init__.py:184) Wikipedia: language=en, user_agent: ThinkerBot (https://github.com/AaronFR/Thinker) (Wikipedia-API/0.7.1; https://github.com/martin-majlis/Wikipedia-API/), extract_format=ExtractFormat.WIKI
2024-09-13 11:26:12,300 [INFO] (__init__.py:523) Request URL: https://en.wikipedia.org/w/api.php?action=query&prop=info&titles=aiorchestrator&inprop=protection|talkid|watched|watchers|visitingwatchers|notificationtimestamp|subjectid|url|readable|preload|displaytitle
2024-09-13 11:26:12,995 [WARNING] (WikipediaApi.py:56) No page found for 'aiorchestrator'.
2024-09-13 11:26:14,290 [INFO] (EncyclopediaManagementInterface.py:59) Encyclopedia and redirects loaded successfully
2024-09-13 11:26:14,304 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 22
2024-09-13 11:26:15,327 [INFO] (_client.py:1026) HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2024-09-13 11:26:15,328 [INFO] (ChatGptWrapper.py:120) Input tokens: 37, Input cost: $0.0000, Output tokens: 32, Output cost: $0.0000, Total cost: $0.0000
2024-09-13 11:26:15,328 [INFO] (AiOrchestrator.py:66) Executor Task Finished, with response:
The AI Orchestrator focuses on techniques for performance analysis and optimization. It involves strategies to enhance system efficiency and effectiveness, ensuring optimal resource utilization and improved outcomes.
2024-09-13 11:26:16,644 [INFO] (__init__.py:184) Wikipedia: language=en, user_agent: ThinkerBot (https://github.com/AaronFR/Thinker) (Wikipedia-API/0.7.1; https://github.com/martin-majlis/Wikipedia-API/), extract_format=ExtractFormat.WIKI
2024-09-13 11:26:16,645 [INFO] (__init__.py:523) Request URL: https://en.wikipedia.org/w/api.php?action=query&prop=info&titles=chatgptwrapper&inprop=protection|talkid|watched|watchers|visitingwatchers|notificationtimestamp|subjectid|url|readable|preload|displaytitle
2024-09-13 11:26:16,947 [WARNING] (WikipediaApi.py:56) No page found for 'chatgptwrapper'.
2024-09-13 11:26:18,252 [INFO] (EncyclopediaManagementInterface.py:59) Encyclopedia and redirects loaded successfully
2024-09-13 11:26:18,267 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 22
2024-09-13 11:26:18,803 [INFO] (_client.py:1026) HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2024-09-13 11:26:18,804 [INFO] (ChatGptWrapper.py:120) Input tokens: 37, Input cost: $0.0000, Output tokens: 13, Output cost: $0.0000, Total cost: $0.0000
2024-09-13 11:26:18,804 [INFO] (AiOrchestrator.py:66) Executor Task Finished, with response:
ChatGPT wrapper has encountered issues related to API efficiency and latency.
2024-09-13 11:26:18,814 [INFO] (EncyclopediaManagementInterface.py:59) Encyclopedia and redirects loaded successfully
2024-09-13 11:26:18,828 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 109
2024-09-13 11:26:19,574 [INFO] (_client.py:1026) HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2024-09-13 11:26:19,575 [INFO] (ChatGptWrapper.py:120) Input tokens: 251, Input cost: $0.0000, Output tokens: 31, Output cost: $0.0000, Total cost: $0.0001
2024-09-13 11:26:19,575 [INFO] (AiOrchestrator.py:95) Function evaluated with response {'terms': [{'term': 'AiOrchestrator', 'specifics': 'performance issues'}, {'term': 'ChatGptWrapper', 'specifics': 'performance issues'}]}
2024-09-13 11:26:19,575 [INFO] (EncyclopediaManagementInterface.py:86) terms to search for in UserEncyclopedia: [{'term': 'AiOrchestrator', 'specifics': 'performance issues'}, {'term': 'ChatGptWrapper', 'specifics': 'performance issues'}]
2024-09-13 11:26:19,589 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 51
2024-09-13 11:26:20,423 [INFO] (_client.py:1026) HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2024-09-13 11:26:20,424 [INFO] (ChatGptWrapper.py:120) Input tokens: 66, Input cost: $0.0000, Output tokens: 47, Output cost: $0.0000, Total cost: $0.0000
2024-09-13 11:26:20,424 [INFO] (AiOrchestrator.py:66) Executor Task Finished, with response:
The aiorchestrator class is designed to coordinate AI tasks, execute queries, and manage interactions with APIs. It likely includes methods for task scheduling, processing responses, and managing errors. There are current performance issues associated with its functionality.
2024-09-13 11:26:20,439 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 56
2024-09-13 11:26:21,366 [INFO] (_client.py:1026) HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2024-09-13 11:26:21,367 [INFO] (ChatGptWrapper.py:120) Input tokens: 71, Input cost: $0.0000, Output tokens: 47, Output cost: $0.0000, Total cost: $0.0000
2024-09-13 11:26:21,367 [INFO] (AiOrchestrator.py:66) Executor Task Finished, with response:
The ChatGPT wrapper is designed to simplify interactions with the ChatGPT API by managing request creation, response interpretation, and error control. It ensures efficient handling of API limits, implements retry logic, and formats data for integration into the application.
2024-09-13 11:26:21,367 [INFO] (FileManagement.py:84) Loading file_name content from: C:\Users\DELL\Documents\Programing\AI\Thinker\Data\..\thoughts\1\AiOrchestrator.py
2024-09-13 11:26:21,368 [INFO] (FileManagement.py:84) Loading file_name content from: C:\Users\DELL\Documents\Programing\AI\Thinker\Data\..\thoughts\1\ChatGptWrapper.py
2024-09-13 11:26:21,373 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 3070
2024-09-13 11:26:28,333 [INFO] (_client.py:1026) HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2024-09-13 11:26:28,334 [INFO] (ChatGptWrapper.py:120) Input tokens: 3101, Input cost: $0.0005, Output tokens: 673, Output cost: $0.0004, Total cost: $0.0009
2024-09-13 11:26:28,334 [INFO] (AiOrchestrator.py:66) Executor Task Finished, with response: ...[Response]
2024-09-13 11:26:28,334 [INFO] (Coder.py:52) Iteration 0 completed with response: To analyze the performance of the `AiOrchestrator` and `ChatGptWrapper` classes, we need to focus on the interactions between these classes, their implementation details, and how they manage API calls. Here's a step-by-step breakdown:

### 1. **AiOrchestrator Class Overview**

The `AiOrchestrator` class serves as a controller that manages interactions with the `ChatGptWrapper`. 

#### Key Areas of Concern:
- **Message Generation**: This class generates messages that are sent to the API. If message construction takes time, it could introduce latency.
- **Retries on API Calls**: The class implements retries if the API does not return a valid response. This adds extra calls, which could contribute to overall time delays.
- **Error Handling & Logging**: Extensive logging and error handling could slow down execution, though they help in debugging.

### 2. **ChatGptWrapper Class Overview**

`ChatGptWrapper` interacts directly with the OpenAI API to fetch responses based on messages constructed by `AiOrchestrator`.

#### Key Areas of Concern:
- **OpenAI API Calls**: This class creates a new instance of the OpenAI client on each instantiation, which is unnecessary and may lead to overhead.
- **Response Handling**: The response handling section checks the response and expects `rerun_count` handling. If multiple calls are made sequentially, that will obviously add to the latency.
- **Error Handling**: Managing exceptions may delay the process slightly as it involves logging and potential retries.

### 3. **Identifying Performance Issues**

#### Potential Bottlenecks:
- **Redundant Client Instantiation**: The `ChatGptWrapper` should ideally be a singleton to minimize overhead associated with instantiating the client with each call.
- **Synchronous Calls**: The `execute` methods in `AiOrchestrator` handle API calls sequentially. Thus, any network latency directly impacts performance.
- **Retries and Reruns Logic**: Multiple reruns of requests if responses are not satisfactory can lead to increased wait times.

### 4. **Optimization Recommendations**

To improve the performance of these classes, consider the following:

1. **Singleton Pattern for ChatGptWrapper**: Implement a singleton pattern to avoid the creation of multiple instances of `ChatGptWrapper`. This can significantly reduce instantiation overhead.

2. **Asynchronous API Calls**: If possible, consider using asynchronous calls when requesting responses from the OpenAI API. This can prevent blocking and allow other processing to continue while waiting for API responses.

3. **Reduce Logging Level in Production**: Extensive logging, especially at the `debug` level, can slow down performance. Consider adjusting log levels based on the environment.

4. **Optimize Message Construction**: Review the logic in `generate_messages` and `build_role_messages`. Ensure that you are not processing unnecessary data or performing additional iterations.

5. **Adjust Retry Logic**: The retry logic can be improved to address specific transient issues without always rerunning calls, especially if a particular query is known to have performance issues.

By addressing these areas, you should be able to enhance the performance of both the `AiOrchestrator` and `ChatGptWrapper`, thereby potentially reducing the execution time for queries significantly.
Please enter your task (or type 'exit' to quit): 

```

Duration: 33 seconds
No singular time gaps.

### Time spent on ApiCalls

2024-09-13 11:25:56,026 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 109
2024-09-13 11:25:58,040 [INFO]
2 seconds
2024-09-13 11:25:58,072 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 117
2024-09-13 11:26:01,208 [INFO]
3.2 seconds
2024-09-13 11:26:01,226 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 1291
2024-09-13 11:26:04,665 [INFO]
3.4 seconds
2024-09-13 11:26:04,684 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 1535
2024-09-13 11:26:08,179 [INFO]
3.5 seconds
2024-09-13 11:26:08,196 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 118
2024-09-13 11:26:08,836 [INFO]
0.6 seconds
2024-09-13 11:26:10,184 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 102
2024-09-13 11:26:10,967 [INFO]
0.8 seconds
2024-09-13 11:26:14,304 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 22
2024-09-13 11:26:15,327 [INFO]
1 second
2024-09-13 11:26:18,267 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 22
2024-09-13 11:26:18,803 [INFO]
0.6 seconds
2024-09-13 11:26:18,828 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 109
2024-09-13 11:26:19,574 [INFO]
0.7 seconds
2024-09-13 11:26:19,589 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 51
2024-09-13 11:26:20,423 [INFO]
0.9 seconds
2024-09-13 11:26:20,439 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 56
2024-09-13 11:26:21,366 [INFO]
0.9 seconds
2024-09-13 11:26:21,373 [INFO] (AiOrchestrator.py:111) Tokens used (limit 128k): 3070
2024-09-13 11:26:28,333 [INFO]
7 seconds
Total: 24.6 seconds, 75% of runtime

2 calls to wikipedia api taking ~0.3 seconds approx

## Next User Prompt

Okay lets rewrite ChatGpt as a singleton then, for the other options I'm afraid there just not options, this isn't production and we don't want to get rid of logging

### Rerunning the first user prompt

2024-09-13 12:08:56,424
2024-09-13 12:09:31,064
35 seconds.

Instantiating the ChatGptApi wasn't the issue.

2024-09-13 12:55:30,539
2024-09-13 12:55:39,640
9 seconds with Encyclopedia system disabled

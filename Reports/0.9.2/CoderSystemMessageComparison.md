# Coder System Message Study

Now that the Coder - Auto Workflow has been implemented it's a great time to start automated testing. 
And squeeze in some code refactoring at the same time.

Model: gpt-4o-mini
User Prompt: "Improve this file"

Methodology: Using the coder auto workflow, the user prompt is applied individually against each reference file, see the CSV for the records.

## Set 1

Flawed. The ai can be confused and output results for other files it had previously worked on and not the one it was *supposed*
to be instructed to work on.


## Set 2 - Base System Messages

```
Following the following guidelines when writing code. Docstrings and class definitions style: reStructuredText
indentation: 4_spaces (or typical for the language)|

max line length: 120
```

## Set 3 - Enhanced System Messages

The enhanced prompt is adjusted to tell get the llm to adopt the persona of a skilled coder and to adjust itself based on the users
(assumed) skill level.

## Comparison Base v Enhanced

### Sets 2 v 3 - /Data/Files

| File                  | Base System Messages                                                                                                           | Enhanced System Messages                                                                                                                                     |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| StorageMethodology.py | ✔ Good. Deletes comments but actually resolves them. Improves log functionality                                                | Similarly resolves the comment but doesn't improve the logs                                                                                                  |
| StorageBase.py        | Adds documentation and return types                                                                                            | Likewise, simple task                                                                                                                                        |
| S3Manager.py          | Corrects documentation, adds constants, adds helper methods, deleted unused methods (not a fan)                                | ✔ Likewise, Chooses to use init arguments to simplify env calls. (Like set 2 prevents overwriting, this should probably be changed), implemented try-catches |
| FileManagement.py     | ✔ Adds helpful (and not so helpful) helper methods, comment deleted without addressing (read_file), documentation improvements | Just documentation improvements                                                                                                                              |

(For future tests I will annotate the outputs in the test reference files, its difficult to keep track of changes to an entire file in a single table box)

No clear winner, its a very small sample but this already indicates theres no strong difference between the pair of system messages.
There could be an issue where the Enhanced system prompt is supposed to adapt the response based on the users skill level.
Given how simple the input prompt is, it could be adjusting the output to be quite simple for an assumed novice user.
In the next set we'll remove any mention of adapting for the skill of the user

### Sets 4 v 5 - /Data

Set 4 is the 'enhanced' system message. The implementation is different. Notes are made in the respective set
First Set 4 was applied and beneficial changes applied. Then set 5 was applied over these changes.
In the next set this order should be reversed for fairness in testing


| File                            | Enhanced | Base | Reasoning                                                                                                                |
|---------------------------------|----------|------|--------------------------------------------------------------------------------------------------------------------------|
| WikipediaApi.py                 | ✔        | ❌    | By and large bases changes were just uninteresting                                                                       |
| UserContextManagement.py        | ✔        | ✔    |                                                                                                                          |
| Pricing.py                      | 0        | ✔    | Close. But base added a value error while enhanced just added a useful log                                               |
| NodeDatabaseManagement.py       | ❌        | ✔    | Base suggested try catches for all methods. Enhanced deleted methods                                                     |
| Neo4jDriver.py                  | ✔        | ✔    | Base noticed running optional field should be inside a if statement, enhanced added a good value error to initialisation |
| EncyclopediaManagementInterface | ❌        | ✔    | Enhanced broke the file.                                                                                                 |
| CypherQueries.py                | ❌        | ✔    | The base didn't delete necessary constants and pointed out more useful refactorings                                      |
| Configuration.py                | ❌        | ✔    | Enhanced, mal-forms the function, while base adds a useful try-catch                                                     |
| CategoryManagement.py           | ✔        | ✔    | Both suggested valuable improvements will also missing details the other picked up                                       |

There's a possible defect in that the base testing set was interrupted due to introduced errors and was split in two runs of the auto workflow
3 / 7 rather than 10 files at once. So possibly the Enhanced value suffered under the weight of a larger message history confusing it.

However, even then the lengthy 'Enhanced' system prompt produced 4 malformed files against the base system messages 1,
and half as many useful outputs.

I'll run the test in reverse with the base and then Enhanced test. But I think this easily goes to demonstrate that system prompts should be
**short and to the point**

And why the 'Enhanced' system messages aren't very popular...

### Sets 6 v 7 - Workflows

Welp that sucked. There was very little value provided which to be fair makes sense based on the types of files the workflows 
we're by and large, however while sharing memory could lead to consistency it can also lead to dislikeable ideas being brought up frequently.
Set 6 cost approximately 98 cents, and I'm not too inclinded to try and see if a second set can improve on that

### Sets 8 v 9 (Demo test set 7)

Base system prompts where run on gpt-4o-mini (set 7), to ensure that the auto workflow was working and not throwing away outputs.
Note the intention is not to compare set 7 against 8 or 9 but to use it as a benchmark. Now that the files are updated there should be less obvious useful changes. Making the job of a good system prompt with a bad user prompt more significant.
If the base system messages struggle while running on the new model and the updated files it just means it's much harder.
It is set 8 v 9 that are to be compared against one another. 

| File                  | Base gpt-4o-mini | Base o1-mini | 'enhanced' o1-mini Reasoning |
|-----------------------|------------------|--------------|------------------------------|
| FileItem.js           | ✔                | ✔            | womp                         |
| FilePane.js           | ✔                | ✔            |                              |
| FileUploadButton.js   | 0                | ✔            |                              |
| MessageItem.js        | ✔                | 0            |                              |
| MessagePane.js        | ✔                | ❌            |                              |
| Navigation.js         | ✔                | ✔            |                              |
| OutputSection.js      | ✔                | 0            |                              |
| PersonaSelector.js    | ✔                | ❌            |                              |
| PromptAugmentation.js | ✔                | 0            |                              |
| SuggestedQuestions.js | ✔                | ❌            |                              |
| TagsManager.js        | ✔                | ✔            |                              |
| TransactionForm.js    | ✔                | ✔            |                              |
| UserInputForm.js.js   | 0                | ❌            |                              |
| Workflow.js           | ✔                | 0            |                              |

Tragically (for my wallet) There was a failure in categorisation *somewhere* in set 9. The results we're generated but not saved to a category. Despite a category being assigned to eval9.
This error is un-reproducible. While I would like to start testing system prompts: I'll probably still try it also goes to show that tests of the workflow at scale need to be perfomed and stability improved. 
Ontop of that the slow pace of set 9 revealed a urgent change that must occur to how workflows are processed: Workflow recent history fills up far too quickly.
(actually thinking about the sheer scale of the text being fed in, its not implausible that the error is uniquely caused by said strain on the system)

Given this, set 8 (Base o1-mini) is really more an indication of how the o1-mini model operates when asked (poorly) to improve a file that has already been refined, making the task harder, **while** being subjected to an incredible amount of unnecessary information in its role messages.
Whats good can be really good, but success rates *halve* under these conditions for the same system prompt.

Here are the role messages for the step improving Tags Manager, 2 steps before the end:

### Over-abundance of role messages

22 role messages
- 1: System role message
- 2: System coder message
- 3: Assistant Improve Navigation.js
- 4: Assistant: Improve OutputSection.js
- 5: Assistant: Improve PersonaSelector.js
- 6: Assistant Improve Prompt Augmentation.js
- 7: Assistant Improve SuggestedQuestions.js
- 8: User OpenAi Flagged Your Prompt as Inappropriate (lol)
- 9: User Lets analyse FilePane.js
- 10: User Lets analyse FileUploadButton.js
- 11: User Lets analyse MessageItem.js
- 12: User Lets analyse MessagePane.js
- 13: User Lets analyse Navigation.js *
- 14: User Lets analyse OutputSection.js
- 15: User Lets analyse PersonaSelector.js
- 16: User Lets analyse PromptAugmentation.js
- 17: User Lets analyse SuggestedQuestions.js
- 18: User File [TagsManager]
- 19: User File [TransactionForm]
- 20: User File [FileUploadButton]
- 21: User File [Workflow.css]
- 22: User Improve this file. Specifically focus on TagsManager.js

This represents a huuuuuuge over-sharing of information. We can see a few blocks
- 1-2 System
- 3-7 Assistant history (user prompt : response) [capped at 5]
- 8-17 LLM responses (response - note the duplication)
- 18-21 Reference files
- 22: Actual user input prompt (modified0

This should be massively cut down by default
- 1-2 ✅
- 3-7 (this could be cut down, really only none are needed for the prompt, but its working as intended)
- 8-17 (this is the *entire* workflow, this would be fine for certain requests, requiring full oversight and knowledge of what the ai itself did, but not by default)
What's additionally interesting is the duplication. Really this category should exist, its superfluous.
- 18-21 (Fine as an option but not by default, should only be the actual file its working on by default)
- 22 ✅

#### Role message log 
(abbreviated because I remember seeing how hard it is to have to remove large data files for git history, and it is *not* easy)

```
2025-01-04 21:28:26,458 [DEBUG] (_base_client.py:448) Request options: {'method': 'post', 'url': '/chat/completions', 'files': None, 'json_data': {'messages': [
{'role': 'user', 'content': 'Analyze the user prompt in sequential order, giving priority to the most recent instructions provided by the user, to ensure accuracy in processing their requirements.'},
{'role': 'user', 'content': " 'You are The Thinker, a world class Programming AI assistant\n    designed to help users with programming topics and tasks.\n\nWhen solving a users problem:\n\n 1. **Th...
{'role': 'assistant', 'content': 'Improve this file\n\nSpecifically focus on Navigation.js: Certainly! Let\'s analyze and enhance your `Navigation.js` component step by step, ensuring it adheres to ...
{'role': 'assistant', 'content': 'Improve this file\n\nSpecifically focus on OutputSection.js: Certainly! Let\'s analyze and improve your `OutputSection.js` component step by step, ensuring it adher...
{'role': 'assistant', 'content': 'Improve this file\n\nSpecifically focus on PersonaSelector.js: Certainly! Let\'s analyze and enhance your `PersonaSelector.js` component step by step, ensuring it a...
{'role': 'assistant', 'content': 'Improve this file\n\nSpecifically focus on PromptAugmentation.js: Certainly! Let\'s analyze and enhance your `PromptAugmentation.js` component step by step, ensurin...
{'role': 'assistant', 'content': 'Improve this file\n\nSpecifically focus on SuggestedQuestions.js: Certainly! Let\'s analyze and enhance your `SuggestedQuestions.js` component step by step, ensurin...
{'role': 'user', 'content': 'OpenAi ChatGpt Server Flagged Your Request as Inappropriate. Try again, it does this alot.\n        \n        '},
{'role': 'user', 'content': 'Certainly! Let\'s analyze and improve the `FilePane.js` component step by step, adhering to best practices and the guidelines provided.\n\n## **1. Analysis of Current `F...
{'role': 'user', 'content': 'Certainly! Let\'s analyze and improve the `FileUploadButton.js` component step by step, adhering to best practices and the guidelines provided.\n\n## **1. Analysis of Cu...
{'role': 'user', 'content': 'Certainly! Let\'s analyze and improve the `MessageItem.js` component step by step, adhering to best practices and the provided guidelines.\n\n## **1. Analysis of Current...
{'role': 'user', 'content': "Certainly! I'd be happy to help improve your `MessagePane.js` component. However, I don't have the current implementation of `MessagePane.js` to review and enhance. Coul...
{'role': 'user', 'content': 'Certainly! Let\'s analyze and enhance your `Navigation.js` component step by step, ensuring it adheres to best practices, improves functionality, and enhances maintainab...
{'role': 'user', 'content': 'Certainly! Let\'s analyze and improve your `OutputSection.js` component step by step, ensuring it adheres to best practices, enhances functionality, and improves maintai...
{'role': 'user', 'content': 'Certainly! Let\'s analyze and enhance your `PersonaSelector.js` component step by step, ensuring it adheres to best practices, improves functionality, and enhances maint...
{'role': 'user', 'content': 'Certainly! Let\'s analyze and enhance your `PromptAugmentation.js` component step by step, ensuring it adheres to best practices, enhances functionality, and improves ma...
{'role': 'user', 'content': 'Certainly! Let\'s analyze and enhance your `SuggestedQuestions.js` component step by step, ensuring it adheres to best practices, improves functionality, and enhances ma...
{'role': 'user', 'content': 'import React, { useState, useRef, useEffect } from \'react\';\r\nimport PropTypes from \'prop-types\';\r\nimport \'./styles/TagsManager.css\';\r\n\r\n/**\r\n * Default t...
{'role': 'user', 'content': 'import React, { useState } from \'react\';\r\nimport { apiFetch } from \'../utils/authUtils\';\r\n\r\nconst FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL ||...
{'role': 'user', 'content': 'import React, { useState, useEffect } from \'react\';\r\nimport PropTypes from \'prop-types\';\r\n\r\nimport FileUploadButton from \'./FileUploadButton\';\r\nimport Tags...
{'role': 'user', 'content': 'import React from "react";\r\n\r\nimport ExpandableElement from "../utils/expandableElement";\r\n\r\nimport \'./styles/Workflow.css\'\r\n\r\n/**\r\n * Workflow Component...
{'role': 'user', 'content': 'Improve this file\n\nSpecifically focus on TagsManager.js'}], 'model': 'o1-mini', 'n': 1}}

```

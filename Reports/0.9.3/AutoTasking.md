# Auto Tasks

So we're given up the pretension of running something vaguely within the orbit of an actual scientific test with measurable results for this report
and default to simple logging and note taking.

What I want to observe is how well the application takes to attempting individual software tasks/tickets.
I also want to see the utility of the Auto workflow for large numbers of files. Put my claim that it can run 'arbitrarily' many operations to the test.

To these ends I have included 20+ files in an auto workflow operation, each one pre-pended with a task, covering almost all existent planned features in the README.
I want to see where it fails, and it will fail, almost certainly, but where and why are useful to know for optimising the application.
For improving its ability to solve any given problem given to it.
Currently we know it struggles with complexity and most of these features (bar a few) are rather complex, but how can we reduce and ease this complexity?

If it can successfully implement even 20% of the pages included that's ~4 features. That's almost an entire update right there.

| file                                         | 1 - Review Task | 2 - Attempt task |
|----------------------------------------------|-----------------|------------------|
| AiOrchestrator_RerunLogic.py                 | ❌               |                  |
| Augmentation_AutoSelectPersona.py            | ❎               |                  |
| Augmentation_AutoSelectWorkflow.py           | ❎               |                  |
| AutoWorkflow_BossPersonaAttempt.py           | ✔               |                  |
| AutoWorkflow_loopWorkflow.py                 | ✔               |                  |
| AutoWorkflow_ParallelProcessing.py           | ✔               |                  |
| CategoryManagement_AutomaticColourisation.py | ✔               |                  |
| CategoryManagement_categoryDescription.py    | ✔               |                  |
| ChatGptWrapper_RemoveReceipts.py             | ✔               |                  |
| InternetSearch.py                            | ✔               |                  |
| Messages_rewrite.js                          | ✔               |                  |
| Messages.js                                  | ❎               |                  |
| NodeDatabaseManagement_EditGetCategory.py    | ✔               |                  |
| process_message_ws_modularWorkflows.py       | ✔               |                  |
| S3Manager_ManageFileRevisions.py             | ✔               |                  |
| SugestedQuestions_MobileFriendly.js          | ❎               |                  |
| UserContextManagement_ExistingContext.py     | ✔               |                  |
| UserContextManagement_NodeDescription.py     | ✔               |                  |
| UserInputForm_Deselect.js                    | ✔               |                  |
| WriteWorkflow_AddGithubIntegration.py        | ✔               |                  |
| WriteWorkflow_CompileCheck.py                | -               |                  |
| WriteWorkflow_ModularWorkflows.py            | 🆗              |                  |
| WriteWorkflow_PhysicsMathIntegration.py      | 🆗              |                  |
| Writing_ExtensionCheck.py                    | ✔               |                  |


### 1 - Review Task

First stage is running auto on gpt-4o-mini and asking it if it thinks the task is possible, if it can improved and clarified,
and if any superfluous information can be removed.
The real purpose of this step is just to ensure that auto can execute a large payload of files without imploding in on top of itself
when running an actually expensive model.

Which it can.

| file                                         | Review                                                                                                                                                                                     |
|----------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| AiOrchestrator_RerunLogic.py                 | ❌ Not a useful response. First created answer. Again points to the idea that sequential history context helps clue it in.                                                                  |
| Augmentation_AutoSelectPersona.py            | ❎ Ditto, it's not familiar with the idea of using custom code to talk to a llm even if told to write such.                                                                                 |
| Augmentation_AutoSelectWorkflow.py           | ❎ Wrong but lays the solution for a correct solution                                                                                                                                       |
| AutoWorkflow_BossPersonaAttempt.py           | ✔ A basic layout and yes, a misunderstanding of the requirements. But it can be built upon                                                                                                 |
| AutoWorkflow_loopWorkflow.py                 | ✔ This might be just straight up solved, really consistent solution                                                                                                                        |
| AutoWorkflow_ParrallelProcessing.py          | ✔ Stripped the iteration from parallel processing. This makes sense without context, but is required to ensure the frontend workflow displays                                              |
| CategoryManagement_AutomaticColourisation.py | ✔ I think this is also an example of the benefit of sequential calls, the llm already had a version of categoryManagement.py in its history even though this wasn't supplied in the prompt |
| CategoryManagement_categoryDescription.py    | ✔ I suppose a lot of these are just easier than I imagined.                                                                                                                                |
| ChatGptWrapper_RemoveReceipts.py             | ✔ Needed to update, as the solution it gave wasn't exactly what I was thinking. Could have explained myself clearer                                                                        |
| InternetSearch.py                            | ✔                                                                                                                                                                                          |
| Messages_rewrite.js                          | ✔ Ahhhh, that was easier than I thought it was                                                                                                                                             |
| Messages.js                                  | ❎ Only did messages, but understandable given how much content is present. <br/>Have refactored to make borrowing from app.js component more obvious                                       |
| NodeDatabaseManagement_EditGetCategory.py    | ✔ This is an embarassement of riches                                                                                                                                                       |
| process_message_ws_modularWorkflows.py       | ✔ Perfectly plausible solution.                                                                                                                                                            |
| S3Manager_ManageFileRevisions.py             | ✔ Perfectly plausible solution.                                                                                                                                                            |
| SugestedQuestions_MobileFriendly.js          | ❎ Our first misunderstanding (finally). I've expanded on the task description to make it less ambigous                                                                                     |
| UserContextManagement_ExistingContext.py     | ✔ Perfectly plausible solution.                                                                                                                                                            |
| UserContextManagement_NodeDescription.py     | ✔ Perfectly plausible solution. Needs re-writing to integrate with the application, but that's expected                                                                                    |
| UserInputForm_Deselect.js                    | ✔ I might have overestimated how hard this task was                                                                                                                                        |
| WriteWorkflow_AddGithubIntegration.py        | ✔ This is a pretty plausible solution. I would still like o1-mini to attempt the task though                                                                                               |
| WriteWorkflow_CompileCheck.py                | a solution, but I don't like having to save the file to check it compiles                                                                                                                  |
| WriteWorkflow_ModularWorkflows.py            | 🆗 Actually tried to attempt the solution, not surprising, 4o-mini gets confused easily, but still might be useful                                                                         |
| WriteWorkflow_PhysicsMathIntegration.py      | 🆗 A plausible *format* for a solution but the methods aren't filled out.                                                                                                                  |
| Writing_ExtensionCheck.py                    | ✔  Plausibly this has been solved in the review task stage, an easy task though so not surprising                                                                                          |

So this did *surprisingly* well, I expected the expensive models like o1-mini to be confused and just produce garbage. But the vast majority of content output is useful *to some degree*.
It *did* fail at actually analysing the task itself on a meta level and suggesting improvements to the task file without doing the task itself.
But its been said before:

The words "Do NOT actually try and answer this task" contain the words " try and answer this task"

### 2 - Attempt Task

Completed @16:36 2025/01/13
Cost: $4.93 (Well the good news is that the openAi billing and your own estimates match almost exactly)

That's very high cost, I anticipated 2-3 euro. The previous large workflow cost about this but ran for only 11 files. 
ToDo: Check the logs to ensure tokens aren't being wasted somewhere.
(in typical fashion the o1-responses are twice as long, which explains why they cost 30 x 2 times more than than the gpt-4-mini responses)
(also in the last response with the issue with ALL file references being sent to each individual step, input costs where 1.5x times higher than output costs, 
here they're 0.9x)

Now lets see what I got for my money.

| file                                         | Review                                                                                                                                                                                                                                                            |
|----------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| AiOrchestrator_RerunLogic.py                 |                                                                                                                                                                                                                                                                   |
| Augmentation_AutoSelectPersona.py            |                                                                                                                                                                                                                                                                   |
| Augmentation_AutoSelectWorkflow.py           |                                                                                                                                                                                                                                                                   |
| AutoWorkflow_BossPersonaAttempt.py           |                                                                                                                                                                                                                                                                   |
| AutoWorkflow_loopWorkflow.py                 |                                                                                                                                                                                                                                                                   |
| AutoWorkflow_ParallelProcessing.py          |                                                                                                                                                                                                                                                                   |
| CategoryManagement_AutomaticColourisation.py |                                                                                                                                                                                                                                                                   |
| CategoryManagement_categoryDescription.py    |                                                                                                                                                                                                                                                                   |
| ChatGptWrapper_RemoveReceipts.py             |                                                                                                                                                                                                                                                                   |
| InternetSearch.py                            |                                                                                                                                                                                                                                                                   |
| Messages_rewrite.js                          |                                                                                                                                                                                                                                                                   |
| Messages.js                                  |                                                                                                                                                                                                                                                                   |
| NodeDatabaseManagement_EditGetCategory.py    |                                                                                                                                                                                                                                                                   |
| process_message_ws_modularWorkflows.py       |                                                                                                                                                                                                                                                                   |
| S3Manager_ManageFileRevisions.py             |                                                                                                                                                                                                                                                                   |
| SugestedQuestions_MobileFriendly.js          |                                                                                                                                                                                                                                                                   |
| UserContextManagement_ExistingContext.py     |                                                                                                                                                                                                                                                                   |
| UserContextManagement_NodeDescription.py     |                                                                                                                                                                                                                                                                   |
| UserInputForm_Deselect.js                    |                                                                                                                                                                                                                                                                   |
| WriteWorkflow_AddGithubIntegration.py        |                                                                                                                                                                                                                                                                   |
| WriteWorkflow_CompileCheck.py                |                                                                                                                                                                                                                                                                   |
| WriteWorkflow_ModularWorkflows.py            |                                                                                                                                                                                                                                                                   |
| WriteWorkflow_PhysicsMathIntegration.py      |                                                                                                                                                                                                                                                                   |
| Writing_ExtensionCheck.py                    | ✅ Works with some modification. Also suggests changes to the rest of the code. In future, the real part of this<br/> will be to somehow split out the exact code that's actually needed with cheap LLM's and feed the key, minimised info in for an expensive LLM |

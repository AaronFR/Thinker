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
| Configuration.py                | ❌        | ✔    | Enhanced, mal-forms the function, while base adds a useful try-catch                                                      |
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

### Sets 7 v 8

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
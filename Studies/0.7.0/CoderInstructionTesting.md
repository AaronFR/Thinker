# Testing

Coder currently uses 5 stages in its primary write workflow:
```Python
analyser_messages = [
    f"As part of <user prompt>{initial_message}</user prompt> "
    f"Examine the current implementation of {file_name} and your answer for any logical inconsistencies or "
    "flaws. Identify specific areas where the logic might fail or where the implementation does not meet "
    "the requirements. Provide a revised version addressing these issues with respect to the following: "
    f"{purpose}",
    f"Evaluate the current implementation of {file_name} for opportunities to enhance features, improve naming "
    "conventions, and increase documentation clarity. Assess readability and flexibility. "
    "Provide a revised version that incorporates these improvements.",
    f"Review the structure and flow of the documentation in {file_name}. "
    "Suggest and implement changes to improve the organization, clarity, and ease of understanding of the code "
    "and its documentation. Provide a new and improved version of the code with its improved documentation.",
    f"Assess the code in {file_name} for adherence to coding standards and best practices. "
    "Suggest changes to improve code quality.",
    f"Present the final revised version of the code in {file_name}, "
    "incorporating all previous improvements we discussed. "
    "Additionally, provide a summary of the key changes made, explaining how each change enhances the code."
]
```

This can be understood as the following stages:
1. Identify Logical Issues: Examine the current implementation for logical inconsistencies or failures, and suggest revisions.
2. Enhance Features & Clarity: Evaluate opportunities to improve features, naming conventions, and documentation clarity, then revise accordingly.
3. Improve Documentation & Structure: Review and enhance the organization, clarity, and flow of the code and its documentation.
4. Adhere to Best Practices: Assess compliance with coding standards and recommend changes to improve code quality.
5. Final Review & Summary: Present the final, revised code version and summarize key changes and their benefits. (currently not provided to user)


Documentation clarity comes up way too often for something which might actually be optional to the user
Simultaneously there's isn't enough proper 'chain of thought reasoning', limitations and facts are not discussed.

```Python
analyser_messages = [
    f"In {file_name}, "
    "identify syntax, style, or logic errors. Provide an overview of any failing tests or warnings. "
    "Rewrite the file with this overview in mind",
    
    f"Analyze the code in {file_name}"
    f"Focus on logic that could break or deviate from the user requirements in {purpose}. Provide a revised version addressing these issues.",
    
    f"Evaluate the code in {file_name} for opportunities to optimize features and improve performance. "
    "Identify areas for refactoring or using better algorithms to enhance efficiency and resource usage. "
    "Provide a revised version with performance optimizations.",
    
    f"Assess the code in {file_name} for adherence to coding standards, readability and best practices. "
    "Suggest improvements to naming conventions, structure, and style."
    "Ensure documentation is sufficient and helpful."
    "Provide a revised version that follows best coding practices.",
    
    # Maybe later
    f"Develop or update unit and integration tests for {file_name}. "
    "Ensure that new features or changes are well-covered by tests and that existing functionality is not broken. "
    "Provide the revised code with an updated test suite.",
    
    f"Consolidate all improvements and perform a final review of {file_name}, "
    "ensuring that all logical, feature, readability, and standards issues have been addressed. "
    "Summarize the key changes and explain how each modification improves the code.",
]
```

We want to see how these workflow performs on a variety of tasks
1. Implement a merge sort algorithm method
2. Create a file reader, that converts everything to upper case and then saves it
3. Create a Prime Number Checker
4. Create a ToDo List CLI app
5. Create snake game in a form the player can play right away
6. Create a chatbot that can remember user interactions during a session and refer back to them (e.g., remembering names, preferences)
7. Create a text-based dungeon explorer game where an AI-controlled character navigates a maze, makes decisions (e.g., fight, flee), and learns from previous encounters.

| Test               | ChatGpt 4o Mini | ChatGpt 4o | ChatGpt o1-preview | Thinker Original Coder workflow | Thinker w/ New Workflow | Thinker streamlined |
|:-------------------|:---------------:|:----------:|:------------------:|--------------------------------:|------------------------:|--------------------:|
| Merge sort         |      9/10       |    9/10    |       10/10        |                            9/10 |                    8/10 |               10/10 |
| File reading       |      9/10       |    9/10    |       10/10        |                            6/10 |                    9/10 |                9/10 |
| Prime Checker      |      9/10       |    9/10    |        6/10        |                           10/10 |                   10/10 |                8/10 |
| ToDo CLI           |      9/10       |    8/10    |        8/10        |                          10/10* |                    6/10 |                8/10 |
| Snake              |      9/10       |    4/10    |        8/10        |                           10/10 |                   10/10 |                9/10 |
| Chatbot w/ Memory  |      6*/10      |    5/10    |        5/10        |                            3/10 |                    6/10 |                4/10 |
| Text based dungeon |      9/10       |    8/10    |        6/10        |                            5/10 |                    6/10 |        6/10 -> 8/10 |

#### Totals
ChatGpt 4o Mini     : 60 / 70

ChatGpt 4o          : 54 / 70

ChatGpt o1-preview  : 53 / 70

Thinker Original    : 57 / 70

Thinker new         : 55 / 70

Thinker streamlined : 57 / 70


### Thinker streamlined
Merge sort: Gives examples and the code is readable. And it actually wrote a decent, fully explained README
File Reading: Like the others, specify 'input.txt' will write to 'output.txt'
Prime Checker: Doesn't requery the user for prime numbers
ToDo CLI : Uses the enter number for method option like o1 which I am not a huge fan of. Does have a neat README though
Snake: Solid entry, handles well (maybe?) and still has the 180 turn allowed at size 2 'bug'. +README
Chatbot w/ Memory: Really badly flawed, can't give preferences as the set preferences command is first, I suppose it doesn't lie
and pretend its listening, also not clear: you need to read the code in order to understand how to use the chatbot, but 
that's kind of the idea of old chatbots when it was smoke and mirrors.
Text based dungeon: offers multiple options which is actually like a game, fails the AI player part in fact the game breaks
because Thinker doesn't know / doesn't know how to make multiple python files link together
-> With some modification Thinker is (nearly) able to link files together, the game is a bit simple also not AI controlled,
but you can explore, and it forms a decent foundation for more content

Notes: Much quicker, plus READMEs 

## Commentary
### ChatGpt 4o Mini
Merge sort: Fine
File Reading: Fine
Prime Checker: Fine, only one example given but that's fine.
ToDo CLI : using numbers to control the application instead of text is a little but less natural, but fine.
Snake: Works completely fine, there is an issue where the snake can turn 180 degrees below 2 but not 1 length.
Chatbot w/ Memory: Sardonically the best entry, just asks the user their name and their favourite colour then just pretends
its listening as the user continues. Hilariously on point.
Text based dungeon: The best entry, funny: You can negotiate with the dragon and theres more specific loot than just 'Treasure'
Really limited by the fact there's only 3 rooms and the programs ends quickly but a solid starting point

Overall suspiciously good for the smaller model (These tests where run AFTER 4o's)


### ChatGpt 4o
Merge sort: Completely satisfactory, works on testing.
File Reading: ..
Prime Checker: ..
ToDo CLI : Good error checking, gives option to remove a task even if no tasks exist which is understandable. 
(stil handling for invalid choice there)
Snake: Every button pressed causes snake to eat itself instantly
Chatbot w/ Memory: A surprisingly decent attempt, but the actual code to recall favorites doesn't work 
(because both terms contain the term 'like' or 'preference' which is first in the logic)
Text based dungeon: First run hilariously flee'd from every single enemy for 25 rooms. Counter for rooms, events,
experience doesn't do anything but a good starting off point.

### ChatGpt o1-preview
Merge sort: Best answer, gives lots of examples and is arguably the easiest program to read
File Reading: Easily the best answer, being the only one to give the option to overwrite the input file, to choose which file
to read and write, to offer optional changes to make the program work with CLI inputs. 
Maybe a bit wordy for a simple question perhaps
Prime Checker: VERY CONFLICTING, on one hand it listed an actual algorithm by name, on the other it didn't actually answer
the user request, its a prime generator not a prime checker
ToDo CLI : Very conflicted, works directly by executing the file from the CLI along with a command which is certainly
the most 'CLI' todo app given but also the most unwieldy and hard to use.
Snake: Really different to the others, starts at size 5 and has warp walls, BUT it has no score, no game over window, and
while harder to break than the others you can cause a 180 turn by hitting two inputs at once.
Chatbot w/ Memory: A neat trick in that it changes the user input header to the given name, but it's the same trick as mini
No memory at all
Text based dungeon: Ahhh hard to say, functionally it outputs a map each turn which is something but looks terrible on console,
still it's a good base? I'm rating low though as it

Strong theme of better or at least more complicated technical solutions at the expense of user value

### Thinker Original Coder workflow
Merge sort: Completely satisfactory, works on testing. But with documentation, but no points because it tries to separately define a type?
File Reading: Works, but redundantly saved the information to 'output.txt' probably because it thought that file was "important"
Prime Checker: Works and provides more examples
ToDo CLI : Excellent, lists options, but it uses emojis to highlight incomplete and complete tasks, and also has genres and priorities.
AND it saved the tasks to memory! (Did create a needless, malformed readme file)
Snake: Game actually works as a java script based html page, Complete with colour, working restart button and you can
actually eat your own tail and game over. Complete with documentation my backend brain doesn't understand
Chatbot w/ Memory: Poor. It works, but asks for a name without actually functionally letting the user enter one. 
Text based dungeon: Takes ages to generate and costs a lot (~15 cents), application does however work but doesn't satisfy
the *AI* controlled aspect really.
NOTE: Coder does not know how to handle non-code files, e.g. README's or data files

On the whole fine, takes much longer but files do have documentation though there are occasional flaws and redundancies

### Thinker new workflow
Merge sort: Not a fan of using asserts instead of showing the results but *fine*
File Reading: Fine
Prime Checker: Fine
ToDo CLI : Works but just isn't as good, less intuitive, confusing. 
Snake: Works just the same as the prior Thinker attempt but in pygame
Chatbot w/ Memory: Functional, doesn't do a lot, asks a name and gets a single preference but at least it does it without failing?
Text based dungeon: One version is rather impressive including walls that you can't move through but lots of redundancy,
no imports between files
NOTE: Coder doesn't know to make files import functionality from other created files







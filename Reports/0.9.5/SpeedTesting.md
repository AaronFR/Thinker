# Speed tests

## Internet search and User context functionality testing

The two primary performance-intensive optional functionalities

Each prompt sampled and averaged after 5x runs
 
| Prompt                                                        | Local (s) | Deployed (s) |
|---------------------------------------------------------------|-----------|--------------|
| "Hey" (o3-mini, background: gemini-2.0)                       | 8         | 6.1          |
| "Talk to me in great detail about ancient Rome" (dito)        | 11 (13)   | 12.7         | (from this point on times are logged programatically) (huge variability over time, probably due to load on openAi servers)
| "Talk to me in great detail about ancient Rome" (all gemini)  | 13        | 11.9         |
| "Hey" (all gemini)                                            | 5.4       | 3.7          |
| "Talk to me in great detail about ancient Rome" (all o4-mini) | 15.4      | 15.8         |
| Same prompt (all gemini +internet +user-context)              | 47.1      | 38.7         |
| Same prompt (all gemini +internet)                            | 20.75     | 20.8         | (well now it's greece because I'm afraid of hitting the same sites too much, but you get the idea. Deployed has an outlier that slows it down - but it's a REAL outlier)
| Same prompt (all gemini +user-context)                        | 30.6      | 25.3         | (Notable decrese in time after 4th call in both sets, presumably neo4j client 'warming' up to requests from this address
| Hey (all gemini +internet +user-context)                      | 19        | 15.45        |
| Hey (all gemini +internet)                                    | 12.91     | 8.57         |
| Hey (all gemini +user-context)                                | 12.45     | 7.85         |

### Notes

- Large variation in Deploy times
- Large variation over time, tests have to be run back to back for any degree of accurate comparison
- For reference testing this (110 prompts) cost approximately ~27 cents

### Functionality percentage increase in duration estimates

| Functionality                 | Local | Deployed |
|-------------------------------|-------|----------|
| Complex task (all gemini-2.0) | 1x    | 1x       |
| +internet                     | 1.6x  | 1.75x    |
| +user-context                 | 2.35x | 2.1x     |
| +internet +user-context       | 3.25x | 3.65x    | (These measurements roughly add up to the combined total: 1.6 x 2.35 = 3.76 , 115% of actual. 1.75 x 2.1 = 3.675x, 100.7% of actual)

| Functionality                 | Local | Deployed |
|-------------------------------|-------|----------|
| Very simple task              | 1x    | 1x       |
| +internet                     | 2.4x  | 2.3x     |
| +user-context                 | 2.3x  | 2.1x     |
| +internet +user-context       | 3.5x  | 4.3x     | (Deployed roughly matches up to the combined total, 2.3 x 2.1 = 4.83, 112.3% of actual. Local is -at least the same order of magnitude? 2.4 x 2.3 = 5.52, 157% of actual)

### Conclusion

- Deployed has a small time advantage for small prompts, probably around 2 seconds to restart for a request locally
  - However, more functionality costs proportionally more time when deployed. It's not clear what this could be.
- True to the general llm analytics, gemini is not only faster but has a notably lower latency, around 2 seconds for the simple prompts
- We can *very* roughly state that internet functionality adds a 2x increase in duration, while user context gives a more consistent 2.1x multiple
  - These are based on the deployment times, while local is good for comparison and for informing decisions based off local development feedback: users will be using the deployed instance.
- User context can be moved out of beta, its very slow- but internet search is not *really* slower


## Best of testing

This isn't *just* a speed test, it's also a test of best of it's self, what it's good at or not
All tests will be run on gemini-2.0, and on the deployed instance.
For the Best of columns the time and cost are measured.

| Functionality             | w/ out Best of  | Best of 2      | Best of 3           | Best of 5       | Best response? |
|---------------------------|-----------------|----------------|---------------------|-----------------|----------------|
| "hey"                     | ¢ 0, 3.76s      | ¢ 0, 4.83s     | ¢ 0, 5.22s          | ¢ 0.01, 4.93s   | 5 or n/a       | (1 decided to do a code block for some reason, 2 and 3 are litterally identical, 5 is more personable)
| Holiday suggestion        | ¢ 0.02, 6.49s   | ¢ 0.03, 8.41s  | ¢ 0.03, 11.74s      | ¢ 0.12, 12.07s  | 5              | (Hands down, Gives 2 primary recomendations, 3 additional ones and actually good advice. 2 and 3 still identical and 1 is the 2nd best
| What men think about      | ¢ 0.01, 6.82s   | ¢ 0.05, 11.84s | ¢ 0.07, 10.77s      | ¢ 0.13 , 20.35s | 5              | (2 and 3 we're meerly similar, what's
| Current News +internet    | ¢ 0.05, 12.15s  | ¢ 0.17, 18.21s | ¢ 0.24, 17.28s      | ¢ 0.27 ,18.22s  | 3              | (Encountered timeout errors on 2 and 3, ran locally so don't look too hard into the times)
| Write Code (bug fix)      | ¢ 0.36, 44.13s  | ¢ 0.36, 29.1s  | ¢ 0.51, 199.75s (!) | ¢ 0.96, 56.96s  | 1              | (Brutal errors, possibly caused by an empty user or system message. (I don't know why gemini chooses to raise an exception when an empty string system message is sent, but hey), the extremly high time in best of 3 is simply caused by the first step timing out
| Discuss Code Improvements | ¢ 0.14, 24.37s  | ¢ 0.61, 49.38s | ¢ 0.55, 49.38s      | ¢ 0.97, 39.18s  | 1 (5 in 2nd)   | (+internet)
| Improve tooltips          | ¢ 0.05, 9.72s   | ¢ 0.21, 20.4s  | ¢ 0.23, 18.55s      | ¢ 0.38, 21.39s  | 1              | (local)
| Platform recommendations  | ¢ 0.01, 14.63s  | ¢ 0.07, 23.79s | ¢ 0.07, 20.9s       | ¢ 0.12, 23.67s  | 1 (5 in 2nd)   | (local)
| Activity suggestion       | ¢ 0.007, 13.67s | ¢ 0.03, 19.84s | ¢ 0.05, 19.6s       | ¢ 0.07, 20.35s  | 5              | (local)
| Activity suggestion (o3)  | ¢ 0.04, 11.76s  | ¢ 0.74, 17.14s | ¢ 0.98, 19.49s      | ¢ 1.75, 24.91s  | 5 (3 in 2nd)   | (Curiously repeated tests, bear out the disproprotionate cost increase of using best of - on o3
| Activity suggestion (o3)  | ¢ 0.27, 13.72s  | ¢ 0.82, 23.56s | ¢ 1.02, 23.53s      | ¢ 1.74, 28.36s  | 2 (1 in 2nd)   | (Post fix to costing mechanism)
| Improve Sys Messages (o3) | ¢ 0.52, 15.88s  | ¢ 1.37, 35.32s | ¢ 1.89, 37.01s      | ¢ 2.44, 37.94s  | 2 (1 in 2nd)   | (Responses best of 3 and best of 5, didn't really produce any notable benefit)
// ToDo: Test o3-mini and measure the time changes

### Notes

- High variability in times, sometimes the Best Of 5 prompt is the longest sometimes a 'smaller' prompt

#### Improve System Messages

Values include any improvements on prior messages (so bear in mind that just because a test case doesn't have any values
doesn't *necessarily* mean it's worse than the last case, just that it isn't better.)


### Conclusion

It's hard to say from this testing run which is better, it appears as though there's a dichotomy:

- Best of on gemini models appears to have a 'Go big or go home' effect, the 5th response is usually the best -or best of disabled
  This implies that there is a 'watering down effect', that repeating these calls injects more and more *A*i into the response,
  Eventually this watering down affect is overcome with enough disparate material and a superior answer is achieved.
- Best of on 03 appears to have a stronger 'watering down' effect. The best responses appear to be at best of 2 or best of disabled.
  This suggests that with more and more content the evaluator actually makes the responses *worse*.

However, there isn't enough data (*especially* not for 03) to be sure about this, as the system messages will be changed and tested next, 
the Best of testing will stop for this set and continue again for another.


## System Message Improvements

### General Notes

| Sys Message         | Original                                                                                                                                         |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| Categorisation      | Works quite well, possibly produces too many categories, but my use isn't typical - its testing                                                  |
| Coder Persona       | Fine, openAi typically reasons and provides explanation AFTER the message, which I don't like, gemini doesn't                                    |
| Writer Persona      | I really don't like gemini's attempts at trying to be personable, OpenAi is more machine like which is it's own problem                          |
| Prompt Augmentation | Destroys long form content less often than it used to, *significantly* increases prompt length which may or may not actually improve performance |
| Prompt Questioning  | Generally pretty good, decent length, still maybe a third to a half irrelevant.                                                                  |
| Summarisation       | Works fine                                                                                                                                       |
| file Summarisation  | Works pretty great.                                                                                                                              |
| Best of             | See above, has it's issues. The 'watering down' effect is interesting I wonder how much it can be mitigated with                                 |
| Persona Select      | Perfectly fine with it's selections, but possibly too verbose                                                                                    |
| Workflow Select     | Usually picks just fine, though personally I still get caught telling the AI to 'write' something instead of telling me                          |

### Input, Output tokens (lower is better, typically)

| Sys Message         | Original           | Iteration 1 | Iteration 2 | Iteration 3 | Iteration 4    | Iteration 5 | Iteration 6 | Iteration 7 |
|---------------------|--------------------|-------------|-------------|-------------|----------------|-------------|-------------|-------------|
| Categorisation      | (119, 61)          | (116, 35)   | (100, 40)   | (92, 44)    | (158.4, 114.2) | (141, 42)   | (116, 7)    | (132, 5)    | (moderate increase in input tokens but dramatically decreased output tokens, which is what takes time and money to calculate.
| Persona Select      | (64, 2), (64, 2)   | N/A         |             |             |                |             |             |             | (it's kind of unbelivable that its only two output tokens but the system is designed to output only a single word)
| Workflow Select     | (100, 2), (100, 2) | N/A         |             |             |                |             |             |             |


### Logs

#### Categorisation

- For testing we use the prompt "What happened in the Xth century" which should be fairly obviously categorised as history.
  - Base existing setup
    - Actually categorises into the existing 'None' category, which is pretty bad.
      ```
      Category Reasoning: The prompt is asking for information about a historical event. This falls under the category of
      providing information, which often involves some level of analysis to determine what is "most interesting". However, 
      without a specific task related to code or systems, the best fit is simply providing information.
  
      <result="none">
      ```
    - Catchall categorises like this definitely pose a problem for categorising messages correctly, another being 'information'
  - Eventually I could spot that the reasoning didn't flow into the actual conclusion:
    - ```
      Category Reasoning: The input is a question about a historical event.
      Therefore, the category is history.

      <result="analysis">
      ```
    - This kind of error was because (for whatever reason) the system messages and user messages where swapped, no
      other AiOrchestrator function call appears to make the same mistake.
  - Fixing system/user message ordering instantly improved categorisation, but it still takes too long and doesn't 
    respond well to explicit instructions to categorise.
    - Additionally, system messages where split apart, there are now 3 system messages.
      - the users actual sys instructions from the settings
      - Context for supplied categories and implications of selecting a category outside the set
      - Necessary Formatting instructions
    - Although additional system messages will add a handful of extra tokens on openAi models (as I found out from 
      recent work on extracting usage data), ensuring that the first and last messages are prioritised and the middle 
      is de-prioritised is worth it.
    - The key detail is that the LLM has to be specifically told that it's not expected to remain with the set of
      supplied examples, (gemini) must be really over-trained on those kind of 'identify from set' problems.
  - Now that categorisation actually works as intended we can look at decreasing output costs and task duration
    - Critically it was discovered that giving gemini 'space' to reason doesn't actually help. And telling it to 
      instantly come to a conclusion can be as accurate as letting it think through the process -> 10-fold decrease in
      output costs.
      - Increase in input costs by approx ~5%, which is fine.
      ```
      Category Reasoning: <result="history">
      ```
- ~~The next step in improving performance would be to 'front-load' categorisation - at the same time messages are 
  automatically selected persona's and workflows, evaluating what processes inside requests take what amount of time,
  under which circumstances is work for later, but I would estimate this could save 1 second of time if the category
  is front-loaded in advance?~~ (Sure does)
        
#### Prompt augmentation

- For testing, we'll look at some standard use cases, we'll alternate from Gemini-2.0 flash and 04-mini for the
  background model (foreground model is gemini-2.0 flash)
  - simple coding question (```Give me a python pi calculator```)
  - Refactor coding question (refactor ...AiOrchestrator.py for x)
  - Internet search (news)
  - Advice "How can I improve my exercise regime?"
- simple coding question
  - Base, no augment used: Gives 3 simple examples of pi calculation methods (fluke, not replicated on next 2 tries)
  - Augment, outputs a *lot* on gemini models
      ```
      Okay, let's craft a well-engineered prompt for generating a Python-based Pi calculator.

      **New Prompt:**

      "I need a Python program to calculate Pi to a specified number of decimal places using the Leibniz formula for Pi 
      approximation. Please provide a complete, runnable Python code snippet.

      **Instructions:**

      1.  **Specify Algorithm:** Implement the Leibniz formula (π/4 = 1 - 1/3 + 1/5 - 1/7 + ...).

      2.  **User Input:** Include a mechanism for the user to input the desired number of iterations or terms in the 
      Leibniz series to control the precision of the Pi calculation. Error handling should be used to ensure the value 
      provided is an integer.

      3.  **Calculation Loop:** Create a loop that iterates the specified number of times, adding or subtracting terms 
      of the Leibniz series as required.

      4.  **Pi Approximation:** After the loop completes, multiply the resulting sum by 4 to approximate Pi.

      5.  **Output:** Print the calculated approximation of Pi. Also, print the number of terms/iterations used in the 
      calculation. The output should have a clearly defined format (e.g., "Pi Approximation: 3.14159, Iterations: 1000000").

      6.  **Code Comments:** Include clear and concise comments throughout the code to explain each step of the process, 
      including the Leibniz formula implementation.

      7. **Constraints:** Prioritize code readability and clarity over extreme optimization. 
      The code should be compatible with standard Python 3 installations without requiring external libraries beyond the 
      Python standard library.

      Provide the complete Python code solution based on these specifications."
      ```
    - Provides only 1 example (ran 3 times), really prefers the Leibniz
  - Much more restrained on 4o-mini
    - ```
      Please provide a Python program that calculates the value of π (pi) using a well-defined algorithm. 
      The program should include clear comments explaining each step of the process, handle exceptions if necessary, 
      and output the value of π with a specified level of precision. Additionally, please outline the method used for 
      the calculation, such as the Monte Carlo method, the Leibniz formula, or any other technique you deem appropriate.
      ```
    - Does indeed have lots of documentation and input verification. (3x)#
    - Review
      - Like the first base answer for it's variety, but it lacks an explanation of what each of the 3 algorithm's do
        and how they work
      - Remaining base answers are fine if technical
      - gemini answer #2 has the best explanation, ironically #3 includes a lot more explanation by volume, but simply stating
        ``Calculates Pi to a specified number of terms using the Leibniz formula:
          π/4 = 1 - 1/3 + 1/5 - 1/7 + ...``
        Gets the concept across a lot better
      - o4-mini derived answers are fine.
      - This test is really just to confirm the augment functionality doesn't distory the answer to the point of
        un-usability, which it doesn't. To see if it improves answers further tests will be evaluating based on a
        specific *metric*
  - `Give me an improved version of AiOrchestrator.py, improving code cleanliness and optimal logical flow`
    - Avoiding the word 'write' so as to avoid triggering a write-workflow by accident
      - When evaluating the select workflow functionality I might want to consider making writing a file more..
        *explicit*, because I fall for it all the time and I'm the one who wrote the thing.
    - Base:
      - Documentation changes, use of Union (which I'm not a fan of), improved names
      - Dito but less useful
      - ❌ Complete overhaul: Usually I want Thinker to change my codebase more thoroughly but this is a decimation
        the new code is just debug and placeholder functions (?)
    - Gemini derived augmentations
      - DOESN'T implement UNION types (👍), documentation, adds a helper function and documentation where it didn't 
        previously exist
      - Does the opposite and combines a helper function into one larger internal method, I do think it leads to better 
        more readable logic flow though.
      - Changes parameter documentation scheme which I don't like but hey that's subjective, adds examples - clarifies 
        '__main__' example,  doc and name improvements, dito on helper function absorption from the 2nd
    - ❌ o4-mini
      - "Below is my step‐by‐step reasoning followed by the enhanced version of the AiOrchestrator.py script." No actual 
        changes
      - Minor doc and name changes (prompter => ai_client), removed RERUN_SYSTEM_MESSAGES: I won't complain, I don't
        *want* that, but if this was production code for a big organisation those varaibles *should* go.
      - Minor doc and name changes
    - Gemini-augmented prompts lead to the best responses, while not too surprising it is note worth that the original augment instructions were created 
      with 4o-mini in mind.
- Internet search
  - `Whats going on in the news today?`
    - Base
      - Simple coverage of American geo-politics, Pensslyvania plane crash, generic news about wildfires - without
        mentioning where they are, AI vulnerabilities e.g. voice cloning.
      - Much worse, almost nothing specific
      - Dito of 1
    - Gemini derived augmented prompt
      - *Hilariously* it broke down and thought it was writing a system message for an LLM
      - Too much meta commentary ("here's your request..."), much better formatting, listing by source, much easier to 
        clearer distinction between specific event and implications
      - Dito this time ranking the stories by importance, including links, but imagining the last story about a 'renewable energy breakthrough'
    - 4o-mini derived
      - Not bad at all, organises by topic
      - Dito, even more detail
      - Local sources selected by internet search, much briefer but still factual.
    - Overall 4o mini actually produces the best results, possibly because for such a usecase gemini's long and
      complicated prompts confuse the issue.
- `How can I improve my exercise regime?`
  - Base
    - Simple, reasonable advice, good attitude "After all, fitness should be fun, not a chore!"
    - Cringe-ier but still decent advice all the same
    - Not as good as 1, but good
  - Gemini derived augmented prompt
    - (I just want to note that the augmented prompt is unironically about 5 paragraphs long) Asks for clarification and
      information about the user (interesting)
      - Follow up: I mean it's a regurgitation of what I put in, but this is a *much* more specific plan, though we have
        to consider the user *just* wanted a simple, generic plan
    - Dito - I'm already pushing the amount of time I have just doing this testing, I have to move on and asusme it's the same
  - 4o-mini derived
    - Really detailed advice for all levels of users
    - Asks for tailored information like gemini, but it asks for a lot less.
    - Detailed, good answer.
  - Conclusion
    - It's subjective but I have to imagine for most users the 4o-mini derived answers are best: if they wanted to be
      asked lots of questions about their current regime, they *would* have just provided that information up front.
- Testing Conclusion:
  - Mixed: Gemini derived augmented prompts appear best for coding tasks, producing deeper structural changes while 
    maintaining consistency and purpose, 4o-mini derived prompts on the other hand appear to benefit non-coding tasks
    possibly because of an 'over-complication' effect caused by gemini being so wordy.
    - I believe this wordiness benefits coding tasks but 'confuses' more simple to the point tasks

Now that we have some sort of understanding of how augment prompt works currently, what it's good for, under what 
circumstance, we'll compare augmented prompts directly.
The system prompt has to be edited to ensure gemini outputs less, that it's more focused on output quality, meanwhile 
4o-mini needs to output *more* for coding tasks specifically, otherwise gemini needs to emulate it's outputs.

It's annoying: It's a definite priority to get to open-beta as fast as possible, but at the same time, it's only after 
this testing I can talk about a functionalities actual utility: I can say that now categorisation: "Outputs an accurate 
single word category, at least 75% of the time". Before I could only say "it categorises well enough, I suppose."

Similarly, for best of, I could just say "I've had good results before", now I can say "It improves coding based 
responses -gemini works best, and for non-coding I would recommend switching to 4o-mini, it can significantly improve
formatting and quality of results -depending on your own prompt of course."

Base sys message:
```
Take the given user prompt and rewrite it augmenting it in line with prompt engineering standards. Increase clarity, 
state facts simply, use for step by step reasoning. Returning *only* the new and improved user prompt Augment user prompt 
with as many prompt engineering standards crammed in as possible, do not answer it
```
->
```
Rephrase the user prompt into a precise, step-by-step instruction set. Return only the improved prompt.
```
Doesn't properly improve prompt ->
```
Rewrite the users prompt (Don't write 'User Prompt:'), improving it according to prompt engineering standards. 
If details are unclear attempt to clarify, state facts simply.
Use clear, consise formatting. If the user provides examples, code snippets or other context make sure to leave them 
un-altered but clearly formatted.
Breakdown complex tasks into multiple simpler steps.
Be specific, descriptive, detailed and relevant, adding relevant context.
Write a list of tasks/objectives and areas to optimise focus on.
Return *only* the new and improved user prompt without meta commentary, do not answer it.
```
Forgets the purpose of this task

Remove mentioning of 'cram', does gemini produce more reasonably sized requests?
```
Take the given user prompt and rewrite it augmenting it in line with prompt engineering standards. Increase clarity, 
state facts simply, use step by step reasoning. Returning *only* the new and improved user prompt, do not answer it
```
Attempt to remove meta commentary? ->
```
You are a prompt engineer, take the given user prompt and rewrite it augmenting it in line with prompt engineering standards. 
Increase clarity, state facts simply, use step by step reasoning. 
Returning *only* the new and improved user prompt, without answering it, as if they had written it themselves.
```
Attempt to improve reference text/code formatting ->

```
You are a prompt engineer, take the given user prompt and rewrite it augmenting it in line with prompt engineering standards. 
Increase clarity, state facts simply, use step by step reasoning.
If I include text/code as reference, please consider keeping it as is, provided it makes sense for the request as a whole.
Returning *only* the new and improved user prompt, without answering it, as if they had written it themselves.
```


Test initial prompts 

- Give me a python pi calculator
- Give me an improved version of AiOrchestrator.py, improving code cleanliness and optimal logical flow
- My application is suffering from a bug, something about an 'index out of bounds' error?
- Whats going on in the news today?
- How can I improve my exercise regime?


- Ai generated sys message suggestion (4o-mini):
  - Not as good, reliably tells the program to perform actions it can't "Run the script", there is also less consideration 
  of edge cases and the user experience no "Include clear comments"
- More elaborate version of original
  - Somewhat 'forgets' that it's writing a prompt for the user to send to the LLM, instead of sending a request to the user
    I like the lists of specific objectives, but the original gives more useful instructions.
- Example prompt optimisation prompts online
  - Actually much worse at understanding that its re-writing a users prompt, not writing to the user *for* a better prompt.
  - Same on gemini, gemini answers are VERY long and comprehensive but they also still understand they're talking TO the 
    user, e.g. including placeholders that the user can fill in, instead of asking the LLM *to ask* the user for clarifying details.
- Example number 2
  - Without mentioning which one it is explicitly, this one is nuts. It outputs about 1000 characters, it so much text that in
    trying to put it on the screen I have to zoom out to max.
    - Still has issues, like suggesting to use any algorithm the LLM wants - then telling it specifically to use one *particular*
      algorithm
    - Gives an example output (as in: an entire pi calculator in pi)
    - Gives surplus or non-helpful goals, like devising unit tests for the method or making sure it "understands" the algorithm.
      'Test the application' this is for a prompt where I didn't even add any code, just said I have 'a' bug, *HOW?*.
- Remove mention of 'cram'
  - Universal improvement: it forms a stark contrast with the examples online, I'm not sure if their just happy to get long prompts
    but even if they did happen to produce better results (which I have to doubt), their outputs are just not readable, 
    it's *way* too much to expect a user to read, and they should be reading what they send. I mention this here as
    removing the 'cram' line, noticeably reduces the length of the prompt while still retaining all the essential 
    instructions *without* basically planning out what the main application should do step by step. 
- 'You are a ' prompt engineer + 'as if they had written it themselves'
  - Removes any of the weird formatting, indeed appearing as if the user wrote it.
  - Now we can move to evaluating outputs
    - Almost universally better than the prior prompt, I'm worried I have confirmation bias: The news prompt, response was
      at least subjective: New had sources and more stories, but the old had longer stories, but both gave different context.
  - What areas could be improved, what would you like to see improved?
    - It does still have a bad habit of wiping example text/code
      - 50/50 and sometimes it makes sense, if the application doesn't need the full method just a description of what it is,
        but it definitely happens when it shouldn't.
        - There a trade off: for very large inputs including this text limits the amount of 'space' it has to actually 
          give the improved prompt. I think for the average user it's best to handle reference text/code like they would
          expect without wiping it: Users can be informed of the tradeoff and wipe the extra line if they prefer.
        - I'm contemplating 'add as reference' functionality, which can reference a file or clipboard without internalising it
          within the applciations database, this would work pretty well for code you want edited - without wiping said code.
    - Doesn't add "You are a X" to the users message, this might improve responses making them more specific and focused,
      though it might also conflict with the persona system
      - Even if there is a benefit this is exactly what the persona/workflow system is supposed to be doing, so *for now*
        I won't be considering adding it by default.

#### Questioning

```
Given the following user prompt what are your questions, be concise and targeted. 
Just ask the questions you would like to know before answering my prompt, do not actually answer my prompt
```
Possible improvement?
```
Pose concise, targeted questions to clarify the prompt before answering. Provide only the questions.
```
Better or at the very least *shorter*, can we move the formatting into the code? ->
```
Pose concise, targeted questions to clarify the prompt before answering.
``` 

```
Provide only a list of questions
```
Interestingly 'list' biases the prompt towards providing many- too many questions, 'provide only the questions.' Keeps 
the number reasonable... Actually I'll leave that part to the user, they can decide to get it to try 'reasoning' before 
hand if they like and it's not a bad hint as to how to structure prompts in order to reduce cost.


Set of prompts to question

- Give me a python pi calculator
- Give me an improved version of AiOrchestrator.py, improving code cleanliness and optimal logical flow
- My application is suffering from a bug, something about an 'index out of bounds' error?
- Whats going on in the news today?
- How can I improve my exercise regime?

- Give me a python pi calculator
  - O: What method (lists methods), what level of accuracy, optimise for speed or readability? Simple or complex function
    - These are really good questions to be asking.
  - N: What methods, what level of precision, are there any performance requirements
  - N2: More questions, ...+validation or not?
- Give me an improved version of AiOrchestrator.py, improving code cleanliness and optimal logical flow
  - O: What are your parts of the code to focus on? (error handling, retries, configuration, model selection, handling streams),
       What ares to prioritise? Code duplication, improved readability, better names, PEP 8?
       Can you give info on this method on Utility class and on ErrorHandler class
    - Good. I would probably find the last 3 annoying, but they would help to *some* degree.
  - ✅N: Any parts to focus on? (handle_rerun or Utility.execute with retries), readability, performance or code duplication?
       Are you open to new dependencies that could improve the code? Questions about the efficiency of a specific utility method
       Cab you give info on determine_prompter?
    - The dependencies question is a really good question to be asking.
  - N2: Loads of questions, maybe too many
- My application is suffering from a bug, something about an 'index out of bounds' error?
  - O: What language, can you give me a code snippet, what inputs or operations lead to the error, can I see the stack
  - ✅(~)N: What language & data structures, provide code, what are the index limits and the actual index, what are the 
       specific circumstances. What have your tried debugging wise.
- Whats going on in the news today?
  - O: What region, what topics?
    - Appropriate but very brief
  - ✅ N: What news sources, what topics and what region
- How can I improve my exercise regime?
  - O: What *is* your current regime, what are your goals, whats your current level of fitness, do you have any health conditions?
       What do you enjoy doing?
    - Good questions, really to the point yet comprehensive.
  - N: Dito but with shorter sentences.

#### Writer

I think the way most AI's talk can be improved, most are *cringey*.

Current sys message:

```
You are a professional writer, you are insightful and interesting, your writing is impactful and clear. 
Work on the user's instructions without commentary.
```

```
You are a talented and charming writer. Work on users instructions without commentary providing: insightful, impactful, concise, clear, interesting, and if context provides for it charming/humorous content.
```
Charming and humorous are definitely problem words for gemini, o3 manages this task fine. ->
```
You are a professional writer, you are insightful and interesting, your writing is impactful and clear. 
Work on the user's instructions without commentary.
```
Better seemingly but still rather cringe in places. Ai suggestion? ->
```
Respond with wit, clarity, and brevity. charm without corporate jargon.
```
Actually much worse.
AI modified, but make the writing 'to the point' and 'mature' ->
```
You are a professional writer, you are insightful and interesting, your writing is impactful and clear.
Your tone is mature and to the point.
Work on the user's instructions without commentary.
```
Lets see if AI can smooth over the remaining stupefying writing ->
```
You are an accomplished writer with a refined command of language. 
Your writing must be clear, precise, and insightful, appealing to both the intellect and the senses with measured statements. 
Every sentence should convey meaningful ideas without resorting to clichés, hyperbole, or sentimental excess.
Write in a mature, straightforward manner that avoids stereotypes and empty flourish. 
Whether composing essays, reports, or narratives, ensure that your language remains substantive and original, 
engaging the reader with thoughtful nuance rather than generic or extravagant descriptions.
```
~~I'll try and simplify it~~ Nevermind, lets- GO GAMBLING! ->
```
You are an accomplished writer with command of language and a focus on clarity, precision, and literal meaning. 
Your work must engage the intellect by presenting thoughtful, measured ideas without resorting to clichés, hyperbole, 
or excessive sentiment. 
Every sentence should be substantive and original, conveying meaningful ideas in a straightforward manner that avoids 
unnecessary metaphor, flowery language, or abstract emotional appeal. 
Ensure that all descriptions are literal and fact-based, steering clear of figurative language that distracts from clear 
communication. 
Your writing should neither overstate its subject's qualities nor imbue objects with unwarranted personality—present them
 as they are, emphasizing accuracy, nuance, and insight.
```

And that appears to work, possibly two wordy but the messages are indeed less cringe inducing, though not, not cringe..


Set of prompts to evaluate 'Writer' on

- Talk about rome
- Whats going on in the news today?
- How can I improve my exercise regime?
- How do superconductors work?
- Discuss cinema in the 2010s

Bad writing (lower is better) (running background and front on gemini 2.0 flash)
- Base
  - Write about rome
  - `Ah, Rome! The Eternal City, a place where the past isn't just history, it's a tangible presence you can practically trip over on any given cobblestone street.`
    - Cringe, "Rome is a city full of history" delivers the same sentiment.
  - `Each brushstroke and soaring archway is an expression of human aspiration and skill.`
    - This says literally nothing, even in context
  - `The aroma of freshly baked pizza wafts from every other doorway`
    - I mean maybe it does, I can't really smell.. but this is an extremely stupid, stereotyped way of talking to an actual adult.
  - `Rome is chaotic, it is crowded, it is overwhelming, and utterly unforgettable.`
    - 😟
- Removing use of the word 'humorous' and 'charming'
  - `Rome, a city layered with history like the sediment of centuries` That's actually not bad- `It's a place where the 
     ghosts of emperors whisper from crumbling ruins` 😟
  - `It is, in short, an unforgettable experience.`
- Using the AI suggestion based on my complaints of overly corporate speek.
  - `You've got pasta that'll make you weep with joy`
    - It's actually worse somehow
  - `history spills out onto the cobblestones and gelato is a legitimate food group`
  - `and you'll probably get pickpocketed if you're not careful.`
    - Okay *that's* funny (unintentionally).
- Telling it to be 'mature'
  - `Rome, a city etched in time, resonates with the echoes of emperors, artists, and revolutionaries.`
    - This is so close to being bad
  - `palimpsest`
    - Complex word use? Oooooo
  - `Beyond its iconic landmarks, Rome is a city of hidden gems`
    - We're 3/5ths of the way through and I usually give up at 1/3- if you imagine a 'bullshit-omiter' on a dial,
      we just hit the orange warning zone.
      - ...I guess that would be the light-brown zone...
  - `Rome is not merely a city of the past; it is a living, breathing metropolis. Its vibrant culture, its passionate 
     people, and its unwavering spirit`
    - That's actually alright, I mean 'passionate people' is 100%
  - `make it a destination that captivates the senses and nourishes the soul`
    - Dark brown
- Getting the AI to re-write it again, AKA 'LETS GO GAMBLING!'
  - `It grapples with the challenges of modernity`
    - That's an interesting way of saying it's mis-managed.
  - `the weight of its historical legacy can, at times, feel burdensome, a constant reminder of past glories against 
     which the present is often measured`
    - 😂
  - I include the two above as reference, theres actually nothing cringe in it. I *do* think the prior message, used 
    better more advanced language, so certainly something has been lost.
- Simplifying
  - The new version contains *three* separate sections basically telling the AI (gemini) to 'not be stupid', this is overkill.
  - Remove 'generic or extravagant descriptions'
    - `traverse not just geography, but also time itself` no
    - `These are not static relics, but rather potent reminders of the rise and fall of empires, the enduring nature of 
       power, and the ephemeral quality of human ambition` No, they quite literally are static ruins.
    - `Rome reveals itself in the intimate details of daily life` Rome shows what's it like to live in by being somewhere
      you can happen to live, within. Brilliant.
    - `sunlight dapples the walls` Okay that's pretty good writing, actually. Evocative.
    - `mingling with the scent of ancient stone and blooming jasmine` What does ancient stone smell like?
      Stone??
    - `Roman existence, a thread stretching from the emperors to the present-day inhabitants who still gather in the 
       piazzas to debate, celebrate, and simply be`
      - 😡
    - `, creating a unique and unforgettable human experience.` Sucks
  - Try removing 'avoids stereotypes and empty flourish'
    - `still echoes with the voices of senators, orators, and merchants who shaped the course of Western civilization`
      - It literally does not
    - `The city became a magnet for artists and scholars, contributing to a flourishing of creativity that continues 
       to resonate today` nah
    - Better but still has the odd cringe sentence here and there.
      - Yeah you put back in 'avoid stereotype and avoid empty flourish' and the cringe is gone, well it's at a tolerable level
  - Try removing 'without resorting to clichés, hyperbole, or sentimental excess'
    - No cringe, but appears to be slightly worse in quality.
  - Absolutely sucks bricks on 03-mini now.
    - `echoes of a vast empire that once dominated the known world, its influence stretching beyond borders and time.`
      - What beyond *all* borders? Do you mean the past - before Rome?
    - `The imposing Colosseum, with its storied history of gladiatorial combat` 'storied', it's like it's written by a 
      hypothetical Colosseum marketing department.
    - `now stands not only as a relic of ancient entertainment but as a testament to the human spirit’s enduring quest 
       for cultural resilience` Literally what does this mean?
    - `It challenges us to reflect on our own lives and histories` Not me
    - `Rome is not merely a city; it is an enduring saga of civilization` It's mostly a city though
    - `and the ceaseless march of time` It is a place that exists- in time, gotcha.
    - `gladiators fought beneath a sky that once dripped with the passions of a people both fierce and innovative` 
      I don't know what that's a lot of, but it is.
    - ` Rome continues to whisper its ageless story to those willing to listen` ' Your an inanimate f###### object!'
  - Getting 03-mini to work on a system-message for 03-mini
    - Not as bad, not as good.
    - Have to compare directly
      - 'Talk about rome'
        - B: Rubbish
        - O: Mostly rubbish. *still*
        - N: Mostly factual and on point, a little light on good content.
      - 'What's going on in the news today?'
        - B: `Across the pond in the UK, investigative reports are drawing attention to troubling conditions at a controversial 
              children’s home. Former residents have described the place as being run in a manner reminiscent of a cult—with 
              allegations of abuse and exploitation` That sounds terrible-`—adding a deeply human dimension to the day’s news` 😂
              nice, *very* respectful.
        - O: There is news there, but a lot of nothing too 'navigate an uncertain global landscape' I mean the future is always uncertain, it varies
          but that statement is always true.1.5 bunk statements (a 'certain' Canadian Tariff: I know exactly which one, more like 'vague') as opposed to new's 5
        - N: 1.5 bunk statements (a 'certain' Canadian Tariff: I know exactly which one, more like 'vague') as opposed to new's 5
      - 'How can I improve my exercise regime?'
        - B: Fine, a medium amount of text
        - O: Fine. I would have liked a list in there, but it's a whole lot of basically useful text
        - N: Less text, still good. It's literally the same information, on one hand the more concise view is quicker to read, but the old 
          text is nicer to read.
      - 'How do superconductors work?'
        - B: Perfectly fine, reasonable explanation
        - O: I'm not a huge fan of its explanation, it's correct, but I prefer explaining that Cooper-Pairs are bosons, (its very cool)
          not scattering each other, following the path of least resistance: None.
          Decent though, an explanation without bunk (except for a little bit at the end)
        - N: "paired electrons avoid scattering" Ah, still doesn't say *why*. It's personal preference. Much more to the point and
          gives a succinct explanation of Type I and Type II superconductors which I didn't get till now.
      - 'Discuss cinema in the 2010s'
        - B: Gives a nice list of changes which are actually mostly believable, actually refernces a specific film as an example
          of a trend.
        - O: Certainly an essay no references. `the decade was distinguished by a willingness to explore complex, often 
          ambiguous themes rather than offering neat, emotionally charged conclusions` Sure would have liked to live in the
          2010's the AI is talking about.
        - N: Fully accurate and believable, no exact references still but a general summary. 
          - `Digital filmmaking became dominant, allowing directors to experiment with more accessible camera technology and post-production techniques`
          - `Studios invested significantly in cinematic universes` Factual
            - ` which yielded consistent returns` (Non-Factual)
    - Overall while the quality might actually be decreasing and long prompts are bad for flexibility and just simply cost and speed,
      I'm absolutely prepared to make these trade offs to avoid listening to hockney, vapid *tripe* from AI. I think in future,
      I will need to get other opinions as this one of the more subjective areas


#### Speed Test

JWT refreshed on new request
```
[14/Mar/2025 15:21:43] "OPTIONS /auth/refresh HTTP/1.1" 200 401 0.001000
[14/Mar/2025 15:21:43] "POST /auth/refresh HTTP/1.1" 200 1570 0.002001
```

Socket connected 
```
[14/Mar/2025 15:21:43] "GET /socket.io/?#### HTTP/1.1" 200 330 0.001108
2025-03-14 15:21:43,449 [INFO] (process_message_ws.py:41) 🟢 Client connected
```

Workflow trigger log T+ 0.115s
```
2025-03-14 15:21:43,564 [INFO] (process_message_ws.py:64) process_message triggered [KBjYRvDPLbzqQQia5huT7m] with data: {'prompt': 'Hey', 'additionalQA': '', 'files': [], 'messages': [], 'persona': None, 'tags': {'model': 'gemini-2.0-flash', 'workflow': None}}
```

User config loaded on startup T+ 0.484s
```
2025-03-14 15:21:43,762 [INFO] (S3Manager.py:131) YAML data loaded from S3: UserConfigs\Config.yaml
2025-03-14 15:21:43,933 [INFO] (S3Manager.py:131) YAML data loaded from S3: UserConfigs\nFVv7DteGDsKu5gfJNkaqb.yaml
```

Messages Generated T+ 0.671s
```
2025-03-14 15:21:44,120 [INFO] (ChatGptMessageBuilder.py:67) Generated role messages - [GeminiModel.GEMINI_2_FLASH] : [{'role': 'system', 'content': "Take the provided input and assign it the most appropriate category.\nThe supplied categories are for reference you don't *HAVE* to select an existing category. "}, {'role': 'system', 'content': 'The existing categories are supplied, by suggesting a new more appropriate category, said category will be created in the system.'}, {'role': 'system', 'content': 'Categorize the data with the most suitable single-word answer.Write it as <result="(your_selection)">'}, {'role': 'user', 'content': '<input>Hey</input>'}, {'role': 'user', 'content': 'Existing categories: advice, aggregation, analysis, configuration, creation, critique, debugging, default, deployment, discussion, documentation, explanation, fitness, formatting, generation, greeting, history, identification, improvement, information, intake, management, mathematics, modeling, number, orchestration, performance, physics, planning, playlist, programming, recommendation, refactoring, refinement, review, security, styling, testing, writing'}]
```

First LLM call: Categorisation T+ 0.780s
```
2025-03-14 15:21:44,228 [INFO] (ChatGptMessageBuilder.py:33) Tokens used (limit 128k): 3
2025-03-14 15:21:44,228 [INFO] (AiOrchestrator.py:85) Executing LLM call with messages:
[{'role': 'system', 'content': "Take the provided input and assign it the most appropriate category.\nThe supplied categories are for reference you don't *HAVE* to select an existing category. "}, {'role': 'system', 'content': 'The existing categories are supplied, by suggesting a new more appropriate category, said category will be created in the system.'}, {'role': 'system', 'content': 'Categorize the data with the most suitable single-word answer.Write it as <result="(your_selection)">'}, {'role': 'user', 'content': '<input>Hey</input>'}, {'role': 'user', 'content': 'Existing categories: advice, aggregation, analysis, configuration, creation, critique, debugging, default, deployment, discussion, documentation, explanation, fitness, formatting, generation, greeting, history, identification, improvement, information, intake, management, mathematics, modeling, number, orchestration, performance, physics, planning, playlist, programming, recommendation, refactoring, refinement, review, security, styling, testing, writing'}]
2025-03-14 15:21:44,229 [INFO] (AiOrchestrator.py:114) EXECUTING PROMPT
```

Earmarking occurs T+ 1.136s
```
2025-03-14 15:21:44,585 [INFO] (AiWrapper.py:99) Total guesstimated cost: 0.0008002999999999999
2025-03-14 15:21:44,857 [INFO] (NodeDatabaseManagement.py:643) Earmarked from user balance for ongoing AI request: 0.0008002999999999999 - total currently earmarked: 0.06094665000000013
2025-03-14 15:21:44,857 [INFO] (models.py:4664) AFC is enabled with max remote calls: 10.
```

User Balance updated T+ 2.121s
```
2025-03-14 15:21:45,570 [INFO] (NodeDatabaseManagement.py:679) User balance updated by: -1.99e-05 (earmarked value: 0.0008002999999999999
2025-03-14 15:21:45,884 [INFO] (NodeDatabaseManagement.py:723) System gemini balance updated by: -1.99e-05
2025-03-14 15:21:45,884 [INFO] (AiWrapper.py:127) Expensing $1.99e-05 to USER_PROMPT Node[KBjYRvDPLbzqQQia5huT7m]
```

Categorisation finishes T+ 2.636s
```
2025-03-14 15:21:46,084 [INFO] (AiOrchestrator.py:92) Execution finished with response:
<result="Greeting"></result>
2025-03-14 15:21:46,085 [INFO] (CategoryManagement.py:68) Category Reasoning: <result="Greeting"></result>
2025-03-14 15:21:46,085 [INFO] (CategoryManagement.py:173) Prompt categorised: greeting
```

Creating blank user prompt node for later population T+3.537s
```
2025-03-14 15:21:46,986 [INFO] (NodeDatabaseManagement.py:200) User prompt node created with ID: KBjYRvDPLbzqQQia5huT7m for category: greeting

```

Executing Chat workflow T+3.623s
```
2025-03-14 15:21:46,987 [INFO] (BasePersona.py:122) Executing workflow 'chat'.
2025-03-14 15:21:46,987 [INFO] (ChatWorkflow.py:41) Chat workflow selected
2025-03-14 15:21:46,987 [INFO] (BasePersona.py:164) Message content: []
2025-03-14 15:21:46,987 [INFO] (BasePersona.py:196) Processing user messages: ['Hey']
2025-03-14 15:21:47,072 [INFO] (AiOrchestrator.py:114) EXECUTING PROMPT

```

LLM chat step starts streaming T+3.744s
```
2025-03-14 15:21:47,193 [INFO] (AiOrchestrator.py:92) Execution finished with response:
<generator object GeminiWrapper.get_ai_streaming_response at 0x0000####>
2025-03-14 15:21:47,193 [INFO] (process_message_ws.py:95) [KBjYRvDPLbzqQQia5huT7m] Response generated, streaming...

```

Call finishes and is expensed T+4.972s
```
2025-03-14 15:21:48,421 [INFO] (NodeDatabaseManagement.py:723) System gemini balance updated by: -3.32e-05
2025-03-14 15:21:48,421 [INFO] (AiWrapper.py:127) Expensing $3.32e-05 to USER_PROMPT Node[KBjYRvDPLbzqQQia5huT7m]


2025-03-14 15:21:48,562 [INFO] (NodeDatabaseManagement.py:771) Node with UUID [KBjYRvDPLbzqQQia5huT7m] updated by [3.32e-05] - None
2025-03-14 15:21:48,562 [INFO] (AiWrapper.py:135) Request cost [GeminiModel.GEMINI_2_FLASH] - Input tokens: 156, $1.56e-05, Output tokens: 44, $1.76e-05
Total cost: $0.0000
```

Populating user_node T+5.441
```
2025-03-14 15:21:48,563 [INFO] (NodeDatabaseManagement.py:217) Attempting to populate USER_PROMPT: user_idnFVv7DteGDsKu5gfJNkaqb, message_id: KBjYRvDPLbzqQQia5huT7m, category: greeting
2025-03-14 15:21:48,861 [INFO] (Neo4jDriver.py:63) Record returned: <Record user_prompt_id='KBjYRvDPLbzqQQia5huT7m'>
2025-03-14 15:21:48,861 [INFO] (Neo4jDriver.py:68) Field 'user_prompt_id' value: KBjYRvDPLbzqQQia5huT7m
2025-03-14 15:21:48,890 [INFO] (NodeDatabaseManagement.py:236) User prompt node populated with ID: KBjYRvDPLbzqQQia5huT7m
```

Workflow completed T+5.441s
```
2025-03-14 15:21:48,890 [INFO] (process_message_ws.py:115) [KBjYRvDPLbzqQQia5huT7m] Request completed in 5.33s
```

##### Notes

0.5 seconds spent loading user config, this was a thought I had for flexibility: You be better off sending config from the frontend

2 seconds dedicated to categorisation: 'Front loading' could significantly speed up prompts (done)

1 second appears to be spent initialising the USER_PROMPT node for this request, (possibly extra processing from Categorisation as well), 
-> consider putting on async thread

Chat execution takes 1.5 seconds, roughly 30% of the time of the full request.

0.5 seconds spent populating the user prompt node, you could think about off-loading this to a thread: but the user has their content
the answer by now anyway so it doesn't really matter.

#### Write workflow

Determining which is better: Chat or Write to file

Foreground model: gemini 2.0 flash

| Task                                           | Chat | Write |
|------------------------------------------------|------|-------|
| Improve TagsSelector.js                        | ✅    | ❌     | (Chat improve on documentation, write erases it, both memoize, chat appears to understand the purpose of the file better - write adds a console warn against intended functionality (writing a new option), chat provides a much more clever logical flow)
| Improve CategorySelector.js (Prompt Augmented) | ✅    | ✅     | (Both other beneficial changes (chat does strip the create new category functionality out for no good reason though), chat assumes I don't want to change too much at once, write assumes I do - uses dependencies for virtualisation. As it happens I don't and I'm going with chat's response but that doesn't mean Write provided a worse answer)
| Improve UserInputForm.js formatting            | ✅    | ❌     | (Easily chat, it suggestions have given me a lot to chew over, with changes well suited for mobile.
| Improve MessagePane.js formatting              | ✅    | ✅     | (Write mangles formatting on home page and affects files pane, but it actually happens to be closer to the approach I want to go with -to start with anyway)
| Improve Workflow.js formatting                 | ✅    | ✅     | (It multi-filed again, even with the setting disabled. Redundent as both produced nearly identical code, my prompt *was* very specific)
| Write about ancient Ro- Greece                 | ❌    | ✅     | ('Ancient Greece, a civilization that bloomed like a radiant flower from the rocky soil of the Aegean' I tried so hard and got so far. But in the end-  Hands down write is better, not even close. Chat mentions almost no facts just the usual shallow platitudes. Write is packed with facts, at worst theres a little repitition -but hey that's how you learn things anyway
| Write about ancient Persia                     | ✅    | ✅     | (Both are good, Chat is more focused on a particualr empire (Achaemenid) wheras write is focused squarley on giving a general comprehensives overview)
| Write about GameFreak                          | ✔    | ✅     | (I tried this recently with my friends and chat was pretty cringe, Saying "Talk about X the Y" as opposed to "Talk about X" appears to produce far better results with less empty platitudes, *possibly* because the former is more associated with empty platitude explanation and definitions online: Anyway write is superior: Chat implies that Game Freak the Fanzine and Game Freak the stuido where founded in the same year, rather than 6 years apart. It also implies Pokemon Red and Blue was there first game, Write being much more detailed avoids these incorrect implications) 
| Write a function for calculating Pi            | ✅    | ✅     | (Write is technically better in that it uses input validation but it's still a very simple implementation)
| Write a *efficient* function for Pi            | ✅    | ✅     | (Technically B provides a more efficient approach, though the question was limited to a set precision so that's not exactly fair)

It seems for coding tasks the extra planning stage can 'disconnect' it from the original vital context.
This context would be important for real tasks, but not important for general testing questions.

It's worth bearing in mind Coder Write workflow and Writer Write workflow are different workflows, if one is performing better than the over in all situations
the flawed worfklow should be rolled into the more comprehensive one.

| Task                                 | Chat | Write |
|--------------------------------------|------|-------|
| Improve OutputSection.js formatting  | ❌    | ❌     | (Nothing much of value, though there wasn't too much to be done, Write DID suggest a way of trying to handle different elements better when closing tags -but it badly malformats output)
| Improve FileItem.js formatting       | ✅    | ✅     | (Both provided wonky but valuable suggestions, ultimately I went with write's suggestion
| FileItem.js auto-format code         | ❌    | ❌     | (For whatever reason both nuke a lot of the files content and break it, (chat did suggest at least somewhat useful CSS changes)
| Write about ancient India            | ✔    | ✅     | (Write is very long, and split into pages - I was wondering if my own page system had triggered somehow)
| Write an *efficient* function for Pi | ✅    | ✔     | ( Chat: 1000 digits in 0.0030 seconds, Write has a OverFlow failure that needs correction, 0.0040-0.0050 seconds after correction)
| Improve Guide.js formatting          | ❌    | ✔     | (Chat: Actually removes left margin causing text to 'scrape' against the window border, Write causes element centering to be lost but it atleast adds borders around the two text blocks which -isn't a lot but it's something)

// Trying to open unexpanded category WORKS again if you happen to have A category open


##### Conclusion 

The additional 'planning' stage in Write workflows seems to be a help or hindrance based on context

In coding contexts the additional artificial material appears to hinder more often, though the initial user message has 
been re-introduced into the write step, it's hard to tell if it has a benefit, I simply don't have that many applicable
coding problems to hand currently.

The planning stage on the other hand does great benefit for fleshing out chat workflows, to the extent that I'm considering
adding it as an option/switch in chat and other workflows. It is worth noting however that the prompts above we'ren't augmented
so augmenting the problem may reduce the difference considerably.


# Write Pages

All in gemini 2.0 flash because I don't like even contemplating how much 03-mini would cost.

| Task                                                                        | #Pages | Cost   | Review                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|-----------------------------------------------------------------------------|--------|--------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Write a guide for frontend frameworks                                       | 6      | ¢ 0.48 | ✅ Solid. Goes into detail and forms a solid impression of Indian history and culture                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Write about ancient Rome in tremendous detail                               | 10     | ¢ 0.67 | ✅ Really good, provides a general overview before drilling into the details and then summarising the contents. begging, middle and end.                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Come up with a plan for a social network based on maps of content           | 15     |        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Short story (inspired by The Three Body Problem Trilogy)                    | 20     | ¢ 0.29 | ❌ A mess. It has some ideas, maybe. But it's Not A story except for a brief bit in the middle, it even near the end harshly reviews the illogical writing in *itself*, so I suppose I don't have to                                                                                                                                                                                                                                                                                                                                                                                                       |
| Story (Inspired by The Stars our Destination and ambiguous protagonists)    | 40     | ¢ 1.88 | ❌✔ It generated *a* story after being explicitly told to do so and only create a story, with characters with the same name and a frequently named maguffin, but that's about the end of the coherency. Written in parallel mode so what else could you expect? Writing wasn't too great either 'Gravitational Degeneracy' caused by 'varying gravitational fields' had me laughing pretty hard. Tell it 'hard-sci' explicitly next time.                                                                                                                                                                  |
| - Dito but instruct it ensure each page is given the essential plot details | 20     | ¢ 0.58 | ❌✔ It's more coherent but is is *not* coherent. Jumps around the place it's still pretty clear that it's just writing in parallel. Maybe a specific write-story workflow would be good... AWFUL writing though                                                                                                                                                                                                                                                                                                                                                                                            |
| - Dito but with sequential steps enabled                                    | 10     | ¢ 0.52 | ✔ Coherent, well except for one part where the maguffin changes from one page to the next - presumably either the LLM for the page took a liberty it shouldn't have and included the maguffin, before it should have been introduced. Awful writing by the way `"And what exactly is someone like me, Inspector? A space rat? A scavenger? Someone who doesn't deserve a shot at a better life?" He paused, a flicker of defiance in his eyes. "Maybe I'm all those things. But I'm also the only one who knows how to get this thing off this derelict before it blows us all to kingdom come.` Rubbish. |
| - Dito but with sequential steps enabled                                    | 20     | ¢ 0.97 | ❌ Just wrote a list of sci-fi technobabble definitions for a story.. which in a way is pretty on brand.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Brief course on Biology                                                     | 60     | ¢ 2.3  | ✅ Pretty excellent by and large didn't repeat itself. Gave a comprehensive overview of the subject.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |

Pricing appears to be wrong though the Three Body Problem inspired story was rather short all in all so it's not 
*entirely* implausible yet? It's okay, it's just affordable.

// May be better off wrapping writeWorkflow into writePages, use the 4 types: chat, write, for each and loop for more advanced more specific workflows: e.g. narrative.



#### Conclusion

Educational topics work very well in the Write pages workflow, giving a full comprehensive coverage of the topic at hand and responding well to the given length, from the samples I've read a consistent idea of begining middle and end is maintained.
Stories on the other hand are terrible. The actual writing isn't very good and even with time and money expensive sequential page writing coherency is poor.

This does point to the idea that different types of request need or would benefit from being handled differently. Theres not really any reason to add sequential processing to an educational document.
Sure it would be neat if the document referred to prior content "Remember when I said this", "Now don't get confused with this, x is different". But the extra possiblity for confusing the LLM alone isn't worth it.

Thankfully, writing stories is just a fun novelty idea to me -in a way it's reassuring it's still quite hard for AI at the moment.


## Loop Workflow

### Loop Workflow manual testing

| Task                            | Loops          | Cost   | Review                                                                                                                                                                                            |
|---------------------------------|----------------|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Write a cover letter            | None           | ¢ 0.04 | A little dry, it's fine, but it's a little on the nose. If I raed this cover letter my first thought would be 'bullshit'                                                                          |
| Write a cover letter            | 2              | ¢ 0.18 | More substantial, this feels more like someone who knows how to talk the lingo. Intro grabs attention though still a bit fake. Better focus on personality and soft skills as well as core values | (Pretty drastic increase in cost, write for example with the planning stage is only 8 percent of a cent
| Write a cover letter            | 3              | ¢ 0.27 | Very similar to 2 loops but a bit worse                                                                                                                                                           |
| Write a cover letter            | 4              | ¢ 0.38 | Tells the user more often to put in their own details, which leads to a less compelling letter, but is more appropriate. Hard to say if I like it more than 2.                                    |
| Write a cover letter            | 5              | ¢ 0.51 | Worse I feel, not as bad as the no loops answer but of a similar spirit.                                                                                                                          |
| Make a neat loading screen (o3) | None           | ¢ 1.64 | Pretty bad, completely eradicates the existing animation making it a still expanding and contracting image)                                                                                       |
| Make a neat loading screen (o3) | 2              | ¢ 4.83 | Pretty good actually, not exactly what I would do but it gives me a foundation to edit: creates a 1 second animation of the                                                                       |
| Make a neat loading screen (o3) | 5              | ¢ 7.38 | Decent, adds a pulse animation which is neat but not quite what I have in mind, the 2 loop procedure is easier to use                                                                             |
| Make a neat loading screen (o3) | None           | ¢ 1.12 | Just a pulse, not very good.                                                                                                                                                                      |
| Feature planning (o3)           | None           | ¢ 0.63 | Decent, had to be told not to regurgitate my ideas -and it basically still is but it provides valid points.                                                                                       |
| Feature planning (o3)           | 2              | ¢ 1.96 | Modular personas - that's a *really* good idea actually. Enables user generated personas'                                                                                                         |
| Feature planning (o3)           | 5              | ¢ 4.15 | Much the same                                                                                                                                                                                     |
| Self-Improvement (o3)           | 2 (+Best of 2) | ¢ 5.33 | Pretty good, checking the loops I'm not really sure it made much of a difference.                                                                                                                 |

### Loops vs Best of

| Task                                      | Loops | Best of | Commentary                                                                                                                                                                                   |
|-------------------------------------------|-------|---------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Fix loading screen orientation (o3)       | 2 ✔   | 2 ✅     | (gemini is terrible at this, Loops.. isn't bad but it's just not quite right, but it is better. Best of provides a near identical solution but is clearer and is much simpler, as requested. |
| Fix tooltips on mobile (o3)               | -     | -       | Actually nevermind, this might be something to look at in future for more novice users, but it's actually completely possible to just tap off tooltips or the tooltip itself.                |
| Explain software design patterns (o3)     | ❌     | ✅       | (Well best of actually uses code blocks correctly so easy win, loop meanwhile messes with them till they break)                                                                              |
| Write about Rome, compelling              | ✔     | ✅       | (best of is just a little bit more compelling and a little more coherent positing the idea that inequality lead to the corruption and ultimate destruction of Rome. A theory.                |
| Write about superconductivity, compelling | ✔     | ✅       | (Best of mentions Bosons so it would win automatically anyway if it wasn't more clearly written)                                                                                             |

Updating the loop system message to make it clearer that it needs to *improve* upon prior messages

| Task                                   | Loops | Best of | Commentary                                                                                                                                                                                              |
|----------------------------------------|-------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Explain software design patterns (o3)  | 2 ✔   | 2 ✔     | Now everything seems to have difficulty formatting code blocks correctly, but the loop answer does seem better than before                                                                              |
| Write about Rome, compelling           | 5 ✅   | 5 ✅     | *technically* I think best of is better as it explains more unexplained references and has less odd sentences, but not that much the two are *very* similar in structure, down to the actual words used |
| Modularise BasePersona System          | 5 ❌   | 5 -     | (200s @ ¢ 1.74 vs 50s @ ¢ 1.34) Loops looses the track and takes credit for files I gave it. Best of solutions pretty poor but it at least IS a something vaguely resembling a solution                 |
| Modularise BasePersona System (o3)     | 5 ✔   | 5 ✔     | I'm going to say both are good. Best of has a slightly nicer conclusion (still echoing the same points), but loop actually formatted it's code successfully                                             |
| Improve workflows.py, consistency (o3) | 2 ✔   | 2 ❌     | Best of failed to format, 2 loops produces a longer (less optimised) file than 5.                                                                                                                       |
| Improve workflows.py, consistency (o3) | 5 ✅   | 5 ❌     | Best of failed to format (what is going on with the code formatting lately??)                                                                                                                           |

I had to tell the AI not to regurgitate points, that might be good to include in the writer persona or an analyst persona.

I want to point out that this entire exercise in speed running has best by me going "okay lets get a real problem my project faces, those are the problems I'm most interested in and can judge the most acutely"
Followed by me working on a solution a couple of hours each.


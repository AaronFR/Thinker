### 0.3.0

Type of test: Report generation

### Thinker Outputs:

    - "Write a comprehensive history of video gaming and do it in het nederlands" -> geschiedenis_van_videogames.md

Answers where reviewed among the following metrics
    - Quality
    - Clarity
    - Completeness
    - Accuracy
    - Engagement
    - Relevance to the initial prompt

The same question was put to the ChatGpt website (ChatGpt 4o) and then the two reports where compared on these metrics on two new fresh chat messages.
ChatGpt is asked to review each rating on a 0 to 5-star basis (because I don't trust it to reliably generate the same percentage for the same input)

### Test 1: Video Game History report in Dutch

I'm trying to learn dutch, heh.

#### Thinker results (geschiedenis_van_videogames.md)

- Quality: ★★★★☆
- Clarity: ★★★★☆
- Completeness: ★★★★★
- Accuracy: ★★★★★
- Engagement: ★★★☆☆
- Relevance to the Initial Prompt: ★★★★★

#### General Thoughts on the Response Overall

The response provides a detailed and accurate history of video games, covering significant milestones, technological advancements, and cultural impacts. It is clear and well-structured, making it easy for readers to follow. However, it could benefit from a more engaging writing style to capture the reader's interest more effectively. Overall, it is a high-quality response that meets the requirements of the prompt comprehensively.

#### ChatGpt.com results (1.md)

Quality: 4.5 stars
Clarity: 4.5 stars
Completeness: 5 stars
Accuracy: 4.5 stars
Engagement: 4 stars
Relevance to the initial prompt: 5 stars

The response is highly relevant, addressing the prompt directly by providing a comprehensive history of video games in Dutch.

### Differential between the two

- Quality: -0.5
- Clarity: -0.5
- Completeness: 0
- Accuracy: +0.5
- Engagement: -1
- Relevance to the Initial Prompt: 0

### My observations

The Thinker output suffers from being obviously stitched together, having 6 separate conclusions and invalid markdown chapter formatting.
Lots of information is repeated or otherwise gone over again, and as a whole the document does not form a coherent whole in my estimation.
Thinkers primary advantage is the *quantity* of information it can output at once

### Test 2: Video Game History report in Dutch #2

Repeated test, with UserInterface operated twice, for a total of 10 iteration steps. 2nd Run is notably slower with more and more tasks to run on the larger and larger input file.
Cost $0.04

#### Thinker results (geschiedenis_van_videospellen.txt):

Quality: ★★★★☆
Clarity: ★★★★☆
Completeness: ★★★★☆
Accuracy: ★★★★★
Engagement: ★★★☆☆
Coherency of the Document Overall: ★★★★☆
Relevance to the Initial Prompt: ★★★★★
The response is highly relevant, providing a comprehensive history of video gaming in Dutch as requested.

#### ChatGpt.com results (2.md)

Quality: ★★★★★
Clarity: ★★★★★
Completeness: ★★★★★
Accuracy: ★★★★★
Engagement: ★★★★★
Coherency of the Document Overall: ★★★★★
Relevance to the Initial Prompt: ★★★★★

### Differential between the two

Quality: -1
Clarity: -1
Completeness: -1
Accuracy: 0
Engagement: -2
Coherency of the Document Overall: -1
Relevance to the Initial Prompt: 0

### My observations

Similar lack of coherent formatting and purpose, with one list 'Belangrijke Mijlpalen in de Gaminggeschiedenis' repeated in various ways 4 times over.
The system could benefit from a more coherent initial vision of how it thinks the task could be solved

## Final Notes

The primary advantage of the Thinkers output is the *bulk* of its output, most general topics related to the initial question are covered.
It's just a question of finding them within a coherently written solution that's the issue.

Improving coherency is a challenge. The current system is based solely on an iterative 2-step loop. First the executive evaluates the current state of the solution and creates a set of tasks to improve the solution.
Then the executor's works on individual tasks. Its modular and flexible but is problematically suggesting the same/similar improvements over and over.

While some 'un-biased' review has value, when the consistency issue is fixed eventually the current metrics should quickly become irrelevant.

Ideas:

- **Additional evaluation layer**:
At the start or the end of the current 2-step process, however it could be as simple as a single initial plan that the executive processes try and follow created at the start of the application.
but simply there's just no guarantee that the task processors will actually take this plan into consideration.
If implemented at the end, the process could evaluate the output and see if this is an improvement, I seriously do not want to do this. This means for an executive process that suggests only a single task, 2/3rds of a given iteration
would be spent *evaluating* instead of 'thinking', it's akin to when a human overthinks something their not confident about doing.
  - **Evaluation reports**: For each executive stage. Actual comprehensive reports that could be referred to along the way, reporting strengths/weaknesses, areas of improvement
  - **Incremental Learning Guidelines** The system can be triggered to review itself automatically for a certain prompt/process and make its own suggestions for reviewing and improving the set of guidelines(system and user messages) it follows
- **Primary area of concern**: Change to the executive-executor process: Instead of listing many areas of concern the executive model could list a *primary* area of concern which **should** differ from iteration to iteration. At least prioritise the list of suggested improvements
- **Role based processing**: Defining such roles on the fly when the given problem could be *anything* is difficult to conceptualise.
  (refer to <https://arxiv.org/html/2405.11804v1#S4>)
  - Modular executive systems and module executors in line with the role model. So for instance at the start of a user prompt, the executive is a planner who is focused on creating a plan of action, the executor is an assistant and writes out said plans and furnishes them with details and considerations.
      middle stages would consist of BA's/Developers referring the current solution against a planned document, and final stages would consist of editors marking areas of refinement and implementing these changes.
- **File summarisation**: File summarisation, could be used to simultaneously highlight areas of improvement.
- **Task Lists**: Creating an actual task list data object which is ticket off item by item.
Instead of an iterative: (what do you see, how can it be improved -> improve the contents in this way) approach, it could be based of an actual series of task objectives, ticking one off until the solution is achieved.
- **Coherence Templates**: So if outputting a report, follow a specific report-template. Could seriously interfere with the flexibility but for common tasks such short hands make some sense, just like how a real brain uses shorthands for tasks its familiar with
- **Refine the process_logs**: If it where made clearer to the application, what occurred why it occurred and whats still left to do it would help.
    In general the system is too generic currently, it only really evaluates at each step the most generic steps, more complicated thinking e.g. structuring, style, coherence, do not occur, but then that's the point of a flexible system.

(For the record when asked to review these notes, The Thinker was capable of *actually* providing novel, interesting ideas I hadn't considered for the same prompt -despite running on the 'weaker' model)

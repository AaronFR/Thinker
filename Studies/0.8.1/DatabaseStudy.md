# Database Study

## User Encyclopedia and Encyclopedia prototypes

Already the system has tried to contextual data on the user in a simple yaml file with very mixed results

There are a series of useful entries which in theory could be quieried to provide additonal context

"occupation": |-
  User works as a Backend Software Developer.
"project": |-
  User is coding a ChatGPT Wrapper hobby project called 'The Thinker'.
...
"watchlater.csv": |-
  A file containing a list of videos or media to watch later, which can be organized by priority on a scale from 1 to 4, where 1 indicates the highest priority and 4 indicates the lowest.
"leisure_watchlater.csv": |-
  A CSV file that organizes leisure activities or media to be watched later, which includes a priority value for each item ranked from 1 to 4.
...
"communication style": |-
  The user seems to prefer verbose or elaborate communication.
...
"priority scale": |-
  A system for ranking items based on their importance or urgency, ranging from 1 (highest priority) to 4 (lowest priority).
...
"user/communication_style": |-
  User has a casual and humorous communication style, as indicated by the phrase 'Whats up doc?'.
"user/react_expertise_level": |-
  User may have a certain level of expertise or interest in React, which could be explored further.

Others however are plainly not useful

"architectural work level": |-
  High amount of architectural work completed.
(Note: For what work?)
...
"string contents": |-
  The textual information associated with each variable name, which can be enhanced or expanded to provide more contextual clues and clearer intentions for their use.
(Note: This is general knowledge not really user knowledge)
...
"user/request": |-
  User has requested to rewrite AiOrchestrator.py and ChatGptWrapper.py for improved documentation.
(Note: Too specific to reserve the term 'request')
...
"user/filenamepreference": |-
  User prefers to name files as file_a.txt and file_b.txt.
(Note: 😑)

However upon closer inspection actually I can see that most entries extract *something* of *some* value

 152 entries (at time of writing)

 59 / 152, ~40% relevant (nevermind a lot are duplicates), (62 / 152 , AI estimate)

 63 / 152, ~40%  duplicated:

    - User knows python: 17 (my estimate), 11 (ai estimate)
    - React Expertise & Frontend Knowledge: 7 (my estimate), 13 (ai estimate)
    - Encyclopedia Management Classes: 9 (this andd the rest are ai)
    - Commit Message Format & Practices: 5
    - Error Handling Preferences: 4
    - Neo4j Knowledge & Interests: 6
    - Project Focus and Goals: 7
    - Daily Schedule & Time Blocking: 5
    - Watchlater & Leisure Prioritization: 6
20 / 152, ~20% Irrelevant/Unfocused

### Conclusion

Now both the key problems: duplicated and Irrelevant/Unfocused entries can be eased by requiring a tighter focus on relationship:
What has, what relation to what concept, which will need to be instantiated as part of addapting creation of user context to a
graph database anyway.

Key points:

- ensure the graph database system has some notion of common terminology and methodology, minimise duplicates and semantic copies
- Configure the ai to think in terms of relationships, the USER -KNOWS- PYTHON, the USER -ASKED- the AI to -IMPROVE- FILE_A,
 USER has a -INTEREST- in PHILOSOPHY, USER has -EXPERIENCE- in
- There must be a system for searching, updating and delting entries
- Keyword detection
- Add a contextual prioritisation, e.g. 'WORKING_ON' gets high priority, 'WORKED_ON' gets low
- Generate summaries and insights based on the graph

## Initial Node efforts

### First data set

- **language learning**  
  - Language: Dutch
- **current proficiency**  
  - Proficiency: Medium
- **study duration**  
  - Study Hours: 200 hours
- **interest topics**  
  - Interest: Daily life
- **word type preference**  
  - Word Type: Adjectives
- **state**  
  - Capital: Sacramento
- **vocabulary level**  
  - Level: Advanced
- **interests**  
  - Programming Language: Python
- **interest**  
  - Topic: Philosophy of history  
  - Cities: Key cities in California
- **language**  
  - Spoken: Spanish
- **unknown**
- **Python**
- **text_format**  
  - Type: XML
- **data_extraction**  
  - Type: String manipulation
- **database**  
  - Type: Neo4j
- **application**  
  - Complexity: 20 Python classes
- **circular_dependencies**  
  - Issue: Experiencing circular dependencies in the application structure
- **solution_attempts**  
  - Approach: Attempted to separate high and low-level classes to manage dependencies
- **dutch proficiency**  
  - Level: Medium, about 200 hours of learning
- **example preference**  
  - Language: Both English and Dutch
- **learning resources**  
  - Type: Looking for practice exercises in addition to overview
- **language_learning**  
  - Clarification Request: User seeks clarification on related terms like independent clauses  
  - Interests: User is interested in language learning
- **Location**  
  - Workplace: Disney World Paris
- **programming language**  
  - Name: React
- **unknown**
- **job**  
  - Occupation: Unknown  
  - Title: Unknown  
  - Type: Unknown
- **location**  
  - City: San Francisco  
  - Type: Unknown
- **favorite_food**  
  - Ice Cream: Peach
- **name**  
  - Last: Bobalicous Sr  
  - First: Jope
- **User's name is not provided**
- **communicationpreference**  
  - Type: Formal email
- **Occupation**  
  - Job Title: Test tube cleaner
- **careeraspect**  
  - Request Type: Raise  

Irrelevant: 14 / 33 -> 42% 

A few things pop out right away, principally is the saving of 'unknown data', remembering that we don't know something is
good conceptually, but not with this degree of non-specificity: theres an infinite amount of things the program *doesn't* know.

Secondly many nodes are not relevant or contextual. ``Study duration`` doesn't mean anything outside of the context (which *was*
'how many hours have I studied dutch')

## Second data set

After modifying user topic generation to reason step by step the same way categorisation is now reasoned through (in theory)

- **learning_context**  
  - Role: Possible student or learner
- **information_seeking**  
  - Comfort Level: Comfortable asking questions for information
- **personal_info**  
  - Context Awareness: Understands the importance of context in communication  
  - Location: Albany  
  - Economic Interest: Economic production
- **not specified**
- **user_open_to_suggestions**  
  - Interaction Style: Open to suggestions or recommendations
- **user_interest_in_insights**  
  - Inquisitive Nature: Values additional insights about a topic or query
- **project_structure**  
  - Framework: Familiarity with Flask web framework  
  - Scope: Willingness to build a large-scale application with clean architectural principles  
  - Language: Knowledge in Python programming  
  - API Integration: Interest in integrating with AI APIs (e.g., ChatGPT)  
  - Architecture: App designed with Flask as a backend for ChatGPT API, focusing on modularity and separation of concerns
- **user_interest**  
  - Event Type: Political
- **user_depth**  
  - Implication Depth: Simplified
- **user_comparison**  
  - Comparison Scope: General
- **math_skill**  
  - Understanding: Basic mathematics knowledge
- **python_experience**  
  - Level of Interest: Intermediate  
  - Skill Improvement: Learning new techniques
- **async_programming**  
  - Project Type: Concurrent Tasks
- **developer_type**  
  - Backend: The user is a backend developer
- **programming_language_experience**  
  - Python: Experienced  
  - Java: Experienced  
  - JavaScript: Beginner
- **goal**  
  - Full Stack: Aims to become a full-stack developer
- **user_name**  
  - Full Name: John Jermiah Johanson
- **user_profession**  
  - Profession: Accountant
- **user_location**  
  - Location: Berkshire  

Irrelevant : 6 / 19 => 31%

## 3rd Set

Mostly running "what is 2 + 2?" questions while testing

- user_name 
  - first_last: Carnie McCorn
- user_location
  - state: Iowa
- user_context
  - familiarity: You are seeking familiarity and personal connection in conversations.
  - continuity: You are interested in establishing continuity in dialogue.
- arithmetic
  - addition: User is interested in basic arithmetic problems.
- learning_language
  - language: Dutch
- interest_area
  - area: Colloquialisms
- cultural_context
  - context: Netherlands
- language_learning
  - slang_words: 50 additional Dutch slang words can enhance your understanding and usage of informal Dutch language, enriching your cultural interaction and communication.
- personal_interest
  - interest: mathematics
- personal_learning_stage
  - level: beginner or intermediate
- personal_skills
  - skills: problem-solving
- personal_context
  - reason: May be performing calculations for academic purposes
  - programming_language: Java
  - interest: Interest in mathematics
  - mathematical_concept: Pi Calculation
  - algorithm_knowledge: Bailey-Borwein-Plouffe
  - interest_level: High
  - status: Possibly a student or someone studying mathematics
- interest
  - mathematics: The user has an interest in mathematical calculations.
  - knowledge: The user is seeking knowledge and understanding.
- need
  - numerical_calculations: User may need assistance with numerical problems.
- study
  - exam_preparation: User might be studying for a math-related exam.
- skill
  - arithmetic: The user likely has basic arithmetic skills.
- math_context
  - interest: user is interested in mathematics or calculations
- interest_in_math
  - interest: User is engaged with mathematical calculations.
- learning_environment
  - setting: User might be in an educational or academic setting.
- inquiry_for_knowledge
  - curiosity: User appears to seek clarity or knowledge regarding number calculations.
- slang_terms
  - slang_list: <Dutch slang terms I didn't read one of which is probably VERY insulting> 
- coding_interest
  - Programming_Language: C
- precision_focus
  - Calculation_Requirement: High accuracy for pi
- background_interest
  - Field: Mathematics or Science
- user_interest
  - style_preference: informal
  - language_interest: Dutch
  - slang_focus: insults

Irrelevant 7 / 25 => 28%
<h1 align="center">
    <a href="https://thethinkerai.com/">
        <img src="FrontEnd/public/ThinkerLogo.png" style="width:280px; height:auto;" alt="ThinkerAI Logo">
    </a>
</h1>

# The Thinker

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

🚧 PUBLIC BETA 🚧

1. [Features](#features)
2. [Planned](#planned)
3. [Roadmap](#roadmap)

The Thinker AI, is designed as an open source wrapper for interacting with publicly available LLM (Large Language Model) 
APIs on a pay-as-you basis, i.e. *without* a monthly subscription.

As well as being fair, this pricing model enables arbitrarily powerful workflows and features, without limit or quota.


## Features

While improving upon base models is foundationally important, this wrapper exists to provide many additional features to
get the most out of your prompt.

- **Arbitrary Scale**: Generate files 1 response long, 10 responses, 100 responses.. If you have files that you want to edit, 
  review or otherwise rewrite, you don't have to prompt them one by one, send in all of them at once against your prompt.
- **Prompt Improvement**: Options for automatically re-writing or questioning the user prompt in advance.
- **Reference**: Save, generate and reference files and messages, search the internet, save and reference user context. To help the
  AI get as much useful information as possible.
- **Categorisation**: Use different personas tailored for different topics, have your messages and files automatically 
 categorised for later reference
- **Response Improvement**: Options to generate multiple responses in sequence and have the AI select the best one. Loop 
  over answers, letting the AI iterate and improve it's response

## Planned

Some of the features planned for the next few releases..

### Functionality

- **Payment System**: If there's interest we'll start allowing user's to top up their balances.
- **Personas**: Fully fleshing out the feature, e.g. "Teacher", "Curator", etc
- **Workflows**: Changing workflows to be specific and targetted, e.g. "Check news", "Suggest System Architecture", "Plan holiday", etc, etc.
- **Temperature**: Change model temperature (randomness)
- **Deepseek R1**
- **Claude**:
  - Given its price and recent advances by Gemini this will be a post-beta feature.
- **Reference/File message optimisation**: Optimised in regard to the prompt referencing them, this could both minimise
  confusion when using a lot of reference material and also serve as basically a 2nd step in the 'thought process' of responding
  to a given prompt
- **Guide to running locally**: It's possible if you setup the necessary accounts and update your env vars accordinly, but there isn't an explict guide setup. If you *are* interested, message me first and I'll guide you through the process myself.

### UI

- **QOL**:
  - 'Delete selected items' button
  - 'Delete category' button
  - 'Rename category'
  - Ability to undo changes to files


## Roadmap

Depends on their being sufficient interest in the project, but there are many ways the project's utility can be enhanced.
Some notable ideas:

- Specific Workflows: The current workflow system is a baseline, more specific workflows need to be created with precise
  plans defined in advance. E.g. the process for planning out a project architecture is different to the process of debugging
- More Personas: To make the most out of the system multiple options for various kinds of speciality or topic area need 
  to be defined.
  - Intelligent personas: Personas that are 'aware' of their history of the user and preferences, on what works for 
    certain problems.
- Context refinement: Internet search and user context retrival are awfully slow. The same way categorisation and workflows
  are front-loaded to the front end (while they can be defined in the backend if needed). Defining and presenting sites
  and retrieved user context would improve speeds and show users in detail what exactly the system is doing.
- Quick-settings: Turning internet search on and off should be an option in the prompting window for instance. It 
  doesn't need to run for every prompt.
- Privacy: Currently user messages are not encrypted. While this is planned the present reasoning is that the only API's
  available are corporate API's that explicitly say they will use your data for training (or cannot be trusted otherwise).
  Saying that we encrypt your data, while it needs to be sent to these 3rd-parties is **false privacy**
  - The option will be added after running our own or a truly private LLM api. If this is a game breaker please get in 
    contact



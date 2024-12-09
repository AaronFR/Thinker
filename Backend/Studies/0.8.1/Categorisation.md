# Categorisation Study

## Test Prompts for regular llm api call

versus function schema call

- 😴 : The full output of the llm's step by step reasoning for why its categorising the input data as it is
- 🙀 : The derived categorisation

### Prompt "What is 2 + 2?"

```Powershell
😴, In the provided prompt-response pair, the user's question is a mathematical one, specifically asking for the mathematical operation of squaring the number 22. The response correctly provides the result of that operation.

While the categories provided include 'geography' and 'personal,' neither fits well as the content of the prompt and response pertains to mathematics rather than a geographical topic or a personal inquiry. However, since the context is educational in nature pertaining to mathematics, it hints towards a personal inquiry about knowledge or learning.

After considering these factors, the most appropriate categorization for the interaction could be seen as 'personal', as the question seems to reflect an individual's curiosity or need for mathematical information.

Thus, I will categorize the data as follows:

<result="personal">
🙀, personal
```

🙃

-> "LIGHTLY suggested existing categories, you DONT need to follow:"...

### Prompt "What is the most interesting event of the 6th Century?"

```Python
😴, <result="history">
🙀, history
```

*I mean, you can't deny the efficiency*

### Prompt "I'm having some issues with my python/flask database, I'm running into circular dependencies more and more, what are you suggestions?"

```Python
😴, <result="programming">
🙀, programming
```

What was I doing going to call this the 'expensive method', this is laser focused

### Prompt "What are some of the 50 most important terms in react programming?"

```Python
Dito
```

### Prompt "Can you give me a suggestion for something to do?" (uploaded: tasks_list.txt)

```Python
😴, <result="personal">
🙀, personal
```

I'm actually rather fascinated now, is there some hidden processing in ChatGpt 4o-mini?
I mean I actually did ask specifically for the reasoning steps and I'm not getting them.

### Prompt "Give me 50 words of dutch to learn" (Plus QA specifying I mean advanced adjectives)

```Python
😴, <result="language">
🙀, language
```

## Stress testing

### Prompt "What is-uh, uhm ...hm.............. uhm so the thing with the where in the hey"
Nonsense prompt to test how it deals with the un-categorisable

```Powershell
😴, The user prompt is vague and lacks a specific question or context. The 
response acknowledges the lack of clarity and asks for more information. This exchange is focused on communication and understanding 
the user's needs.

Given this reasoning, I would categorize the interaction under "personal" as it relates to direct, individual communication and understanding.

<result="personal">
🙀, personal
```

That's fair

### Prompt "Hey can you discuss the history of philosophy?"
There is an existing 'History' *and* 'Philosophy' category

```Python
😴, <result="philosophy">
🙀, philosophy
```

Okay I suppose I get that

### Prompt "Hey can you discuss the philosophy of history?"

```Python
 😴, <result="philosophy">
🙀, philosophy
```

Right of course, its a shame there's no reasoning steps like I asked for but seeing as philosophy is more niche than history
.. at leastt I think it is? It makes sense to preference the more niche subject. But who knows.

### Prompt "Can you describe a python class for calculating e to a given arbitrary level of precision?"
There is already an existing 'Mathematics' and 'Programming' category

```Python
😴, <result="programming">
🙀, programming
```

I'm happy with these decision though *eventually* there will be conflicts which lead to some user dissatisfaction.
The ability to change not just the current prompts category 
(which is very easy: just tell it "please categorise this as X")
But a prior category the user believes is miss categorised may be helpful, it may also be rather annoying if error prone

## Conclusion

There's not even any point giving an option in the settings between 'expensive categorisations' and cheap ones, this is 
plainly the superior prompt.

It's not just falling into the 'personal' or 'information' category black holes the last one did.

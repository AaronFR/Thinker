User prompt: "What is my name?"

Fascinatingly with the encyclopedia system added the System is basically already asking for n-shot examples 
before answering a given question:
```
Function evaluated with response {'terms': [
    {'term': 'insightful response', 'specifics': 'examples of insightful responses in literature or communication'},
    {'term': 'fascinating response', 'specifics': 'what makes a response fascinating in a discussion or debate'},
    {'term': 'educated response', 'specifics': 'how to formulate an educated response in intellectual conversations'},
    {'term': 'name_query.txt', 'specifics': "context and contents of the file 'name_query.txt'"}
]}
```
It is also looking for file that would already answer this question, which is incorrect and suggests a possible conflict
for where the program should be looking for information.
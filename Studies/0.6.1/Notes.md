### User prompt: "What is my name?"

Fascinatingly with the encyclopedia system added the System is basically already asking for n-shot examples 
before answering a given question:
```Python
#Function evaluated with response:
terms = {'terms': [
    {'term': 'insightful response', 'specifics': 'examples of insightful responses in literature or communication'},
    {'term': 'fascinating response', 'specifics': 'what makes a response fascinating in a discussion or debate'},
    {'term': 'educated response', 'specifics': 'how to formulate an educated response in intellectual conversations'},
    {'term': 'name_query.txt', 'specifics': "context and contents of the file 'name_query.txt'"}
]}
```
It is also looking for file that would already answer this question, which is incorrect and suggests a possible conflict
for where the program should be looking for information.

### User prompt: Improve the flow of this [Class] while reducing redundancy

```commandline
2024-09-10 09:59:08,279 [WARNING] (WikipediaApi.py:69) No page found for 'python coding standards'.
...
2024-09-10 09:59:09,309 [WARNING] (WikipediaApi.py:69) No page found for 'best practices in python programming'.
...
2024-09-10 09:59:10,811 [WARNING] (WikipediaApi.py:69) No page found for 'pep 8 guidelines'.
...
2024-09-10 09:59:11,829 [WARNING] (WikipediaApi.py:69) No page found for 'code readability practices'.
...
2024-09-10 09:59:12,795 [WARNING] (WikipediaApi.py:69) No page found for 'error handling in python'.
...
2024-09-10 09:59:13,771 [WARNING] (WikipediaApi.py:69) No page found for 'unit testing in python'.
```

It's fascinating to see how the application ""wants"" specific technical instructions related to its job. This could be
an opportunity for adding in more technical information in a more configurable in depth way than the configuration files,
but we would need to be wary of conflicts/redundancy.
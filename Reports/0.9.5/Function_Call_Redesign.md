# The issues with function calls

With the introduction of gemini models and after adding the ability to use them for background processing in The Thinker (important because
gemini flash-lite can be an order of magnitude cheaper than even gpt-4o-mini) the way 'function' calls are processed 
needs to be reconsidered.

Function calls at least in the OpenAI way of doing things are a way of processing a user prompt with a provided schema 
in order to try and guarantee a certain result, I utilised them early on as they did indeed appear to be an easy way of
improving (Not guaranteeing!) A response would follow a provided schema

The problem back then is that schema's are long, and your costed for them. For simple queries the schema can be as many
tokens as the request itself - doubling input costs, typically that's not so bad output is much more
expensive, the problem is (again in the OpenAI method) the output HAS to be given as json 
object and then you get the properties you actually want, this is *another* layer of expense.

But it IS possible to get LLMs to produce content reliably if sufficiently simple (I also swear all models have become
more reliable at this exact task over the last 8 months since I've started working, but I have no data to back that up.)
For instance if you ask an ai to output a single word it will usually succeed but sometimes fail, by referencing its 
answer with something like
```
Sure, okay! Here's my answer
```

In that case though you can provide a structure you can then extract. For instance specifying that all answer must be 
inside tag elements ```<tag_name>answer</tag_name>``` and then regex selecting for these defined elements actually works
great, I already use this for selecting categories for instance.
```
<result>category_name</result>
```
This also allows the AI to actually do some basic reasoning before just jumping to a solution.

- Compatibility issues between AI providers
  - Lock in
- Significant increase in input expenses
- Moderate increase in output expenses
- Inability to reason through outputs before just stating them

## Existing functional-replacements

The next thing that needs to be done is create a more unified way of getting prompts to emit structured responses and 
processing that structure

Existing uses:
- CategoryManagement.py/categorise_prompt_input 

Function calls to replace:
- EncyclopediaManagementInterface.py/search_encyclopedia
- Writing.py/determine_files


encyclopediaManagementInterface.PY

(Needs a refactor, the prior 'encyclopedia' system is just a no go, why try and create a database of concepts when the 
internet exists?)
```
{'terms': [{'term': 'project', 'specifics': 'details'}, {'term': 'project', 'specifics': 'goals'}, {'term': 'project', 'specifics': 'timeline'}]}
```
->
```
[{"term": "project", "specifics": "details"}, {"term": "current work"}, {"term": "objectives"}, {"term": "scope"}, {"term": "timeline"}]
```

So by switching to structuring and regex searching responses we can cut off that 'terms' part which de-complicates things


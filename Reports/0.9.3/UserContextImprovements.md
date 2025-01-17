# User Context

Currently of some use, the hello world of this functionality is that you can tell the application your name -
and it will remember it or rather it COULD remember it later on.

However currently the storing of information is too scattershot and there is too much marginal information being included
(refer to prior reports on memory)

## Iteration 1 - User Context Management knows about existing nodes

This is pretty obvious, I was scarred about costs but for o4-mini processing these kind of prompts is percents of cents 
so it's not really a big worry if your preventing the creation of nodes and improving memory coherency.
I won't include the prior USER_TOPIC node records for fear of bloat and having to screen the data, but there are 51 nodes.
Those nodes can contain one singular arbitrary data point or loads are crammed into a not wholly representative node
We'll see to what total of nodes

Just by changing the existing system prompt to describe its self by role "You are a .." and giving a unobtrusive example 
the amount of grouping can be improved.

Definitely a use case for including a description in a context node, I saw the programming trying to process "Do you know my name"
It looks in its memory. sees ['project', 'profession', 'personal'] and picks 'project'.
personal is a fine name for a user information node, but you can see how that's not intuitive.

Meanwhile, you ask it, "do you know the name of the *project* I'm working on and what it does" and it knows; it can select from
memory.
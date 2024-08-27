#ToDo: Documents which are themeselves are a powerful way of instructing the AI to follow tasks,
# but for now we will avoid this until we can trigger it more deliberately
SUMMARISER_SYSTEM_INSTRUCTIONS = """Take the file input and summarise it in a few lines.
Note what the file is, what its category is, notable features.

Finally add a index of the files various parts chapters/functions etc, structurally summarising the document"""
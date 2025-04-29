# Manual Testing Before Open Beta

I really need to move these entries to a blog after..

## Contents

I'll evaluate a series of questions and see what the result is, if the site is ready: Professional, bug and glitch free,
functioning as intended.

### Abuse Mitigation

[REDACTED]

I'm not publishing information on what security concerns I have and my efforts to mitigate them. 🙂

### Workflows

1. ✅ Does the chat workflow work as expected
    Sort of: There is a clear 'reasoning' section which should be displayed differently.. but it's fine?
2. ✅ How much faster is deployed over local builds?
    Depends. 2-second difference max, but deployed can be slower for long jobs
3. ✅ What's the speed with no functionality enabled versus max?
    Massive, 3.5x - 4x, you can't have all functionality enabled, all the time
4. ✅Does best of work on Gemini Models
    Appears to. 

#### Does write pages work as expected

It's not outputting files or displaying them in the files section. Files section has been empty for a while actually.

...It's the *exact* same problem as categories not being saved in time. The Application is working faster than the database
this time said database is s3, so I don't need to worry about neo4j possibly being slow.

Solution is to create file nodes the moment a file is created:

Current flow:

```Workflow (WriteWorkflow)
save_file_step() -> produces content via LLM call
->  s3Manager.save_file() -> Saves the file content in an appropriate s3 folder (which can confirm)
process_message_ws() -> Near the end tries to create files for the given user prompt by checking the working area (staged files)
s3Manager.list_staged_files -> []
  The database hasn't made the files available yet
  -> No file nodes are created
  ==> user cannot access file content or see response
```

Suggested change:

```
Workflow(WriteWorkflow for e.g.)
save_file_step -> produces content via LLM call
->  s3Manager.save_file() -> Saves the file content as before
->  nodeDB.create_file_node() -> Immediately saves file node representation (also allows file size to be saved against node)
```

##### Replacing staging-directory approach

Staging based approach replaced with immediate file save in node and in files via Organising.save_file, cleaner, less 
error-prone, faster when running the save_file_step in threads and you know, it actually works again now.

##### So does it work as expected?

Well it doesn't in fact save files, which is a bit of a problem. After switching to use the new node/s3 organising.save_file
method and emitting the file id for the frontend it's picked up correctly.

5. Does loop pages work as expected?

(gemini-2.0)
Well they do in fact work, simple requests to make stories 'compelling' and briefer actually makes them more and more 
nonsensenscial with each iteration.
When working on coding problems it at least doesn't degrade

Seems to think it's talking about coding problems even on writer?'
Probably because your ENHANCEMENT_QUALITIES specifically talk about 'the code' and talk about improving it like code.
You might want to optionally disable that.

Disabling that, and giving it a specific difficult to convince objective, the response went from well considered but vague 
and inapplicable to specific and exacting the stated steps making key sense. 

### Request

1. ✅ What happens if I try to reference a deleted message or file?
   It crashes, but that's not possible anymore.. unless you delete a referenced file (refactor code)
2. ✅ What happens if I try to upload a non-supported file type? (pdf, image...)
    It fails to upload, error during decode(): `'utf-8' codec can't decode byte 0xd3 in position 10: invalid continuation byte`


### Pricing

1. ✅ Does earmarking work as expected?
    Testing appears to suggest so, the initial user earmarked balance is usually zero'd out correctly for each request, while 
    non-zero mid-workflow. Occasionally it can produce a floating point error e.g. '-4.336808689942018e-19' but this simply
    isn't significant. 
2. ✅ Are open AI prices correct?
    Well I get the costs from the API directly based on the current up to date prices, so yeah
3. ✅ Are Gemini prices correct?
  Dito
4. ✅ Are message and functionality prices correct? Sure appear to be, will need heavier traffic to spot any discrepancies.

### Quality and Value

1. ✅ Are responses naturalistic and enjoyable to read 
   After changes to the Writer's system message: It's better, limits it's output but I personally prefer it to the cringe.
2. “Is it clearly able to distinguish, prior output versus input?” (No.)
3. ✅Are responses correctly formatted?
    ~~Not if it's a file, or singularly a code block~~
4. ✅  Does best of produce 'better' responses?
   Depends. For best of 5 usually consistently, for less and especially for coding values 'the edge is sanded off'
5. Does looping produce better responses?
6. ✅ Does write page produce superior or inferior responses compared to a regular chat?
    Depends. Coding it appears no, for general inquiry and reports: Definitely.
7. ✅ Does the login / register check work as expected?
    Yes.
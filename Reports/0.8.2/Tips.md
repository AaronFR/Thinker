
# Tips

- When creating a react app the application should have informed the user to run a command like npx create-react-app to build the program. Not try and do it themselves/yourself.
- Think through architectural decisions. E.g. frontend is complicated rather than just saying add a router to the App.js page
 state that it should be added to an index.html preferably
- If you have a fault program and you ask the ai: "this is my code, this is the problem, what do you suggest" it can run
 in loops forever if its solution doesn't work or clashes with other pieces of code. If you ask instead "I am trying to create an X"
 how are X's typically created? How do they approach problem Y specifically?" This can avoid these types of clashes and provide
 a well rounded solution from the get go.
  - A workflow that asks the AI to consider the platonic ideal first then thinks through how to solve your specific issue may lead to better solutions, especially if serious changes could be recommended. (!!!)
- On the theme of looping forever, remember AI does not think, it got stuck looping the same stuff WHEN exposed to the logs
 when trying to write a solution for refreshing tokens on a websocket connection. It got caught up and biased by the idea of
 doing things a specific way instead of adapting to the information provided and changing track.
- 01 models have a bad habit of trying to 'codify' every problem they're given. Something to lean into for the coder persona, rectify and manage for everything else.
- 01 models should be forced to explain and reason first THEN write code, not explain themselves after the fact
- Telling ai models not to do something is dangerous, even if they do it they can be obsessed with that and refuse to focus on what you actually wanted them to do

-

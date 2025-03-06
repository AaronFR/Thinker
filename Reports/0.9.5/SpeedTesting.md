# Speed tests

## Internet search and User context functionality testing

The two primary performance-intensive optional functionalities

Each prompt sampled and averaged after 5x runs
 
| Prompt                                                        | Local (s) | Deployed (s) |
|---------------------------------------------------------------|-----------|--------------|
| "Hey" (o3-mini, background: gemini-2.0)                       | 8         | 6.1          |
| "Talk to me in great detail about ancient Rome" (dito)        | 11 (13)   | 12.7         | (from this point on times are logged programatically) (huge variability over time, probably due to load on openAi servers)
| "Talk to me in great detail about ancient Rome" (all gemini)  | 13        | 11.9         |
| "Hey" (all gemini)                                            | 5.4       | 3.7          |
| "Talk to me in great detail about ancient Rome" (all o4-mini) | 15.4      | 15.8         |
| Same prompt (all gemini +internet +user-context)              | 47.1      | 38.7         |
| Same prompt (all gemini +internet)                            | 20.75     | 20.8         | (well now it's greece because I'm afraid of hitting the same sites too much, but you get the idea. Deployed has an outlier that slows it down - but it's a REAL outlier)
| Same prompt (all gemini +user-context)                        | 30.6      | 25.3         | (Notable decrese in time after 4th call in both sets, presumably neo4j client 'warming' up to requests from this address
| Hey (all gemini +internet +user-context)                      | 19        | 15.45        |
| Hey (all gemini +internet)                                    | 12.91     | 8.57         |
| Hey (all gemini +user-context)                                | 12.45     | 7.85         |

### Notes

- Large variation in Deploy times
- Large variation over time, tests have to be run back to back for any degree of accurate comparison


### Functionality percentage increase in duration estimates

| Functionality                 | Local | Deployed |
|-------------------------------|-------|----------|
| Complex task (all gemini-2.0) | 1x    | 1x       |
| +internet                     | 1.6x  | 1.75x    |
| +user-context                 | 2.35x | 2.1x     |
| +internet +user-context       | 3.25x | 3.65x    | (These measurements roughly add up to the combined total: 1.6 x 2.35 = 3.76 , 115% of actual. 1.75 x 2.1 = 3.675x, 100.7% of actual)
| Very simple task              | 1x    | 1x       |
| +internet                     | 2.4x  | 2.3x     |
| +user-context                 | 2.3x  | 2.1x     |
| +internet +user-context       | 3.5x  | 4.3x     | (Deployed roughly matches up to the combined total, 2.3 x 2.1 = 4.83, 112.3% of actual. Local is -at least the same order of magnitude? 2.4 x 2.3 = 5.52, 157% of actual)

### Conclusion

- Deployed has a small time advantage for small prompts, probably around 2 seconds to restart for a request locally
  - However, more functionality costs proportionally more time when deployed. It's not clear what this could be.
- True to the general llm analytics, gemini is not only faster but has a notably lower latency, around 2 seconds for the simple prompts
- We can *very* roughly state that internet functionality adds a 2x increase in duration, while user context gives a more consistent 2.1x multiple
  - These are based on the deploy times, while local is good for comparison and for informing decisions based off local development feedback: users will be using the deployed instance.
- User context can be moved out of beta, its very slow- but internet search is not *really* slower


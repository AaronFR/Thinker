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
- For reference testing this (110 prompts) cost approximately ~27 cents

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
  - These are based on the deployment times, while local is good for comparison and for informing decisions based off local development feedback: users will be using the deployed instance.
- User context can be moved out of beta, its very slow- but internet search is not *really* slower


## Best of testing

This isn't *just* a speed test, it's also a test of best of it's self, what it's good at or not
All tests will be run on gemini-2.0, and on the deployed instance.
For the Best of columns the time and cost are measured.

| Functionality             | w/ out Best of  | Best of 2       | Best of 3           | Best of 5       | Best response? |
|---------------------------|-----------------|-----------------|---------------------|-----------------|----------------|
| "hey"                     | ¢ 0, 3.76s      | ¢ 0, 4.83s      | ¢ 0, 5.22s          | ¢ 0.01, 4.93s   | 5 or n/a       | (1 decided to do a code block for some reason, 2 and 3 are litterally identical, 5 is more personable)
| Holiday suggestion        | ¢ 0.02, 6.49s   | ¢ 0.03, 8.41s   | ¢ 0.03, 11.74s      | ¢ 0.12, 12.07s  | 5              | (Hands down, Gives 2 primary recomendations, 3 additional ones and actually good advice. 2 and 3 still identical and 1 is the 2nd best
| What men think about      | ¢ 0.01, 6.82s   | ¢ 0.05, 11.84s  | ¢ 0.07, 10.77s      | ¢ 0.13 , 20.35s | 5              | (2 and 3 we're meerly similar, what's
| Current News +internet    | ¢ 0.05, 12.15s  | ¢ 0.17, 18.21s  | ¢ 0.24, 17.28s      | ¢ 0.27 ,18.22s  | 3              | (Encountered timeout errors on 2 and 3, ran locally so don't look too hard into the times)
| Write Code (bug fix)      | ¢ 0.36, 44.13s  | ¢ 0.36, 29.1s   | ¢ 0.51, 199.75s (!) | ¢ 0.96, 56.96s  | 1              | (Brutal errors, possibly caused by an empty user or system message. (I don't know why gemini chooses to raise an exception when an empty string system message is sent, but hey), the extremly high time in best of 3 is simply caused by the first step timing out
| Discuss Code Improvements | ¢ 0.14, 24.37s  | ¢ 0.61, 49.38s  | ¢ 0.55, 49.38s      | ¢ 0.97, 39.18s  | 1 (5 in 2nd)   | (+internet)
| Improve tooltips          | ¢ 0.05, 9.72s   | ¢ 0.21, 20.4s   | ¢ 0.23, 18.55s      | ¢ 0.38, 21.39s  | 1              | (local)
| Platform recommendations  | ¢ 0.01, 14.63s  | ¢ 0.07, 23.79s  | ¢ 0.07, 20.9s       | ¢ 0.12, 23.67s  | 1 (5 in 2nd)   | (local)
| Activity suggestion       | ¢ 0.007, 13.67s | ¢ 0.03, 19.84s  | ¢ 0.05, 19.6s       | ¢ 0.07, 20.35s  | 5              | (local)
| Activity suggestion (o3)  | ¢ 0.04, 11.76s  | ¢ 0.74., 17.14s | ¢ 0.98, 19.49s      | ¢ 1.75, 24.91s  | 5 (3 in 2nd)   | (Curiously repeated tests, bear out the disproprotionate cost increase of using best of - on o3
// ToDo: Test o3-mini and measure the time changes

### Notes

- Durations increase proportionally to best of, this goes directly against my assumption for the last few months: "it's still one request so it should still take the same amount of time"
  - The increase also appears to be far too substantial to simply be an increase in the second evaluator call evaluating larger and larger inputs. 


// ToDo: Test write file versus regular chat


### responses
#### "Hey"
1: Okay, I understand. The user has simply said "Hey". My task is to acknowledge this greeting.

Response:
Hey there! How can I help you today?

2: Hey there! What can I do for you today?

3: Hey there! What can I do for you today?

5: Hey there! How can I brighten your day or lend a hand with whatever's on your mind?

#### "Hey I'm wondering what's a good, affordable place to go on holiday from Ireland?"

1: Ah, Ireland, the land of rolling green hills and even more rolling good times! When it comes to holiday destinations, there are some places that manage to be both kind to your wallet and big on the fun. Let's explore some affordable options, shall we?

Spain (Costa Brava or Costa del Sol): Spain is always a popular choice. The Costa Brava and Costa del Sol regions offer beautiful beaches, charming towns, and plenty of sunshine. Flights can be quite reasonable, and you can find affordable accommodations and dining options.
Portugal (Algarve): Similar to Spain, Portugal offers a lot of value for your money. The Algarve region is known for its stunning coastline, golf courses, and delicious seafood. It's easy to find budget-friendly flights and accommodations.
Italy (Naples or Puglia): For a taste of Italy without breaking the bank, consider Naples or Puglia. Naples offers amazing food (pizza, anyone?) and historical sites, while Puglia boasts beautiful beaches and countryside.
Croatia (Dubrovnik or Split): Croatia has become increasingly popular in recent years, and for good reason. The coastal cities of Dubrovnik and Split offer stunning scenery, historical landmarks, and a vibrant nightlife.
Poland (Krakow or Warsaw): Poland is an excellent option for a budget-friendly city break. Krakow and Warsaw offer rich history, cultural attractions, and delicious food at affordable prices.
Hungary (Budapest): Budapest is a beautiful city with thermal baths, stunning architecture, and a lively nightlife. It's also very affordable, with plenty of budget-friendly accommodations and dining options.
Consider these wonderful locales, you can explore culture, sunbathe, and have a good time all without emptying your bank account! Happy travels!


-> Gives 5 reasonable options

2:

Ah, Ireland... land of rolling green hills! When the wanderlust bug bites and you're ready to escape the Emerald Isle without emptying your pot of gold, here are some brilliantly affordable holiday destinations:

For Sun Seekers:

The Algarve, Portugal: Think sunshine, stunning beaches, and charming towns. With budget airlines flying direct, it's very accessible! Plus, who can resist those delicious Portuguese tarts?
For City Explorers:

Krakow, Poland: A city steeped in history with a vibrant culture. You can explore medieval architecture, visit poignant historical sites, and indulge in hearty Polish cuisine, all while keeping your wallet happy. And the nightlife? Let's just say it's an experience.
Happy travels!

-> 2 options.. stupid pot of gold joke

3: Identical to 2

5: Ah, Ireland! A land of rolling green hills, cozy pubs, and the friendliest folks you'll ever meet. But even the Irish need a change of scenery now and then. If you're looking for an affordable getaway from the Emerald Isle, here are a few ideas, blending value with that holiday je ne sais quoi:

Sun-Kissed Shores (and Budget-Friendly)

The Algarve, Portugal: Picture yourself lounging on golden beaches, a glass of vinho verde in hand, as the sun warms your face. The Algarve offers stunning coastline, charming towns like Lagos and Tavira, and some seriously delicious seafood. Plus, flights and accommodation can be surprisingly affordable, especially if you travel during the shoulder seasons (spring or autumn).
Costa Brava, Spain: A classic for a reason! Think vibrant beach resorts like Lloret de Mar and Tossa de Mar, paired with historic towns like Girona. Tapas are cheap and cheerful, the beaches are beautiful, and the nightlife is buzzing. EasyJet and Ryanair often have great deals on flights.
City Breaks with a Twist

Krakow, Poland: A city steeped in history and culture, Krakow offers a fascinating blend of medieval architecture, poignant reminders of the past, and a vibrant modern scene. Explore Wawel Castle, wander the Old Town, and sample pierogi to your heart's content. Accommodation and food are generally very budget-friendly.
Budapest, Hungary: Known as the "Pearl of the Danube," Budapest is a city of thermal baths, grand architecture, and ruin bars. Explore Buda Castle, soak in the Széchenyi Baths, and enjoy a hearty goulash. Like Krakow, it offers great value for money.
Italy (Naples or Palermo): Want a taste of la dolce vita without the hefty price tag of Rome or Venice? Naples and Palermo offer vibrant culture, incredible food (pizza and cannoli, anyone?), and fascinating history, all at a more affordable price point.
Something Different

Croatia's Dalmatian Coast: Imagine crystal-clear waters, historic towns, and breathtaking islands. Croatia's Dalmatian Coast is a budget-conscious gem. Explore ancient Roman ruins, sail through the Adriatic Sea, and savor local delicacies without breaking the bank.
Morocco (Marrakech or Agadir): For a taste of North Africa, consider Marrakech or Agadir. Marrakech is a sensory overload with its bustling souks, vibrant colors, and exotic flavors, while Agadir offers a more relaxed beach resort experience. Flights can be reasonable, and you can find affordable riads (traditional Moroccan houses) or hotels.
Tips for Keeping Costs Down:

Travel during the shoulder seasons: Spring (April-May) and autumn (September-October) often offer the sweet spot of good weather and lower prices.
Be flexible with your dates: Mid-week flights are typically cheaper than weekend ones.
Consider budget airlines: Ryanair and Aer Lingus often have great deals from Ireland to various European destinations.
Consider self-catering accommodation: This can save you a bundle on food costs.
Look for package deals: Sometimes booking flights and accommodation together can unlock discounts.
Eat like a local: Try street food or local restaurants for affordable and authentic culinary experiences.
Whichever you choose, I hope you have a fantastic and affordable holiday!


-> Gives actually good advice, 5 options with 2 primary recommendations

#### Hey talk to me about the Roman Empire, describe some really cool interesting tidbit ands facts!

Actually no, but it's a very basic 'tell me about history' type question

1: Ah, the Roman Empire! A realm of emperors, gladiators, and architectural marvels that continues to fascinate us. Let's dive into some cool and interesting tidbits:

Purple Reign: Ever wonder why purple was associated with royalty? In ancient Rome, purple dye was incredibly expensive, extracted from thousands of sea snails. Only emperors and the elite could afford garments dyed in Tyrian purple, making it a symbol of power and status.

Vomitoriums - Not What You Think: Despite popular belief, vomitoriums weren't dedicated rooms for Romans to purge between courses. They were actually passageways that allowed large crowds to exit stadiums quickly. The name comes from the Latin word "vomere," meaning "to spew forth."

Gladiator Grub: Gladiators, those fierce warriors of the arena, followed a surprisingly vegetarian diet. They were known as "hordearii" (barley men) because they primarily ate grains and vegetables. This diet was thought to give them the necessary energy and endurance for combat.

The Emperor's New... Water System: Roman emperors didn't just build aqueducts for the people; they also had private aqueducts leading directly to their palaces. Imagine having your own personal water supply in a city where water was a precious resource!

Political Graffiti: Romans loved to express themselves, and they did so through graffiti. Walls in Pompeii were covered with political slogans, personal insults, love poems, and even advertisements. It's like the ancient version of social media, but with chisels and paint!


-> I really despise this way of talking.

2: Alright, buckle your sandals! Let's dive into some truly cool and interesting tidbits about the Roman Empire:

Vomitoriums: Fact vs. Fiction: Forget the image of Romans strategically purging between courses. Vomitoriums were actually cleverly designed passageways in stadiums like the Colosseum, allowing huge crowds to enter and exit quickly. Think efficient crowd control, not ancient binge-eating rituals!

Purple Reign (and the Sea Snails Behind It): Purple was the color of power, reserved for emperors. Why? Because Tyrian purple dye was extracted from thousands of sea snails, making it astronomically expensive. Imagine a pound of wool dyed purple costing more than a person's life!

Concrete Jungle That Lasts: The Romans were concrete gods. Their recipe, using volcanic ash, was so good that many structures are still standing after 2000 years, often surpassing modern concrete in durability. Take that, modern construction!

Pigeon Post Power: Forget email, the Romans had pigeons! They used these feathered friends to send messages, especially during battles, delivering crucial news back to Rome.

Gladiator Retirement Plans: Gladiators weren't just fighting to the death every day. Some skilled gladiators did retire, often becoming trainers for the next generation of fighters or even working as bodyguards. Talk about a career change!

Pompeii's Graffiti Scene: Pompeii wasn't just preserved by ash; it was covered in graffiti! We're talking jokes, insults, love notes, political statements... basically, imagine stumbling upon 2000-year-old bathroom stall covered in the same stuff you see today.

The Roman Empire really was full of surprises!


-> Base style of communication these are interesting facts and an improvement on the best of 1 response

3: Alright, let's dive headfirst into the fascinating, and often bizarre, world of the Roman Empire!

Romans were obsessed with urine! They used it for everything from teeth whitening (the ammonia was thought to remove stains) to tanning leather and even laundry. Public urinals were big business, and urine was taxed. "Pecunia non olet" ("money doesn't stink") said Emperor Vespasian when criticized for it.

Road Trip! They built around 400,000 kilometers (250,000 miles) of roads, engineered masterpieces designed for durability and efficiency. This allowed for rapid military deployment, trade, and communication. Imagine a superhighway system connecting an entire continent, all built by hand!

Gladiators weren't just muscle-bound brutes: While some fit that description, many were highly skilled athletes, almost like modern-day sports stars. Some were even celebrities, endorsing products and attracting huge crowds. They went to gladiator school, where they were offered contracts, food, lodging and medical care in exchange for their participation in gladiatorial combats!

Concrete Jungle: The Romans were masters of concrete, and their recipe was so good that many structures built over 2,000 years ago are still standing today! Their secret ingredient? Volcanic ash, which made their concrete incredibly durable and resistant to seawater.

Vomitoriums weren't what you think: Contrary to popular belief, vomitoriums weren't rooms where Romans purged themselves during feasts to make room for more food. They were actually passageways that allowed large crowds to quickly exit a building, like a stadium or theater. Think of them as the emergency exits of their time!

Socks and Sandals approved!: Romans were wearing socks with sandals well before it became a fashion faux pas. Archaeological evidence found in Britain proves it!


-> Hmmm I find this less interesting that 2

5: Alright, buckle your sandals; we're diving headfirst into the fascinating world of the Roman Empire!

Vomitoriums weren't what you think: Forget images of Romans purging between courses. Vomitoria were actually stadium exits designed to "spew forth" crowds quickly. Talk about crowd control!
Purple was the power color: Only emperors could wear pure purple. To produce just one gram of Tyrian purple, it took around 9,000 murex snails, making it worth more than gold. Imagine flexing that hard.
Gladiators had fan clubs: These weren't just brutal fighters; they were celebrities. They had merchandise, endorsements, and groupies. A successful gladiator could become richer than many senators. They ate a primarily vegetarian diet of barley, beans, and oatmeal. They were nicknamed "Hordearii" which translates to "barley men." One of the most intriguing gladiator types was the 'Retiarius'. Armed with only a net, trident, and dagger, they were lightly armored, relying on agility and strategy to ensnare and defeat their opponents. Imagine facing that in an arena! If they survived enough battles, they could retire with wealth and fame. Some even became celebrity trainers for new gladiators. Not bad for a job that involves battling to the death.
Concrete was a game-changer: Roman concrete was so good that many structures still stand today. Their secret ingredient? Volcanic ash. They were basically ancient material scientists.
Road trip!: The Roman road network spanned over 400,000 kilometers (250,000 miles). That's like driving around the world ten times! It's often said, "All roads lead to Rome," and for a good reason.
Mouse Patrol: Romans kept dormice as pets and even ate them as a delicacy. They would fatten them up in special containers called "gliraria" before roasting and serving them with honey and poppy seeds.
Aqueducts: The Romans were master engineers, and their aqueducts were a testament to their ingenuity. These structures not only supplied fresh water to cities but also powered mills and mines. Some aqueducts are still in use today!
Roman Law: Roman law was surprisingly fair and sophisticated for its time, influencing legal systems around the world. They had concepts like "innocent until proven guilty" [wow more advanced than France] and the right to a defense. So, next time you binge-watch a legal drama, remember to thank the Romans.
The Roman Empire: Always extra, always impressive, and always good for a party anecdote or two!


-> Humour sucks, but that's not the measuring stick: Many answers, the Gilirarium and the extra details on Tyrian Pruple we're especially interesting 

#### What's going on in the news, give me a precise interesting and insightful review

1: Here's a concise snapshot of the current news landscape, drawing from the three sources you provided:

Trump and International Relations: Donald Trump's stance towards Russia is causing concern among U.S. allies, who fear intelligence sharing could be compromised.
Domestic Issues in the U.S.: Potential cuts to Veteran Affairs (VA) contracts are raising alarms about veterans' care.
Global Affairs: North Korea has halted foreign tourism shortly after reopening.
Health: A report indicates that losing a baby late in pregnancy is more common in the Southern U.S., potentially linked to factors like lack of Medicaid expansion and prenatal care access.
Technology: There's concern about the vulnerability of undersea cables to sabotage, potentially threatening the UK's infrastructure.
Culture: Roy Ayers, a legendary musician known for "Everyone Loves the Sunshine," has passed away.
Business: Germany's car industry faces a crisis, impacting the country's economic outlook.
Social Issues: Diversity, Equity, and Inclusion (DEI) programs in the U.S. are under attack, potentially requiring a rebrand to survive. Ketamine abuse among young people is on the rise, causing catastrophic health impacts.


-> Fine, curt but covers many areas

2: Okay, here's a concise and insightful review of what's making headlines, drawing from the previous summaries:

Global Flashpoints & Lingering Shadows: The war in Ukraine remains a central concern, with questions about long-term support and intelligence sharing. Adding complexity, the US is engaging in direct talks with Hamas, highlighting the intricate dynamics of the Israel-Hamas conflict. And even when seemingly absent, Trump's influence looms large - from Zelenskyy expressing a willingness to work with him, to renewed discussions of a potential Greenland takeover.

Social & Political Divides Sharpen: DEI policies are facing increasing pushback, sparking boycotts and broader debates about inclusion. Immigration is a hot-button issue, fueling political tensions.

Beyond the Headlines: Keep an eye on the Pope's health, as reports suggest ongoing respiratory problems. On a lighter note, the world continues to deliver the unexpected, from golden toilet heists to the unveiling of unbelievably thin phones, reminding us that news isn't always about conflict and controversy.


-> Definitely precise, I would say this appears 'professional' but is ..shallow or otherwise.. mindless.

3: Okay, here's a concise and insightful look at the news landscape:

Politics: The reverberations from Trump's latest address to Congress continue, fueling fact-checking frenzies and heated debate. A key development: the U.S. has reportedly suspended intelligence sharing with Ukraine, a move with potentially significant geopolitical implications. Tensions are high as the House contemplates censuring a Representative for disrupting Trump's speech, showcasing the deep divisions within Congress. The debate around "sanctuary cities" is also intensifying, with mayors from major cities testifying before Congress.

World Affairs: Gaza faces a critical situation as supplies dwindle and prices skyrocket due to Israel's aid freeze. Adding to the intrigue, Trump's comment about Lesotho has sparked curiosity, especially given Musk's interest in doing business there.

Culture: Erykah Badu's declaration that "woke is the new Black" is sparking conversations about cultural shifts and evolving perspectives. She also discussed her music, MAGA, real hip hop and ‘A.I. ancestors’.

Legal: The Supreme Court dealt a blow to the Trump administration by rejecting its bid to freeze billions in foreign aid.

Podcast Trends: News commentary podcasts like "Pivot," "Consider This from NPR," and "The Bulwark Podcast" are dominating the charts, reflecting a strong public appetite for in-depth analysis of current events.


-> Strangely better, some ai 'mindlessness' but it has a proper appearance of good coverage

5: Okay, here's your daily download of news insights!

Top Story: The media landscape is more fragmented than ever. Everyone is vying for your attention, and news podcasts are booming, but quality varies wildly. It's a microcosm of the broader media environment: fragmented, competitive, and increasingly shaped by personalization and ideological alignment.

Key Trends & Observations:

Podcast Saturation: The podcast arena, particularly in news and commentary, is incredibly crowded.
Diverse Formats: News podcasts come in all shapes and sizes, from quick daily briefings to deep dives and even comedic takes.
Legacy Media Adaptation: Traditional news organizations (NYT, NPR, BBC, etc.) have aggressively moved into the podcast space, leveraging their existing journalistic resources and brand recognition.
Political Polarization: Many news commentary podcasts wear their political leanings on their sleeves, catering to specific ideological audiences.
Beyond Headlines: Many news podcasts attempt to go beyond the headlines, offering analysis, context, and different perspectives on current events.
What to Watch (Podcasts):

For a Quick Hit: "Apple News Today" or "FT News Briefing" — short, sweet, and to the point.
For a Deeper Dive: "Today, Explained," and "Post Reports" give you a longer, more analytical take on key issues.
Critical Media Consumption: "On The Media" is your go-to, with a smart and relentlessly interesting perspective.
Pivot: Kara Swisher and Scott Galloway slice and dice tech, business, and politics with sharp wit and predictions.
The Bulwark Podcast: Tim Miller tackles political news with a pro-democracy slant and a dose of humor.
In the Headlines:

Geopolitics: Ongoing tensions and conflicts continue to shape international relations, influencing government policies and business decisions.
Media: Examination of how media shapes our understanding of the world, including free speech and government transparency.
Politics: Unfiltered conversations exposing power plays, agendas, and policies.
Business: Coverage of global markets and financial scoops, along with insights into how various factors influence business decisions.
Culture: Discussions about culture, exploring new ways to think about various aspects of life.
The Takeaway:

Be picky. The podcasting world is flooded, so choose sources known for reliable reporting.
Mix it up. Get a range of perspectives. Don't let your echo chamber get too comfy.
Stay informed, not overwhelmed. News should empower you, not stress you out.
And remember, a little skepticism goes a long way. Happy listening!


-> Longest response. "Quality varies wildly" it certainly does. Detailed, but I asked about the news not about political podcasting


#### Refactor InternetSearch.py with timeout functionality when attempting to read sites.

Isn't this interesting timing?

"There is an occasional bug where when attempting to read a site it appears that instead the system gets stuck, presumably waiting for a connection that never comes, in any event can you add some sort of timeout function when reading website content? So that if it does get stuck it skips after say 10 seconds?"

Write method

1: Not bad, notices that urls are sent to the frontend and SEPARATELY sends faulty URLs (which was in fact something I was planning down the line),
 implements the timeout via knowledge of requests and handles the cases well it looks like.

2: Poor. Implements the required functionality but hardcoded, doesn't include specific error codes like 1, doesn't anticipate future requirements

3: Additional generic error code, doesn't anticipate future needs like 1.

5: Almost identical to 5, the best of process stripped out future aspects I actually like


#### Given my process_message_ws.py route, analyse the file and make notes about possible areas of improvement: performance,
 reliability, useful information given, logical flow. Given these notes re-write the file.

first test run on local gave a decent suggestion, though deletes my abort code

1: Not bad, worst I can say is I'm not a fan on the debug log spam and logging by user_id and not message_id is a mistake

2: (incorrectly ran first time on the results of best of 1. Interesting though, updated schema but tried changing categorisation to an async operation, that just doesn't work with the current workflow)

Pretty terrible, not actually formatted correctly

3: Not awful, but gives a bunch of suggestions I'm not really a fan of (e.g. logging config, flask rooms)

5: Close, and it marks logs with message_uuid but I think 1 is just a bit better

#### Attached are the tooltips for llm wrapper website, first improve them with the primary goal of making the purpose of 
the element the are applied to more obvious and intuitive for the user (intuiting what said purpose is from the current tips)
Then feel free to make your own suggestions.

1: A handful of suggestions contain *some* improvement. Continues the phenomena of 'boiling' prior output down.

2: It's attempts at adding charm are kinda cringe, interestingly it's the *same* variables more or less that I think could 
be usefully changed. So context is important

3: Less cringe but also less useful alterations

5: "Wait that's actually a good, clear sentenc- oh it's just my writing, copied". Nothing over the over prompts


#### I'm looking for a good social media site to use, it should be focused on the user, I'm open to it being paid instead of free, 
it primarily has to have an algorithm that isn't focused purely on engagement, creating echo-chambers, what would you recommend?


1: Are.na, Tildes, Cohost and Mastodon: Sounds interesting

2: Mastadon and Tildes, more (useful) information but less options

3: Tidbits focused on, mentions Are.na and Glass (not interested in photography)

5: Gives a holistic set of suggestions with a oddball answer, comprehensive but 1 gave me the most options


# I have a free hour and I'm bored, what would you recommend for something I can watch or read online?


1: "The Gunfighter" (YouTube) and "The untold story of the cat who brokered a peace treaty in Turkish politics" ->
It looks like there aren't many great matches for your search

Huh.

2: "Key & Peele Best Skits" or "Mitchell and Webb Look." , "A ted talk"
Electric Literature or The New Yorker's fiction, "A blog post"

Better, but not very precise

3: "The Black Hole" on YouTube (6 minutes) [it's actually 3], netflix's explained series (20 mins each)
The Egg by Andy Weir (10 minutes), Wikipedia: paperclips or anglerfish mating rituals

Alright-ish

5: "A short film" on youtube or vimeo, "A TED talk", "Youtube skits: Key and Peele or Monty Python"
The New Yorker, The Atlantic, or Longreads 
Lightspeed (sci-fi) [Interesting], Fantasy & Science Fiction, or Clarkesworld
"Read A wikipedia article, Bolivian Tree Lizard mating rituals", [weirdly obsessed with odd animals and there mating rituals]

Probably the best for actually useful suggestions


# I have a free hour and I'm bored, what would you recommend for something I can watch or read online? (o3-mini)

1: shortoftheweek and Project Gutenberg [Can recommend], The importance of being earnest

These are good suggestions

2: Netflix's Black mirror Bandersnatch, Shirley Jackson's "The lottery"

Meh

3: Paperman (10 minutes) by Disney, Ted Talks (Your body language shapes who you are), The Egg, Project Gutenberg -> Oscar Wilde's
The happy prince and other Tales

Alright

5: "The present" (10 minutes) + Don Hertzfeldt's "World of tomorrow" (16m)
Project Gutenberg, Oscar Wilde "The Canterville ghost" that or "A medium article"


# Improve System Messages


1: 

2: 

3: 

5: 




1: 

2: 

3: 

5: 


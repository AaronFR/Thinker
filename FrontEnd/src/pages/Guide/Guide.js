import Navigation from "../../components/Navigation";
import '../../App.css';
import './Guide.css'

export const About = () => {
  return (
    <div>
      <div>

        <h2 className="centered">
          🚧 In beta - Beta testers wanted! Enquire and get to use the app <i>for free</i> 🚧
        </h2>
      </div>
      

      <p>
        Hey, thanks for checking this application out! 'The Thinker' is designed to be a low fuss, low BS tool for iteracting with LLMs and using them
        in your day to day life and work. Without being ripped off by 'AI Hype' grifters and idiots.
      </p>
      <p>
        I've been looking at the state of AI since before gpt-2 and for the last 2 years I've been thinking: "Okay cool.. is <i>this</i> it? 
      </p>
        <ul>
          Where can I use workflows of <b>multiple</b> prompts, not just one and only one at a time?
        </ul>
        <ul>
          Where can I, <i>you know</i>, use AI to help automate using AI??
        </ul>
        <ul>
          Where can I deeply customise how I interact with LLMs and how they respond to my prompts?
        </ul>
        <ul>
          Where uses a system to try and mitigate the inconsistencies and hallucinations of LLMs <i>intelligently</i>,
          instead of thinking we need to try and cram
          the entire, up to date human canon inside a statistical algorithm?
        </ul>
        <ul>
          And where can I get them without having to pay for another damn subscription?
        </ul>
        <ul>
          There are products designed for enterprise, but where is an application for the average person?
        </ul>
        
        
      <small>prefereably open source</small>

      <p>Eventually, I just got tired of wondering these questions and decided to take a shot at it myself!</p>



      <h2 className="centered">Okay, why should <i>I</i> care?</h2>
        <h3>Reasonably Priced</h3>

        <p>
          If you plan on using or even just experimenting with AI, The Thinker would be a great place to start because it's <b>pay as you go</b>
        </p>
        <p>
          No monthly subscription, no running costs, no qoutas, no limits. While your also provided with workflows and optional functions that can help
          you make the most of AI in your day to day.
        </p>
          <ul>
            You can put in an amount as low as <b>$0.10 (US)</b> to get started and if you use the default, <s>cheap</s> economical models that can actually last a bit.
          </ul>
          <ul>
            No running fees. Put in any amount and come back and use it whenever you want. The next day, the next month, the next year. Whenever.
          </ul>

        <p>
          The cost of the application will be our costs per LLM api call plus a small percentage to pay for server costs and salary 
          (Hopefully around +10-20%, but for now its at cost -so at a loss)
        </p>
        <p>And if you want to use it locally and just use your own API keys you can.</p>
    </div>
  )
}

export const Tutorial = () => {
  return (
    <div>
      <h2 className="centered">How do I use it?</h2>

      <h3>Home Page</h3>
      <p>
        On the home page you'll see the typical LLM wrapper prompt box. When you make your first request that request will be Automatically
        categorised based on its contents -so you don't need to worry about organising your prior messages yourself. At the same time a persona
        (role) and workflow will be assigned.
      </p>
      <p>
        Different personas interpret responses and produce different responses based on their role. `Coder` Will work like a software developer given a coding ticket,
        `Writer`'s will act like writers creating an article and so on.
      </p>
      <p>
        Workflows dictate how the applciation will respond and what it will output
      </p>
        <ul>
          Chat - Your typical prompt -{'>'} response
        </ul>
        <ul>
          Write - will write to a file name you suggest or come up with its own. The Writer persona can be asked to write a certain number of 'pages' for arbitrarily long documents
        </ul>
        <ul>
          Auto - Will process each and every file reference you select/upload as individual prompts. (I find this useful for improving on entire folders or working on many tasks at once)
        </ul>

        <h4>Tags</h4>
        You'll see some boxes beneath the command menu, these are tags you can write your own say if you want to explicetely categorise a prompt.
        This is mostly a debug feature but one is of note:

        <ul>
          best of - If you specifiy a number, the program will run each step in the workflow that many times and then run again, filtering for the best result. This can improve consistency
          or whatever other factor you would like to optimise for.
        </ul>


        <h3>Settings</h3>
          <p>Here you can config how the application will react in detail</p>
            <ul>User Interface</ul>
            <ul>
              Functionality - By default most features a few features are disabled, toggle them on if you want to try them out. Each function typically incurrs an additional cost:
              However each function has been designed to work on the cheapest available LLM model (gpt-4o-mini), so they shouldn be rather afforadable to run ()
            </ul>
            <ul>System Messages - These dictate how an LLM will respond to your prompt. You can customise nearly all system messages based on your preferences</ul>

        <h3>Messages</h3>
          <p>
            Here you'll see prior messages and files that have been created/uploaded, if you select on the bottom of a file or message you can select it, then its contents will be used as reference
            in your next prompt
          </p>
          <p>
            if you want to expand a file or prompt, just click on the text/file name respectively to expand the item
          </p>
    </div>
  )
}

export function Guide() { 

  return (
    <div className="scrollable container">
      <Navigation />

      <h1 className="centered thinker">
        The Thinker AI
      </h1>
      <h2 className="centered">
        🧰 A toolbox for AI 🧰
      </h2>

      <About />

      <Tutorial />      
    </div>
  )
}

export default Guide;
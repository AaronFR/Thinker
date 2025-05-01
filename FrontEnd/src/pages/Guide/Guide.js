import Navigation from "../../components/Navigation";
import '../../App.css';
import './Guide.css'

import TooltipConstants from '../../constants/tooltips';
import { Tooltip } from "react-tooltip";
import GitHubButton from "../../components/GitHubButton";

export const About = () => {
  return (
    <div className="about">
      <p>
        'The Thinker' is designed to be a low fuss, low BS tool for iteracting with <u
          id="not currently anyway"
          className="explanation"
          data-tooltip-id="tooltip"
          data-tooltip-html={TooltipConstants.llmDetails}
          data-tooltip-place="bottom"
        >
          LLMs 
        </u>  and using them
        in your day to day life and work. Without being ripped off by 'AI Hype' grifters.
      </p>
      <p>
        I've been looking at AI since before gpt-2, before the hype and I've been thinking: "Okay cool.. is <i>this</i> it? 
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
          Why do I have to deal with these limits and restrictions, why can't <i>I</i> set the limits?
        </ul>
        <ul>
          And where can I get them without having to pay for another damn subscription?
        </ul>
        <ul>
          There are products designed for enterprise, but where is something for the average person?
        </ul>
        
        
      <small>prefereably open source</small>

      <p>Eventually, I just got tired of wondering these questions and decided to take a shot at it myself!</p>



      <h2 className="centered">Okay, why should <i>I</i> care?</h2>
        <p>
          If you plan on using or even just experimenting with AI, The Thinker would be a great place to start because it's <b>pay as you go</b>.
        </p>
        <p>
          No monthly subscription, no recurring fees, no qoutas. While your also provided with workflows and optional functions that can help
          you make the most of AI in your day to day.
        </p>

        <p>
          Prices will be our own costs per AI resource we pay for, plus a small percentage to pay for server costs and salary 
          (1% after beta, but for now its at cost -so at a loss).
        </p>
        <p>And if you want to use it locally and just use your own API keys you can.</p>
    </div>
  )
}

export const BetaBanner = () => {
  return (
    <div className="centered beta-banner">
      <div>
        <h2 id="Not guranteed!">
          🚧 In beta - Email feedback/opinions and ask for <i>free credit</i>
        </h2>
        <div className="centered">
          <h3 >Contact us: <a href= "mailto:TheThinkerAi@protonmail.com">TheThinkerAi@protonmail.com</a></h3>
        </div>
      </div>
    </div>
  )
}

export const Pitch = () => {
  return (
    <div>
      <div className="card-container">
        <div className="card">
          Popular AI applications
          <ul id="giving 'wrappers' a bad name">
            😑 - <i>Very</i> simple, one prompt -{`>`} one response
          </ul>
          <ul>
            🗿 - You can maybe change the instructions or the tone - which does nothing usually
          </ul>
          <ul id="I can see people saying 'well I never have this problem', but I dunno this stuff REALLY annoyed me, personally">
            😠 - Constantly sorting long stacks of messages to find that one you want..
          </ul>
          <ul id="because 'f### you, pay me' right?">
            🤑 - Subscription models, costing the same amount of money regardless of how little you use the application in a given month, if at all
          </ul>
          <ul>
            🐢 - Rate limits to ensure your not dipping into those profit margins
          </ul>
          <ul hidden>
            🥴 Hallucinates and is generally unreliable
          </ul>
          <ul hidden>
            👁‍🗨 Explicetely (sometimes) tell you they will use your data for their own purposes
          </ul>
          <ul id="because 'fuck you, pay me' right?">
            🔐 - Closed source: closed off, uncheckable, non-collaborative, <b>untrustworthy</b>
          </ul>
        
        </div>
        <div className="card">
          The Thinker AI
          <ul>
            😃 - Utilise workflows and optional features, one prompt can trigger as many AI calls as you want/need.
          </ul>
          <ul>
            ⚙ - Fully customisable. Don't like a feature? Just turn it off
          </ul>
          <ul>
            🤖 - Uses AI... to automate using AI
          </ul>
          <ul id="I'm hoping break even with budget for contribution bounties can be reached at 10-20% margin. That may be naive honestly.">
            ¢ - Pay as you go, pay for what you want as you want, with a small 1% margin (0% in beta) paying hosting costs and possibly the maintance and development of this application
          </ul>
          <ul id="Well. That's the idea anyway">
            🦅 - No Rate limits! Use as much as you can as quickly as you want
          </ul>
          <ul hidden id="WIP, though the workflow part is true">
            🤔 Workflows are designed by a humnan, with (optional) internet search every step of the way to minimise inaccuracies
          </ul>
          <ul hidden id="Currently we *can* see user messages, I need to implement privately hosted models that encyrpt/do not log user requests, otherwise as far as I'm concerned saying I encrypt user data - but then send it on to a 3rd party api, would be *false privacy*">
            🚧 (WIP) Option to select a privately hosted model that does not log your messages, encypted secure messages
          </ul>
          <ul>
            👐 - Open Source, providing a tool for the whole community
          </ul>
        </div>
      </div>
    </div>
  )
}

export const Tutorial = () => {
  return (
    <div className="tutorial">
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
        Workflows dictate how responses and actions taken
      </p>
        <ul>
          Chat - Your typical prompt -{'>'} response
        </ul>
        <ul>
          Write - will write to a file name you suggest or come up with its own. The Writer persona can be asked to write a certain number of 'pages' for arbitrarily long documents
        </ul>
        <ul>
          For Each - Will process each file reference you select/upload individually. (Useful for improving on entire folders or working on many tasks at once)
        </ul>

        <h3>Settings</h3>
          <p>Here you can configure how the application will react in detail</p>
            <ul>User Interface</ul>
            <ul>
              Functionality - By default most features a few features are disabled, toggle them on if you want to try them out. Each function typically incurrs an additional cost:
              But background processes run on a seperate model from the main, one that's economical and fast while still competent (You can select which specfific model is used as the background model in settings), so they should be rather afforadable to run
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
      <GitHubButton />

      <h1 className="centered thinker logo-bg">
        The Thinker AI
      </h1>
      <h2 className="centered">
        🧰 AI Toolkit 🧰
      </h2>

      

      <About />

      <Tutorial />

      <Tooltip id="tooltip" />
    </div>
  )
}

export default Guide;
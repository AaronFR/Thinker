import Navigation from "../../components/Navigation";
import '../../App.css';

import './Guide.css'

import TooltipConstants from '../../constants/tooltips';
import { Tooltip } from "react-tooltip";
import GitHubButton from "../../components/GitHubButton";

export const About = () => {
  return (
    <div className="about">
      <div className="QA-card">
        <h2>What is The Thinker AI?</h2>
        <p>The Thinker AI is a pay as you go AI chat website, that means no recurring fees, no quotas. You only pay for what you actually use. This also means that you get more control - <i>you</i> choose when to use expensive cutting edge models, additional features or just keep costs as low as possible.</p>

      </div>

      <div className="QA-card">
        <h2>What's the <i>point</i> of this site?</h2>
        <p>Do you like subscriptions?</p>
        <p>Neither do we. There are plenty of times when you want to ask AI loads of questions all at once.. then <i>none</i> at all for months. Being pay as you go means it's <i>fairer</i>, The Thinker AI also offers a greater degree of customization and options for increasing the 'power' of a given prompt, for offering features which making using AI convenient.</p>
        <p>You have the choice to use as much or as little as you'd like <i>precisely</i> because it's pay as you go.</p>

      </div>

      <div className="QA-card">
        <h2>What can I use it for?</h2>
        <p>Well for anything you'd like feedback on. AI is a good fit for ideation, opinions, drafts and testing/growing your own knowledge. To get the most use out of AI, use it as an assistant, something to <b>help</b> you do the work, not to try and do the work all on it's own - that's asking for trouble.</p>

      </div>

      <div className="QA-card">
        <h2>What does it cost?</h2>
        <p>You pay what we pay. Pay in what you'd like, each prompt you send will use up a portion of your balance - the cost is included on each prompt and the total lifetime cost of each feature is also displayed in settings.</p>
        <p>When you need to just top up your balance. Currently in Beta the AI is priced at cost, in future there will be a small margin on top to pay hosting costs, should be around a percent or two.</p>

        <p>We will soon be accepting payments, in the meantime there is a <i>limited</i> number of free 1$ credits available on registration.</p>
      </div>

      <div className="QA-card">
        <h2>I would like if the site did such-and-such -and I don't like that it does this-and-that</h2>
        <p><i><b>Please</b></i> let us know! We can't convey just how important feedback is to us. If you have an idea for something you'd like to see in our app, we'd be <i>happy</i> to take it onboard!</p>

        <p><a href= "mailto:TheThinkerAi@protonmail.com">TheThinkerAi@protonmail.com</a></p>
      </div>

        <p>And if you want to use it locally and just use your own API keys you can.</p>
    </div>
  )
}

export const BetaBanner = () => {
  return (
    <div className="centered beta-banner">
      <div>
        <h2 id="Not guaranteed!">
          🚧 In beta - Email feedback/opinions and ask for <i>free credit</i>
        </h2>
        <div className="centered">
          <h3 >Contact us - <a href= "mailto:TheThinkerAi@protonmail.com">TheThinkerAi@protonmail.com</a></h3>
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
            👁‍🗨 Explicitly (sometimes) tell you they will use your data for their own purposes
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
            ¢ - Pay as you go, pay for what you want as you want, with a small 1% margin (0% in beta) paying hosting costs and possibly the maintenance and development of this application
          </ul>
          <ul id="Well. That's the idea anyway">
            🦅 - No Rate limits! Use as much as you can as quickly as you want
          </ul>
          <ul hidden id="WIP, though the workflow part is true">
            🤔 Workflows are designed by a human, with (optional) internet search every step of the way to minimise inaccuracies
          </ul>
          <ul hidden id="Currently we *can* see user messages, I need to implement privately hosted models that encrypt/do not log user requests, otherwise as far as I'm concerned saying I encrypt user data - but then send it on to a 3rd party api, would be *false privacy*">
            🚧 (WIP) Option to select a privately hosted model that does not log your messages, encrypted  secure messages
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
      <h2 className="centered">Q&A</h2>

      <div className="QA-card">
        <h2>How do I get started?</h2>
        <p>Just put in your question (prompt) inside the text area on the home page after registering, then hit enter. The AI will then respond to your prompt. By default your account has a *minimum* number of features enabled, each one usually costs additional money after all. There are a few exceptions however for features that help explain how the application works. So when comfortable make sure to check the settings and enable/disable features to your own liking.</p>
      </div>

      <div className="QA-card">
        <h2>What's an AI model?</h2>
        <p><u
          id="not currently anyway"
          className="explanation"
          data-tooltip-id="tooltip"
          data-tooltip-html={TooltipConstants.llmDetails}
          data-tooltip-place="bottom"
        >
          LLMs
        </u> take in input text and then output text, it's worth noting that this is less intelligence and more pattern recognition.</p>
        <p>On the prompt page you can select the 'foreground' model, this AI model processes your prompt step by step. In settings you can select a default for the 'background' model, this handels background features, e.g. categorisation. The background model should be fast and economical. Don't worry the most economical model is selected by default.</p>
      </div>

      <div className="QA-card">
        <h2>What are Categories?</h2>
        <p>When you submit a prompt it's automatically categorised by the AI based on your prompts content. This is to help make retrieving and referencing prior content easier. If you want to reference a prior message in a new prompt, click on the text sample to expand, click on the footer to only select/deselect.</p>
      </div>

      <div className="QA-card">
        <h2>What are Workers/Workflows?</h2>
        <p>Workers are a type of 'focus' for your prompt. Each one responds to your messages in their own specific way. Writers focus on writing documents, coders on coding and presenting code.. etc.</p>
        <p>Workflows are sets of tasks for approaching various problems.</p>
        <ul>
          <li>Chat – single prompt → single reply</li>
          <li>Write – create or rewrite a file</li>
          <li>For Each – rewrite multiple files simultaneously</li>
        </ul>
      </div>

      <div className="QA-card">
        <h2>What settings should I change?</h2>
        <p>Check the <b>'Functionality'</b> group first, 'Prompt improvement' and 'Prompt questioning' in particular can be useful for helping writing a prompt when you really want a good result.</p>
        <p>With the same line of thought, enabling the option to produce multiple responses at once or getting the AI to rewrite/loop over it's answer can also improve answer quality.</p>
        <p>Initial settings are kept as simple as possible to avoid any additional expenses but also to prevent the initial experience from being <i>too</i> overwhelming. 
        But as you get familiar, if you want, you can fine-tune the specific instructions for almost every single AI process used.</p>
      </div>
    </div>
  )
}

export function Guide() { 

  return (
    <div className="scrollable container logo-bg">
      <Navigation />
      <GitHubButton />

      <h1 className="centered thinker ">
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
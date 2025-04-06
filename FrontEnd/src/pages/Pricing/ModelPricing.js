import React, { useState, useCallback } from 'react';

import TooltipConstants from '../../constants/tooltips';

import './styles/ModelPricing.css';
import openAiLogo from './styles/openAiLogo.png';
import googleLogo from './styles/googleLogo.png'; 

const models = [
    {
        name: 'Gemini 2.0 Flash',
        inputPerToken: 0.0000001,
        outputPerToken: 0.0000004,
        description: 'Very-affordable model while nearing peak performance. Talks more conversationally than OpenAi models',
        goodFor: 'Competent performance while very affordable. Fastest available LLM.',
        image: googleLogo,
    },
    {
        name: 'Gemini 2.0 Flash Lite',
        inputPerToken: 0.000000075,
        outputPerToken: 0.00000030,
        description: "One of the most inexpensive model's on the market",
        goodFor: 'EXTREMELY economical model',
        badFor: 'Basic, lower tier intelligence',
        image: googleLogo,
    },
    {
      name: 'GPT 4o Mini',
      inputPerToken: 0.00000015,
      outputPerToken: 0.0000006,
      description: 'Affordable open-ai model, capable, outputs short to the point statements',
      goodFor: 'Affordable model',
      badFor: 'Requests where you need peak performance',
      image: openAiLogo,
    },
    {
        name: 'Gemini 2.5 Pro Preview',
        inputPerToken: 0.00000125,
        outputPerToken: 0.00001,
        description: `Current cutting edge model for performance. 
        (NOTE: For inputs bigger than 200,000 tokens input costs double (100% increase),
        while output costs will rise by 50%.`,
        goodFor: 'Cutting edge model for problem solving and coding',
        badFor: 'Not a wide margin compared to o3 mini for the price.',
        image: googleLogo,
    },
    {
        name: 'o3 mini',
        inputPerToken: 0.00000055,
        outputPerToken: 0.0000044,
        description: 'OpenAi\'s leading publicly avaible model, intelligent, quick and affordable ',
        goodFor: 'Strong, problem solving model',
        badFor: 'Long latency (that means it takes a while to get started)',
        image: openAiLogo,
    },
    {
        name: 'o1 Mini',
        inputPerToken: 0.00000055,
        outputPerToken: 0.0000044,
        description: 'Very verbose, which can be good or bad depending on context',
        goodFor: 'Slightly faster than o3-mini',
        badFor: 'Long-winded, outdated by o3-mini',
        image: openAiLogo,
    },
    {
        name: 'GPT 4o',
        inputPerToken: 0.0000025,
        outputPerToken: 0.00001,
        description: 'Legacy model, competent but not as good as more recent, cheaper models',
        badFor: 'Expensive and no longer cutting edge',
        image: openAiLogo,
    },
];

const cheapestModel = models.reduce((min, model) => (model.inputPerToken < min.inputPerToken ? model : min), models[0]);

const ModelPricing = () => {
    const [priceDisplay, setPriceDisplay] = useState('perMillion'); // 'perToken', 'perMillion', 'multiplier'

    const formatPrice = useCallback(
        (price) => {
            if (priceDisplay === 'perToken') {
                return `$${price.toFixed(9)}/Token`;
            } else if (priceDisplay === 'perMillion') {
                const pricePerMillion = price * 1000000;
            
                let formattedPrice;
                if (pricePerMillion < 0.0999) { // don't round down sub 10 cent prices
                    formattedPrice = pricePerMillion.toFixed(3);
                    //Remove trailing zeros
                    formattedPrice = formattedPrice.replace(/(\.0*|0+)$/, '');
                } else {
                    formattedPrice = pricePerMillion.toFixed(2);
                }
            
                return `$${formattedPrice}/Million Tokens`;
            } else if (priceDisplay === 'multiplier') {
                const multiplier = price / cheapestModel.inputPerToken;
                return Number.isInteger(multiplier) ? `${multiplier}x` : `${multiplier.toFixed(2)}x`;
            } else {
                return `$${price.toFixed(9)}/Token`;
            }
        },
        [priceDisplay, cheapestModel])
    ;

    const handleToggle = useCallback((event) => {
        setPriceDisplay(event.target.value);
    }, []);

    return (
        <div className="models-container">
            <h2>Available models</h2>
            <p>
                <b>Warning:</b> This is beta pricing. Out of beta, the application will cost around 1.1x these prices to ensure maintenance costs can be paid.
            </p>
            <p>
                With additional features enabled its not just your original prompt that will be input, you can see the pricing of any enabled features in settings.
            </p>
            <p>
              Contained below are our recomendations and opinions, you should look up external sources. <a href='https://artificialanalysis.ai/models'>artificialanalysis.ai</a> is a good, comprehensive place to start.
            </p>
            
            <div className="toggle-container">
                <label
                  data-tooltip-id="tooltip"
                  data-tooltip-html={TooltipConstants.perToken}
                  data-tooltip-place="bottom"
                >
                    <input
                        type="radio"
                        value="perToken"
                        checked={priceDisplay === 'perToken'}
                        onChange={handleToggle}
                    />
                    Per Token
                </label>
                <label
                  data-tooltip-id="tooltip"
                  data-tooltip-html={TooltipConstants.perMillionToken}
                  data-tooltip-place="bottom"
                >
                    <input
                        type="radio"
                        value="perMillion"
                        checked={priceDisplay === 'perMillion'}
                        onChange={handleToggle}
                    />
                    Per Million Tokens
                </label>
                <label
                  data-tooltip-id="tooltip"
                  data-tooltip-html={TooltipConstants.byCheapest}
                  data-tooltip-place="bottom"
                >
                    <input
                        type="radio"
                        value="multiplier"
                        checked={priceDisplay === 'multiplier'}
                        onChange={handleToggle}
                    />
                    Multiplier of Cheapest
                </label>
            </div>

            {models.map((model) => (
                <div className="model" key={model.name}>
                    <div className="model-header">
                      <img src={model.image} alt={`${model.name} Logo`} className="model-logo" />
                      <h3 className="model-name">{model.name}</h3>
                    </div>
                    
                    <div className="centered model-header">
                        <p>
                            Input: <span className="cost input-cost">{formatPrice(model.inputPerToken, model)}</span>
                        </p>
                        <p>
                            Output: <span className="cost output-cost">{formatPrice(model.outputPerToken, model)}</span>
                        </p>
                    </div>
                    <p className="description">{model.description}</p>
                    <div className="good-bad">
                        {model.goodFor && (
                            <div className="good">
                                <strong>+</strong> {model.goodFor}
                            </div>
                        )}
                        {model.badFor && (
                            <div className="bad">
                                <strong>-</strong> {model.badFor}
                            </div>
                        )}
                    </div>
                </div>
            ))}

            <small>
              Prices last updated: 24th of Febuary
            </small>
        </div>
    );
};

export default ModelPricing;

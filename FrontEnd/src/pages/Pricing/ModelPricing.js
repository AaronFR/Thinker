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
        description: 'Very-affordable, very competent mid-tier model. Our recommended default model.',
        goodFor: 'Competent performance while very affordable. Very fast.',
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
        name: 'GPT 4.1 Nano',
        inputPerToken: 0.0000001,
        outputPerToken: 0.0000004,
        description: 'Competent economical model',
        goodFor: 'Affordable model. Fastest available model (Though only ~10% faster than 2.0 Flash)',
        badFor: 'Not as good as Gemini 2.0 Flash while in the same price range.',
        image: openAiLogo,
    },
    {
        name: 'GPT 4.1 Mini',
        inputPerToken: 0.0000004,
        outputPerToken: 0.0000016,
        description: 'Competent mid-tier model, more intelligent than Gemini 2.0 Flash but more expensive too',
        badFor: 'Not of the same ability as 04-mini and Gemini 2.5 Pro',
        image: openAiLogo,
    },
    {
        name: 'o4 mini',
        inputPerToken: 0.0000011,
        outputPerToken: 0.0000044,
        description: 'OpenAi\'s leading publicly available model.',
        goodFor: 'Current cutting edge model, very intelligent and affordable',
        badFor: 'Slow, Long latency (that means it takes a while to get started)',
        image: openAiLogo,
    },
    {
        name: 'Gemini 2.5 Pro Preview',
        inputPerToken: 0.00000125,
        outputPerToken: 0.00001,
        description: `Leading Gemini model. 
        (NOTE: For inputs bigger than 200,000 tokens input costs double (100% increase),
        while output costs will rise by 50%.`,
        goodFor: 'Very intelligent model',
        badFor: 'Expensive. 04-mini performs better for a lower price. Long latency (that means it takes a while to get started)',
        image: googleLogo,
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
                <b>Note:</b>A margin of around 1% will be applied when topping up your balance to pay for hosting costs. However in beta no such margin is applied.
            </p>
            <p>
                With additional features enabled its not just your original prompt that will be input, you can see the pricing of any enabled features in settings.
            </p>
            <p>
              Contained below are our recommendations and opinions, you should look up external sources. <a href='https://artificialanalysis.ai/models'>artificialanalysis.ai</a> is a good, comprehensive place to start.
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
              Prices last updated: 17th of April
            </small>
        </div>
    );
};

export default ModelPricing;

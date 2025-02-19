import React, { useState } from 'react';

import TooltipConstants from '../../constants/tooltips';

import './styles/ModelPricing.css';
import openAiLogo from './styles/openAiLogo.png';
import googleLogo from './styles/googleLogo.png'; 

const ModelPricing = () => {
    const [priceDisplay, setPriceDisplay] = useState('perMillion'); // 'perToken', 'perMillion', 'multiplier'

    const models = [
        {
            name: 'Gemini 2.0 Flash',
            inputPerToken: 0.0000001,
            outputPerToken: 0.0000004,
            description: 'Very-affordable model while nearing peak performance. Talks more conversationally than OpenAi models',
            goodFor: 'Near cutting edge performance while very affordable',
            badFor: 'Generates more coding typos than openAI models',
            image: googleLogo,
        },
        {
            name: 'Gemini 2.0 Flash Lite - preview',
            inputPerToken: 0.000000075,
            outputPerToken: 0.00000030,
            description: "Preview for Google Gemini's next economical model, which when released should be among the cheapest on the market",
            goodFor: 'EXTREMELY economical model',
            badFor: 'Rate limited and experimental currently',
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
            name: 'GPT 4o',
            inputPerToken: 0.0000025,
            outputPerToken: 0.00001,
            description: 'OpenAI latest flagship model, offers state-of-the-art performance across various tasks',
            goodFor: 'Complex tasks, high-quality outputs, and versatile applications',
            badFor: 'Cost-sensitive operations due to higher pricing',
            image: openAiLogo,
        },
        {
            name: 'o1 Mini',
            inputPerToken: 0.000003,
            outputPerToken: 0.000012,
            description: 'Very verbose, which can be good or bad depending on context',
            goodFor: 'Complicated tasks which benefit from reasoning',
            badFor: 'Long-winded',
            image: openAiLogo,
        },
        {
            name: 'o1 Preview',
            inputPerToken: 0.000015,
            outputPerToken: 0.00006,
            description: 'A very expensive preview model of o1 (which is itself extremely expensive) outmoded by o3, will be replaced when o3 is made available',
            badFor: 'Extremly expensive (o1-mini has a marginally worse performance)',
            image: openAiLogo,
        },
    ];

    const cheapestModel = models.reduce((min, model) => (model.inputPerToken < min.inputPerToken ? model : min), models[0]);

    const formatPrice = (price, model) => {
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
    };

    const handleToggle = (event) => {
        setPriceDisplay(event.target.value);
    };

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
              Prices up to date as of 19th of Febuary
            </small>
        </div>
    );
};

export default ModelPricing;

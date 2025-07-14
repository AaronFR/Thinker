import React, { useEffect, useState, useMemo } from 'react';
import './styles/ComparisonGraph.css'

const DATA      = [5, 7, 0, 0, 9, 2]
const MAX_VALUE = 10  // ($)
const BAR_GROWTH_DURATION  = 1.5 // (s)
const STAGGER   = 1.5 // seconds between each bar’s start
const WAIT_PERIOD = 2 // (s)
const BAR_W     = 40        // px
const GAP       = 16        // px
const PADDING   = 16        // px
const TOTAL_W   = 380       // px
const TOTAL_H   = 400       // px

export default function ComparisonGraph() {
  const innerH = TOTAL_H - 2 * PADDING
  const maxH = TOTAL_H - PADDING

  // 1) Precompute bar & line points
  const points = useMemo(() => {
    return DATA.map((v, i) => {
      const blueH   = (v / MAX_VALUE) * innerH
      const orangeH = innerH - blueH
      const y       = PADDING + orangeH
      const x       = PADDING + i * (BAR_W + GAP) + BAR_W / 2
      return { x, y, blueH, orangeH }
    })
  }, [innerH])

  // 1.5) Compute Y-axis ticks
  const tickCount = 5
  const ticks = useMemo(() => {
    return Array.from({ length: tickCount + 1 }, (_, i) => {
      // Round to nearest integer or one decimal
      return Math.round((i * MAX_VALUE / tickCount) * 100) / 100
    })
  }, [tickCount])

  // 2) After bars grow, flip stage
  const [modelStage, setModelStage] = useState(false)
  useEffect(() => {
    const lastDelay = (points.length) * STAGGER + BAR_GROWTH_DURATION + WAIT_PERIOD;
    const id = window.setTimeout(() => setModelStage(true), lastDelay * 1000)
    return () => window.clearTimeout(id)
  }, [points.length])

  return (
    <div className='centered'>
      <div className="comparison-container">
        <div className="titles">
          <h2 className={`graph-title sub ${modelStage? 'fade-out':'fade-in'}`}>
            Subscription Model
          </h2>
          <h2 className={`graph-title pay ${modelStage? 'fade-in':'fade-out'}`}>
            Pay As You Go Model
          </h2>
        </div>

        <div className='graph-content'>
          <div>
            <div className="graph-legend-wrapper">
              <div className="graph" style={{ width: TOTAL_W, height: TOTAL_H }}>
                
                {/* dashed axes */}
                <div className="axis axis-y"
                    style={{ top: PADDING, bottom: PADDING, left: PADDING }} />
                <div className="axis axis-x"
                    style={{ left: PADDING, right: PADDING, bottom: PADDING }} />

                {/* y-axis tick labels */}
                <div className="y-axis-labels" style={{ top: 0, left: PADDING }}>
                  {ticks.map((val, i) => {
                    const yPos = PADDING + (1 - val / MAX_VALUE) * innerH
                    return (
                      <div
                        key={i}
                        className="y-axis-label"
                        style={{ top: yPos }}
                      >
                        ${val}
                      </div>
                    )
                  })}
                </div>

                {/* stacked bars */}
                <div className="bars" style={{ padding: PADDING }}>
                  {points.map((p, i) => {
                    const hasCost     = p.blueH > 0
                    const blueDelay   = `${i * STAGGER}s`
                    const orangeDelay = hasCost
                      ? `${i * STAGGER + BAR_GROWTH_DURATION}s`
                      : `${i * STAGGER}s`
                    const orangeH = modelStage
                      ? p.blueH * 0.05
                      : p.orangeH

                    return (
                      <div key={i}
                          className="bar-wrapper"
                          style={{
                            width: BAR_W,
                            height: innerH,
                            marginRight: i < points.length - 1 ? GAP : 0
                          }}>
                        {orangeH !== 0 && <div
                          className="bar orange"
                          style={{
                            height: orangeH,
                            animationName: 'grow',
                            animationDelay: orangeDelay,
                            animationDuration: `${BAR_GROWTH_DURATION}s`
                          }}
                        />}
                        <div
                          className="bar blue"
                          style={{
                            height: p.blueH,
                            animationName: hasCost ? 'grow' : 'none',
                            animationDelay: blueDelay,
                            animationDuration: `${BAR_GROWTH_DURATION}s`
                          }}
                        />
                      </div>
                    )
                  })}
                </div>

                {/* line + dots */}
                <svg className="line-layer" width={TOTAL_W} height={TOTAL_H}>
                  {points.slice(1).map((p, i) => {
                    const prev = points[i]
                    const dx   = p.x - prev.x
                    const dy   = p.y - prev.y
                    const L    = Math.hypot(dx, dy)
                    return (
                      <line key={i}
                            x1={prev.x + PADDING} y1={maxH}
                            x2={p.x + PADDING}    y2={maxH}
                            stroke="crimson" strokeWidth="3"
                            strokeDasharray={L}
                            strokeDashoffset={L}>
                        <animate attributeName="y1"
                                from={maxH} to={prev.y}
                                begin={`${i * STAGGER}s`}
                                dur={`${BAR_GROWTH_DURATION}s`}
                                fill="freeze"/>
                        <animate attributeName="y2"
                                from={maxH} to={p.y}
                                begin={`${(i + 1) * STAGGER}s`}
                                dur={`${BAR_GROWTH_DURATION}s`}
                                fill="freeze"/>
                        <animate attributeName="stroke-dashoffset"
                                from={L} to={0}
                                begin={`${i * STAGGER}s`}
                                dur={`${BAR_GROWTH_DURATION}s`}
                                fill="freeze"/>
                      </line>
                    )
                  })}

                  {points.map((p, i) => (
                    <circle key={i}
                            cx={p.x + PADDING} cy={maxH}
                            r={6}
                            fill="white"
                            stroke="crimson" strokeWidth="2">
                      <animate attributeName="cy"
                              from={maxH} to={p.y}
                              begin={`${i * STAGGER}s`}
                              dur={`${BAR_GROWTH_DURATION}s`}
                              fill="freeze"/>
                    </circle>
                  ))}
                </svg>
              </div>
            </div>
          </div>
          
          <div className={modelStage === true ? 'logo-bg' : 'money-grub-logo-bg'}>
            <div className="legend">
              <div className="legend-item">
                <span className="legend-color orange" /> Margin
              </div>
              <div className="legend-item">
                <span className="legend-color blue" /> Usage
              </div>
            </div>
            <div className='descriptor'>
              <p>With a subscription model you pay a constant sum of money, even if you don't happen to use AI <i>at all</i> in a given period</p>
              {modelStage === true && <p>With a pay-as-you-go model margins are <b>actually proportional to how much you use</b></p>}
            </div>
          </div>
          
        </div>
        
      </div>
    </div>
  )
}

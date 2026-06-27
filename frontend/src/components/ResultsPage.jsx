import { useEffect, useState } from 'react'
import Disclaimer from './Disclaimer'
import { AlertCircle, AlertTriangle, CheckCircle, RefreshCw, ChevronRight } from 'lucide-react'
import { useLanguage } from '../LanguageContext'

export default function ResultsPage({ results, onRestart }) {
  const { lang, t } = useLanguage()
  const [animationProgress, setAnimationProgress] = useState(0)

  const getRiskConfig = (level) => {
    switch(level) {
      case 'Rendah':
      case 'Low': 
        return { color: 'var(--color-success)', text: t('riskLow'), Icon: CheckCircle }
      case 'Tinggi':
      case 'High': 
        return { color: 'var(--color-danger)', text: t('riskHigh'), Icon: AlertTriangle }
      default: 
        return { color: 'var(--color-warning)', text: t('riskMed'), Icon: AlertCircle }
    }
  }

  const riskConfig = getRiskConfig(results.risk_level)
  const probabilityNum = results.probability * 100
  const RiskIcon = riskConfig.Icon

  useEffect(() => {
    // Only animate after mount
    const timer = setTimeout(() => {
      setAnimationProgress(probabilityNum)
    }, 100)
    return () => clearTimeout(timer)
  }, [probabilityNum])

  const radius = 90
  const circumference = Math.PI * radius
  const strokeDashoffset = circumference - (animationProgress / 100) * circumference
  
  // Format percentage with comma if ID
  const displayPercentage = animationProgress.toFixed(1).replace('.', lang === 'id' ? ',' : '.')

  const renderMetricBar = (label, value, safeMin, safeMax, unit) => {
    const val = parseFloat(value);
    const min = label.includes('BMI') ? 10 : 40;
    const max = label.includes('BMI') ? 50 : 300;
    const percent = Math.min(Math.max(((val - min) / (max - min)) * 100, 0), 100);
    const isSafe = val >= safeMin && val <= safeMax;
    const color = isSafe ? 'var(--color-success)' : (val > safeMax ? 'var(--color-danger)' : 'var(--color-warning)');
    
    return (
      <div className="mb-4">
        <div className="flex justify-between text-bold text-sm mb-1">
          <span>{label}</span>
          <span style={{ color }}>{val} {unit}</span>
        </div>
        <div style={{ height: '12px', width: '100%', backgroundColor: 'var(--color-border)', position: 'relative' }}>
          <div style={{
            position: 'absolute',
            left: `${((safeMin - min) / (max - min)) * 100}%`,
            width: `${((safeMax - safeMin) / (max - min)) * 100}%`,
            height: '100%',
            backgroundColor: 'var(--color-success)',
            opacity: 0.3
          }} />
          <div style={{
            position: 'absolute',
            left: `calc(${percent}% - 4px)`,
            top: '-4px',
            width: '8px',
            height: '20px',
            backgroundColor: color,
            border: '2px solid var(--bg-primary)'
          }} />
        </div>
      </div>
    )
  }

  // Find glucose and bmi in contributing_factors, or use raw if we had it
  // Wait, backend predict doesn't return raw inputs. We have to parse them from the values.
  // Actually, contributing_factors has `value: "90.5 mg/dL"` etc. 
  const glucoseFactor = results.contributing_factors.find(f => f.factor.toLowerCase().includes('gluko') || f.factor.toLowerCase().includes('glucose'));
  const bmiFactor = results.contributing_factors.find(f => f.factor.toLowerCase().includes('bmi') || f.factor.toLowerCase().includes('massa'));
  
  const glucoseVal = glucoseFactor ? parseFloat(glucoseFactor.value) : null;
  const bmiVal = bmiFactor ? parseFloat(bmiFactor.value) : null;

  return (
    <div className="px-container py-section animate-slide-up">
      
      <div className="text-center mb-5">
        <div 
          className="badge"
          style={{ 
            backgroundColor: riskConfig.color,
            color: '#000',
            fontSize: '1.5rem',
            padding: '12px 32px',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '12px',
            boxShadow: 'var(--shadow-brutal)'
          }}
        >
          <RiskIcon size={28} strokeWidth={3} />
          <span>{riskConfig.text}</span>
        </div>
      </div>

      <div className="split-layout">
        <div className="split-left text-center">
          <div className="card mb-4" style={{ display: 'inline-block', width: '100%' }}>
            <h3 className="mb-4">{t('probStroke')}</h3>
            <div className="gauge-container">
              <svg width="280" height="150" viewBox="0 0 220 120" className="gauge-svg" style={{ margin: '0 auto' }}>
                <path
                  d="M 20 110 A 90 90 0 0 1 200 110"
                  fill="none"
                  stroke="var(--bg-secondary)"
                  strokeWidth="20"
                />
                
                <path
                  d="M 20 110 A 90 90 0 0 1 200 110"
                  fill="none"
                  stroke={riskConfig.color}
                  strokeWidth="20"
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeDashoffset}
                  style={{ transition: 'stroke-dashoffset 1.5s cubic-bezier(0.1, 0.7, 0.1, 1)' }}
                />
                
                <text x="110" y="90" textAnchor="middle" fontSize="2.2rem" fontWeight="900" fill="var(--color-text)">
                  {displayPercentage}%
                </text>
              </svg>
            </div>
            
            <div className="text-bold text-sm mt-3" style={{ borderTop: 'var(--border-width) solid var(--color-border)', paddingTop: '16px' }}>
              {t('modelUsed')} {results.model_used.replace('_', ' ').toUpperCase()}
            </div>
          </div>
          
          <button className="btn btn-accent btn-block mb-4" onClick={onRestart}>
            <RefreshCw size={20} strokeWidth={3} /> {t('btnRestart')}
          </button>
        </div>

        <div className="split-right">
          <div className="mb-5">
            <h3 className="mb-3">{t('contribFactors')}</h3>
            <div className="form-grid" style={{ gridTemplateColumns: '1fr' }}>
              {results.contributing_factors.map((item, idx) => {
                const brutalColors = ['var(--brutal-cyan)', 'var(--brutal-yellow)', 'var(--brutal-pink)', 'var(--brutal-lime)', 'var(--brutal-lavender)'];
                const bgColor = brutalColors[idx % brutalColors.length];
                const impactColor = item.impact === 'high' ? 'var(--color-danger)' : 
                                    item.impact === 'medium' ? 'var(--color-warning)' : 'var(--color-success)'
                return (
                  <div key={idx} className="card card-colored p-3 flex align-center gap-3" style={{ '--brutal-bg': bgColor, backgroundColor: 'var(--brutal-bg)', borderLeft: `8px solid ${impactColor}` }}>
                    <div>
                      <div className="text-bold" style={{ fontSize: '1.1rem' }}>{item.factor.toUpperCase()}: {item.value.toUpperCase()}</div>
                      <div className="text-sm text-muted">{item.description}</div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {(glucoseVal || bmiVal) && (
            <div className="mb-5">
              <h3 className="mb-3">{t('metricsAnalysis')}</h3>
              <div className="card p-4">
                {glucoseVal && renderMetricBar(t('glucose'), glucoseVal, 70, 140, 'mg/dL')}
                {bmiVal && renderMetricBar(t('bmi'), bmiVal, 18.5, 24.9, '')}
                <div className="flex justify-between text-xs text-muted mt-3">
                  <div className="flex align-center gap-1">
                    <div style={{width: 12, height: 12, backgroundColor: 'var(--color-success)', opacity: 0.3}}></div>
                    {t('safeZone')}
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="mb-4">
            <h3 className="mb-3">{t('recommendations')}</h3>
            <div className="card p-4" style={{ backgroundColor: 'var(--color-primary)', color: 'var(--bg-primary)' }}>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {results.recommendations.map((rec, idx) => (
                  <li key={idx} className="mb-3 flex align-start gap-3">
                    <ChevronRight size={24} strokeWidth={3} style={{ color: 'var(--color-success)', flexShrink: 0 }} />
                    <span className="text-bold" style={{ fontSize: '1.1rem' }}>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

        </div>
      </div>
      
      <Disclaimer />
    </div>
  )
}

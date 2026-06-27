import { useState, useEffect } from 'react'
import { Check, AlertCircle, ArrowRight, ArrowLeft, Target } from 'lucide-react'
import { useLanguage } from '../LanguageContext'

const getFallbackModels = (lang) => [
  {
    id: 'logistic_regression',
    name: 'LOGISTIC REGRESSION',
    recommended: true,
    badge: lang === 'en' ? 'RECOMMENDED' : 'DIREKOMENDASIKAN',
    description: lang === 'en' ? 'Most sensitive model. Excellent for early screening (85% Recall).' : 'Model paling sensitif. Sangat baik untuk screening awal (85% Recall).',
    pros: lang === 'en' ? 'High recall, safe for screening' : 'Recall tinggi, aman untuk screening',
    cons: lang === 'en' ? 'May yield false alarms' : 'Bisa memberikan false alarm',
    best_for: lang === 'en' ? 'Safety-first Screening' : 'Screening Mengutamakan Keselamatan'
  },
  {
    id: 'decision_tree',
    name: 'DECISION TREE',
    recommended: false,
    badge: lang === 'en' ? 'HIGH ACCURACY' : 'AKURASI TINGGI',
    description: lang === 'en' ? 'Highest overall accuracy using historical data patterns.' : 'Akurasi keseluruhan tertinggi menggunakan pola data historis.',
    pros: lang === 'en' ? 'Solid overall accuracy' : 'Akurasi keseluruhan mantap',
    cons: lang === 'en' ? 'Low recall, cases might be missed' : 'Recall rendah, bisa terlewat',
    best_for: lang === 'en' ? 'General Analysis' : 'Analisis Umum'
  },
  {
    id: 'knn',
    name: 'K-NEAREST NEIGHBORS',
    recommended: false,
    badge: lang === 'en' ? 'BALANCED' : 'SEIMBANG',
    description: lang === 'en' ? 'Classification based on similarity to other patients.' : 'Klasifikasi berdasarkan kemiripan dengan pasien lain.',
    pros: lang === 'en' ? 'Intuitive, similarity-based' : 'Intuitif, berbasis data mirip',
    cons: lang === 'en' ? 'Highly dependent on distribution' : 'Sangat bergantung distribusi',
    best_for: lang === 'en' ? 'Balanced Alternative' : 'Alternatif Seimbang'
  }
];

export default function ModelSelector({ onSelect, selectedModel, onBack }) {
  const { lang, t } = useLanguage()
  const [models, setModels] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    const baseUrl = import.meta.env.VITE_API_URL || 'https://xvasthunter-sana-backend.hf.space'
    fetch(`${baseUrl}/api/models?lang=${lang}`)
      .then(res => res.json())
      .then(data => {
        setModels(data)
        setLoading(false)
      })
      .catch(err => {
        console.warn('Failed to fetch models, using fallback', err)
        setModels(getFallbackModels(lang))
        setLoading(false)
      })
  }, [lang])

  if (loading) {
    return <div className="p-5 text-center text-bold text-lg">{t('loadingModels')}</div>
  }

  return (
    <div className="px-container py-section animate-slide-up">
      <h2 className="mb-2">{t('selectModelTitle')}</h2>
      <p className="mb-4">
        {t('selectModelDesc')}
      </p>

      <div className="form-grid mb-5">
        {models.map((model, idx) => {
          const brutalColors = ['var(--brutal-yellow)', 'var(--brutal-cyan)', 'var(--brutal-pink)'];
          const bgColor = brutalColors[idx % brutalColors.length];
          return (
          <div 
            key={model.id}
            className={`card model-card ${selectedModel === model.id ? 'selected' : 'card-colored'}`}
            style={{ '--brutal-bg': bgColor, backgroundColor: selectedModel === model.id ? '' : 'var(--brutal-bg)' }}
            onClick={() => onSelect(model.id)}
          >
            <div className="flex justify-between align-center mb-3">
              <h3 style={{ marginBottom: 0 }}>{model.name}</h3>
              {model.badge && (
                <span className={`badge ${model.recommended ? 'badge-primary' : ''}`}>
                  {model.badge}
                </span>
              )}
            </div>
            
            <p className="mb-3 text-bold" style={{ color: selectedModel === model.id ? 'inherit' : 'var(--color-text)' }}>
              {model.description}
            </p>
            
            <div className="mb-4">
              <div className="flex align-center gap-2 mb-1">
                <Check size={18} strokeWidth={3} style={{ color: selectedModel === model.id ? 'inherit' : 'var(--color-success)' }} />
                <span className="text-sm">{model.pros}</span>
              </div>
              <div className="flex align-center gap-2">
                <AlertCircle size={18} strokeWidth={3} style={{ color: selectedModel === model.id ? 'inherit' : 'var(--color-danger)' }} />
                <span className="text-sm">{model.cons}</span>
              </div>
            </div>
            
            <div className="flex align-center gap-2 text-sm text-bold mt-auto" style={{ borderTop: '2px solid', paddingTop: '12px', borderColor: selectedModel === model.id ? 'var(--bg-primary)' : 'var(--color-border)' }}>
              <Target size={18} strokeWidth={3} />
              {t('bestFor')} {model.best_for}
            </div>
          </div>
        )})}
      </div>
      
      <div className="flex gap-3">
        <button 
          className="btn btn-accent flex-1"
          onClick={onBack}
        >
          <ArrowLeft size={20} strokeWidth={3} /> {t('btnBack')}
        </button>
        <button 
          className="btn btn-primary"
          style={{ flex: 2 }}
          onClick={() => {
            if(!selectedModel) onSelect('logistic_regression')
            document.dispatchEvent(new CustomEvent('model-selected-continue'))
          }}
        >
          {t('btnContinue')} <ArrowRight size={20} strokeWidth={3} />
        </button>
      </div>
    </div>
  )
}

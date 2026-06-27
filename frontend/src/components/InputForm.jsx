import { useState, useEffect } from 'react'
import { ArrowLeft, ArrowRight, Activity, AlertTriangle } from 'lucide-react'
import { useLanguage } from '../LanguageContext'
import { useToast } from './Toast'

export default function InputForm({ selectedModel, onSubmit, onBack }) {
  const { lang, t } = useLanguage()
  const { showToast, ToastContainer } = useToast()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  const [formData, setFormData] = useState({
    model: selectedModel || 'logistic_regression',
    gender: '',
    age: '',
    hypertension: null,
    heart_disease: null,
    ever_married: '',
    work_type: '',
    residence_type: '',
    avg_glucose_level: '',
    bmi: '',
    smoking_status: ''
  })

  useEffect(() => {
    setFormData(prev => ({ ...prev, model: selectedModel || 'logistic_regression' }))
  }, [selectedModel])

  const [validationErrors, setValidationErrors] = useState({})

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (validationErrors[field]) {
      setValidationErrors(prev => ({ ...prev, [field]: null }))
    }
  }

  const validateStep = (currentStep) => {
    const errors = {}
    
    if (currentStep === 1) {
      if (!formData.gender) errors.gender = t('required')
      if (!formData.age || isNaN(formData.age) || formData.age <= 0 || formData.age > 120) {
        errors.age = t('ageInvalid')
      }
      if (!formData.ever_married) errors.ever_married = t('required')
    } 
    else if (currentStep === 2) {
      if (formData.hypertension === null) errors.hypertension = t('required')
      if (formData.heart_disease === null) errors.heart_disease = t('required')
    }
    else if (currentStep === 3) {
      if (!formData.work_type) errors.work_type = t('required')
      if (!formData.residence_type) errors.residence_type = t('required')
      if (!formData.smoking_status) errors.smoking_status = t('required')
    }
    else if (currentStep === 4) {
      if (!formData.avg_glucose_level || isNaN(formData.avg_glucose_level) || formData.avg_glucose_level <= 0) {
        errors.avg_glucose_level = t('glucoseInvalid')
      }
      if (!formData.bmi || isNaN(formData.bmi) || formData.bmi <= 0 || formData.bmi > 100) {
        errors.bmi = t('bmiInvalid')
      }
    }

    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleNext = () => {
    if (validateStep(step)) {
      setStep(s => s + 1)
      window.scrollTo(0, 0)
    }
  }

  const handleBack = () => {
    if (step > 1) {
      setStep(s => s - 1)
      window.scrollTo(0, 0)
    } else {
      onBack()
    }
  }

  const handleSubmit = async () => {
    if (!validateStep(4)) {
      showToast(t('errValidation'), 'warning')
      return
    }

    setLoading(true)
    setError(null)
    showToast(t('toastAnalyzing'), 'info', 8000)

    try {
      const payload = {
        ...formData,
        age: parseFloat(formData.age),
        avg_glucose_level: parseFloat(formData.avg_glucose_level),
        bmi: parseFloat(formData.bmi)
      }

      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 15000)

      const baseUrl = import.meta.env.VITE_API_URL || ''
      const res = await fetch(`${baseUrl}/api/predict?lang=${lang}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal,
      })
      clearTimeout(timeoutId)

      if (res.status === 503) {
        const msg = t('errModelNotReady')
        setError(msg)
        showToast(msg, 'error')
        return
      }
      if (res.status === 429) {
        const msg = t('errServerBusy')
        setError(msg)
        showToast(msg, 'warning')
        return
      }
      if (!res.ok) {
        const msg = t('errServerDown')
        setError(msg)
        showToast(msg, 'error')
        return
      }

      const data = await res.json()
      showToast(t('toastSuccess'), 'success', 2000)
      onSubmit(data)
    } catch (err) {
      let msg
      if (err.name === 'AbortError') {
        msg = t('errTimeout')
      } else if (err.message?.includes('fetch') || err.message?.includes('network') || err.message?.includes('Failed')) {
        msg = t('errServerDown')
      } else {
        msg = t('errUnknown')
      }
      setError(msg)
      showToast(msg, 'error')
    } finally {
      setLoading(false)
    }
  }

  const renderVisualIndicator = (value, type) => {
    if (!value || isNaN(value)) return null;
    const val = parseFloat(value);
    let min, max, safeMin, safeMax, unit;
    if (type === 'bmi') {
      min = 10; max = 50; safeMin = 18.5; safeMax = 24.9; unit = '';
    } else {
      min = 40; max = 300; safeMin = 70; safeMax = 140; unit = ' mg/dL';
    }

    const percent = Math.min(Math.max(((val - min) / (max - min)) * 100, 0), 100);
    const isSafe = val >= safeMin && val <= safeMax;
    const color = isSafe ? 'var(--color-success)' : (val > safeMax ? 'var(--color-danger)' : 'var(--color-warning)');
    const label = isSafe ? t('safeZone') : t('dangerZone');

    return (
      <div className="mt-2 animate-slide-up" style={{ padding: '8px', border: '2px solid var(--color-border)', backgroundColor: 'var(--bg-input)' }}>
        <div className="flex justify-between text-xs text-bold mb-1">
          <span style={{ color }}>{label}</span>
          <span>{val}{unit}</span>
        </div>
        <div style={{ height: '8px', width: '100%', backgroundColor: 'var(--color-border)', position: 'relative' }}>
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
            height: '16px',
            backgroundColor: color,
            border: '2px solid var(--bg-primary)',
            transition: 'all 0.3s ease'
          }} />
        </div>
      </div>
    )
  }

  const renderProgress = () => (
    <div className="mb-4">
      <div className="flex justify-between text-bold text-sm mb-1">
        <span>{t('step')} {step}/4</span>
        <span>{step === 1 ? t('step1') : step === 2 ? t('step2') : step === 3 ? t('step3') : t('step4')}</span>
      </div>
      <div className="progress-container">
        <div className="progress-fill" style={{ width: `${(step / 4) * 100}%` }}></div>
      </div>
    </div>
  )

  const renderError = (field) => {
    return validationErrors[field] ? (
      <div className="error-text">
        <AlertTriangle size={16} strokeWidth={3} /> {validationErrors[field]}
      </div>
    ) : null
  }

  return (
    <div className="px-container py-section animate-slide-up">
      <ToastContainer />
      {renderProgress()}
      
      {error && (
        <div className="info-box danger mb-4" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '12px' }}>
          <div className="flex align-center gap-3">
            <AlertTriangle size={24} strokeWidth={3} style={{ flexShrink: 0 }} />
            <span className="text-bold" style={{ fontSize: '1rem' }}>{error}</span>
          </div>
          <div className="flex gap-3" style={{ width: '100%' }}>
            <button
              className="btn btn-primary"
              style={{ flex: 1, padding: '10px', fontSize: '0.9rem' }}
              onClick={() => { setError(null); handleSubmit() }}
            >
              {t('btnRetry')}
            </button>
            <button
              className="btn"
              style={{ flex: 1, padding: '10px', fontSize: '0.9rem' }}
              onClick={() => window.location.reload()}
            >
              {t('btnReload')}
            </button>
          </div>
        </div>
      )}

      {/* STEP 1 */}
      <div className={`step-content ${step === 1 ? 'active' : 'hidden'}`} style={{ display: step === 1 ? 'block' : 'none' }}>
        <h2 className="mb-4">{t('step1')}</h2>
        
        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">{t('gender')}</label>
            <select 
              className={`form-control ${validationErrors.gender ? 'is-invalid' : ''}`}
              value={formData.gender}
              onChange={e => handleChange('gender', e.target.value)}
            >
              <option value="">{t('selectOption')}</option>
              <option value="Male">{t('genderMale')}</option>
              <option value="Female">{t('genderFemale')}</option>
            </select>
            {renderError('gender')}
          </div>

          <div className="form-group">
            <label className="form-label">{t('age')}</label>
            <input 
              type="number" 
              className={`form-control ${validationErrors.age ? 'is-invalid' : ''}`}
              value={formData.age}
              onChange={e => handleChange('age', e.target.value)}
              placeholder={t('agePlaceholder')}
              min="1" max="120"
            />
            {renderError('age')}
          </div>

          <div className="form-group full-width">
            <label className="form-label">{t('marital')}</label>
            <div className="pill-group">
              <button 
                className={`pill-btn ${formData.ever_married === 'Yes' ? 'active' : ''}`}
                onClick={() => handleChange('ever_married', 'Yes')}
              >{t('marriedYes')}</button>
              <button 
                className={`pill-btn ${formData.ever_married === 'No' ? 'active' : ''}`}
                onClick={() => handleChange('ever_married', 'No')}
              >{t('marriedNo')}</button>
            </div>
            {renderError('ever_married')}
          </div>
        </div>
      </div>

      {/* STEP 2 */}
      <div className={`step-content ${step === 2 ? 'active' : 'hidden'}`} style={{ display: step === 2 ? 'block' : 'none' }}>
        <h2 className="mb-4">{t('step2')}</h2>

        <div className="form-grid">
          <div className="form-group full-width">
            <label className="form-label">{t('hypertension')}</label>
            <div className="pill-group">
              <button 
                className={`pill-btn ${formData.hypertension === 1 ? 'active' : ''}`}
                onClick={() => handleChange('hypertension', 1)}
              >{t('yesHave')}</button>
              <button 
                className={`pill-btn ${formData.hypertension === 0 ? 'active' : ''}`}
                onClick={() => handleChange('hypertension', 0)}
              >{t('no')}</button>
            </div>
            {renderError('hypertension')}
          </div>

          <div className="form-group full-width">
            <label className="form-label">{t('heartDisease')}</label>
            <div className="pill-group">
              <button 
                className={`pill-btn ${formData.heart_disease === 1 ? 'active' : ''}`}
                onClick={() => handleChange('heart_disease', 1)}
              >{t('yesHave')}</button>
              <button 
                className={`pill-btn ${formData.heart_disease === 0 ? 'active' : ''}`}
                onClick={() => handleChange('heart_disease', 0)}
              >{t('no')}</button>
            </div>
            {renderError('heart_disease')}
          </div>
        </div>
      </div>

      {/* STEP 3 */}
      <div className={`step-content ${step === 3 ? 'active' : 'hidden'}`} style={{ display: step === 3 ? 'block' : 'none' }}>
        <h2 className="mb-4">{t('step3')}</h2>

        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">{t('workType')}</label>
            <select 
              className={`form-control ${validationErrors.work_type ? 'is-invalid' : ''}`}
              value={formData.work_type}
              onChange={e => handleChange('work_type', e.target.value)}
            >
              <option value="">{t('selectOption')}</option>
              <option value="Private">{t('workPrivate')}</option>
              <option value="Govt_job">{t('workGovt')}</option>
              <option value="Self-employed">{t('workSelf')}</option>
              <option value="Never_worked">{t('workNever')}</option>
              <option value="children">{t('workChild')}</option>
            </select>
            {renderError('work_type')}
          </div>

          <div className="form-group">
            <label className="form-label">{t('residence')}</label>
            <div className="pill-group">
              <button 
                className={`pill-btn ${formData.residence_type === 'Urban' ? 'active' : ''}`}
                onClick={() => handleChange('residence_type', 'Urban')}
              >{t('residenceUrban')}</button>
              <button 
                className={`pill-btn ${formData.residence_type === 'Rural' ? 'active' : ''}`}
                onClick={() => handleChange('residence_type', 'Rural')}
              >{t('residenceRural')}</button>
            </div>
            {renderError('residence_type')}
          </div>

          <div className="form-group full-width">
            <label className="form-label">{t('smoking')}</label>
            <select 
              className={`form-control ${validationErrors.smoking_status ? 'is-invalid' : ''}`}
              value={formData.smoking_status}
              onChange={e => handleChange('smoking_status', e.target.value)}
            >
              <option value="">{t('selectOption')}</option>
              <option value="never smoked">{t('smokeNever')}</option>
              <option value="formerly smoked">{t('smokeFormer')}</option>
              <option value="smokes">{t('smokeActive')}</option>
              <option value="Unknown">{t('smokeUnknown')}</option>
            </select>
            {renderError('smoking_status')}
          </div>
        </div>
      </div>

      {/* STEP 4 */}
      <div className={`step-content ${step === 4 ? 'active' : 'hidden'}`} style={{ display: step === 4 ? 'block' : 'none' }}>
        <h2 className="mb-4">{t('step4')}</h2>

        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">{t('glucose')}</label>
            <input 
              type="number" 
              className={`form-control ${validationErrors.avg_glucose_level ? 'is-invalid' : ''}`}
              value={formData.avg_glucose_level}
              onChange={e => handleChange('avg_glucose_level', e.target.value)}
              placeholder={t('glucosePlaceholder')}
              step="0.1"
            />
            <div className="text-bold text-xs mt-1" style={{color: 'var(--color-info)'}}>{t('glucoseNormal')}</div>
            {renderVisualIndicator(formData.avg_glucose_level, 'glucose')}
            {renderError('avg_glucose_level')}
          </div>

          <div className="form-group">
            <label className="form-label">{t('bmi')}</label>
            <input 
              type="number" 
              className={`form-control ${validationErrors.bmi ? 'is-invalid' : ''}`}
              value={formData.bmi}
              onChange={e => handleChange('bmi', e.target.value)}
              placeholder={t('bmiPlaceholder')}
              step="0.1"
            />
            <div className="text-bold text-xs mt-1" style={{color: 'var(--color-info)'}}>{t('bmiNormal')}</div>
            {renderVisualIndicator(formData.bmi, 'bmi')}
            {renderError('bmi')}
          </div>
        </div>
      </div>

      {/* Form Navigation */}
      <div className="form-actions mt-5 flex gap-3">
        <button 
          className="btn btn-accent flex-1"
          onClick={handleBack}
          disabled={loading}
        >
          <ArrowLeft size={20} strokeWidth={3} /> {t('btnBack')}
        </button>
        
        {step < 4 ? (
          <button 
            className="btn btn-primary"
            style={{ flex: 2 }}
            onClick={handleNext}
          >
            {t('btnNext')} <ArrowRight size={20} strokeWidth={3} />
          </button>
        ) : (
          <button 
            className="btn btn-primary"
            style={{ flex: 2 }}
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? t('btnProcess') : t('btnAnalyze')} <Activity size={20} strokeWidth={3} className={loading ? 'rotating' : ''}/>
          </button>
        )}
      </div>

    </div>
  )
}

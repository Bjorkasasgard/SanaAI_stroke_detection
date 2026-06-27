import Disclaimer from './Disclaimer'
import NewsSection from './NewsSection'
import { ArrowRight, Activity } from 'lucide-react'
import { useLanguage } from '../LanguageContext'

export default function LandingPage({ onStart }) {
  const { t } = useLanguage()

  return (
    <div className="px-container py-section animate-slide-up">
      <div className="split-layout">
        <div className="split-left">
          <h1 className="mb-3">
            {t('landingTitle1')}<br/>
            {t('landingTitle2')}<br/>
            {t('landingTitle3')}
          </h1>
          
          <p className="mb-4 text-lg">
            {t('landingDesc')}
          </p>

          <button className="btn btn-primary btn-block mb-4" onClick={onStart}>
            {t('btnStart')} <ArrowRight size={20} strokeWidth={3} />
          </button>
        </div>

        <div className="split-right">
          <div className="card" style={{ backgroundColor: 'var(--color-warning)', color: '#000', borderColor: '#000' }}>
            <div className="flex align-center gap-3 mb-2">
              <Activity size={32} strokeWidth={3} />
              <h2>{t('whoStats')}</h2>
            </div>
            <p className="text-bold" style={{ color: '#000' }}>
              {t('whoDesc')}
            </p>
          </div>
          
          <div className="mt-4">
            <Disclaimer />
          </div>
        </div>
      </div>
      
      <NewsSection />
    </div>
  )
}

import ThemeToggle from './ThemeToggle'
import { Activity, Globe } from 'lucide-react'
import { useLanguage } from '../LanguageContext'

export default function Header() {
  const { lang, setLang, t } = useLanguage()

  return (
    <header className="header">
      <div className="header-logo">
        <Activity size={28} strokeWidth={3} />
        <span className="header-logo-text">{t('appName')}</span>
      </div>
      <div className="flex align-center gap-2">
        <button 
          className="theme-toggle" 
          onClick={() => setLang(lang === 'id' ? 'en' : 'id')}
          title="Toggle Language"
          style={{ gap: '8px', padding: '8px 12px', fontWeight: 'bold' }}
        >
          <Globe size={20} strokeWidth={2.5} />
          {lang.toUpperCase()}
        </button>
        <ThemeToggle />
      </div>
    </header>
  )
}

import ThemeToggle from './ThemeToggle'
import { Activity, Globe } from 'lucide-react'
import { useLanguage } from '../LanguageContext'

function TelegramIcon({ size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M21.9 4.05L18.67 19.37C18.44 20.37 17.84 20.62 17.01 20.16L12.18 16.67L9.85 18.9C9.6 19.15 9.39 19.36 8.93 19.36L9.26 14.44L18.12 6.45C18.49 6.12 18.04 5.94 17.55 6.27L6.61 13.19L1.84 11.72C0.87 11.43 0.85 10.77 2.04 10.3L20.49 3.16C21.29 2.87 22.0 3.35 21.9 4.05Z"
        fill="currentColor"
      />
    </svg>
  )
}

export default function Header() {
  const { lang, setLang, t } = useLanguage()

  return (
    <header className="header">
      <div className="header-logo">
        <Activity size={28} strokeWidth={3} />
        <span className="header-logo-text">{t('appName')}</span>
      </div>
      <div className="flex align-center gap-2">
        <a 
          href="https://t.me/SanaaaAI_bot" 
          target="_blank" 
          rel="noopener noreferrer"
          className="theme-toggle"
          title="Sana AI Telegram Bot"
          style={{ padding: '8px', color: '#229ED9' }}
        >
          <TelegramIcon size={24} />
        </a>
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

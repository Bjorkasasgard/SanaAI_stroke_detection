import { AlertTriangle } from 'lucide-react'
import { useLanguage } from '../LanguageContext'

export default function Disclaimer() {
  const { t } = useLanguage()

  return (
    <div className="info-box danger mt-4">
      <AlertTriangle size={32} strokeWidth={3} />
      <div>
        <div className="text-bold text-lg mb-1">{t('disclaimerTitle')}</div>
        <div className="text-sm">
          {t('disclaimerDesc')}
        </div>
      </div>
    </div>
  )
}

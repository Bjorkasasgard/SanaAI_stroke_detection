import { useState } from 'react'
import { useLanguage } from '../LanguageContext'

// Telegram SVG icon (official Telegram plane logo)
function TelegramIcon({ size = 28 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M21.9 4.05L18.67 19.37C18.44 20.37 17.84 20.62 17.01 20.16L12.18 16.67L9.85 18.9C9.6 19.15 9.39 19.36 8.93 19.36L9.26 14.44L18.12 6.45C18.49 6.12 18.04 5.94 17.55 6.27L6.61 13.19L1.84 11.72C0.87 11.43 0.85 10.77 2.04 10.3L20.49 3.16C21.29 2.87 22.0 3.35 21.9 4.05Z"
        fill="currentColor"
      />
    </svg>
  )
}

export default function TelegramBubble({ botUsername = 'SanaAI_bot' }) {
  const { t } = useLanguage()
  const [hovered, setHovered] = useState(false)

  const telegramUrl = `https://t.me/${botUsername}`

  return (
    <div style={{
      position: 'fixed',
      bottom: '28px',
      right: '28px',
      zIndex: 999,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'flex-end',
      gap: '10px',
    }}>
      {/* Tooltip */}
      <div style={{
        backgroundColor: 'var(--color-text)',
        color: 'var(--bg-primary)',
        padding: '8px 14px',
        border: '3px solid var(--color-border)',
        boxShadow: '3px 3px 0px var(--color-border)',
        fontWeight: 700,
        fontSize: '0.85rem',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
        whiteSpace: 'nowrap',
        opacity: hovered ? 1 : 0,
        transform: hovered ? 'translateY(0px)' : 'translateY(6px)',
        transition: 'opacity 0.2s ease, transform 0.2s ease',
        pointerEvents: 'none',
      }}>
        {t ? t('telegramBot') || 'Analisis via Telegram Bot' : 'Analisis via Telegram Bot'}
      </div>

      {/* Bubble Button */}
      <a
        href={telegramUrl}
        target="_blank"
        rel="noopener noreferrer"
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        title="Gunakan Bot Telegram Sana AI"
        style={{
          width: '60px',
          height: '60px',
          backgroundColor: '#229ED9', // Telegram brand blue
          color: '#fff',
          border: '3px solid #000',
          boxShadow: hovered ? '2px 2px 0px #000' : '5px 5px 0px #000',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          textDecoration: 'none',
          transform: hovered ? 'translate(2px, 2px)' : 'translate(0, 0)',
          transition: 'transform 0.15s ease, box-shadow 0.15s ease',
          borderRadius: '0px', // Brutalism = no border radius
        }}
      >
        <TelegramIcon size={30} />
      </a>
    </div>
  )
}

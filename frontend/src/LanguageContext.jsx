import { createContext, useContext, useState, useEffect } from 'react'
import { translations } from './i18n/translations'

const LanguageContext = createContext()

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState(() => {
    return localStorage.getItem('sana-lang') || 'id'
  })

  useEffect(() => {
    localStorage.setItem('sana-lang', lang)
  }, [lang])

  const t = (key) => {
    return translations[lang]?.[key] || key
  }

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  return useContext(LanguageContext)
}

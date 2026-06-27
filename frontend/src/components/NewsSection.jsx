import { useState, useEffect } from 'react'
import { Newspaper, ArrowUpRight } from 'lucide-react'
import { useLanguage } from '../LanguageContext'

export default function NewsSection() {
  const { lang, t } = useLanguage()
  const [news, setNews] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    fetch(`/api/news?lang=${lang}`)
      .then(res => res.json())
      .then(data => {
        if (data.status === 'ok') {
          setNews(data.news)
        }
        setLoading(false)
      })
      .catch(err => {
        console.error("Error fetching news:", err)
        setLoading(false)
      })
  }, [lang])

  if (loading) {
    return (
      <div className="mt-5 p-4 card text-center">
        <span className="text-bold">{t('loadingNews')}</span>
      </div>
    )
  }

  if (news.length === 0) return null

  return (
    <div className="mt-5 pt-4" style={{ borderTop: 'var(--border-width) solid var(--color-border)' }}>
      <div className="flex align-center gap-2 mb-4">
        <Newspaper size={28} strokeWidth={3} />
        <h2 style={{ marginBottom: 0 }}>{t('newsTitle')}</h2>
      </div>

      <div className="form-grid">
        {news.map((item, idx) => (
          <div key={idx} className="card model-card" style={{ display: 'flex', flexDirection: 'column' }}>
            <h3 className="mb-2" style={{ fontSize: '1.1rem', lineHeight: '1.4' }}>{item.title}</h3>
            {item.summary && (
              <p className="text-sm text-muted mb-3" style={{ flexGrow: 1 }}>
                {item.summary.replace(/<[^>]+>/g, '')}
              </p>
            )}
            <a 
              href={item.link} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="btn btn-secondary mt-auto"
              style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', padding: '8px' }}
            >
              <span className="text-sm text-bold">{t('readMore')}</span>
              <ArrowUpRight size={16} strokeWidth={3} />
            </a>
          </div>
        ))}
      </div>
    </div>
  )
}

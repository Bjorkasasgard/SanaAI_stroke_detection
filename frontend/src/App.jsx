import { useState, useEffect } from 'react'
import { LanguageProvider } from './LanguageContext'
import Header from './components/Header'
import LandingPage from './components/LandingPage'
import ModelSelector from './components/ModelSelector'
import InputForm from './components/InputForm'
import ResultsPage from './components/ResultsPage'
import TelegramBubble from './components/TelegramBubble'

export default function App() {
  const [currentPage, setCurrentPage] = useState('landing') // landing, modelSelect, form, results
  const [selectedModel, setSelectedModel] = useState('logistic_regression')
  const [results, setResults] = useState(null)

  // Listen for custom event from ModelSelector
  useEffect(() => {
    const handleProceed = () => {
      setCurrentPage('form')
    }
    document.addEventListener('model-selected-continue', handleProceed)
    return () => document.removeEventListener('model-selected-continue', handleProceed)
  }, [])

  const renderPage = () => {
    switch (currentPage) {
      case 'landing':
        return <LandingPage onStart={() => setCurrentPage('modelSelect')} />
      case 'modelSelect':
        return (
          <ModelSelector 
            selectedModel={selectedModel} 
            onSelect={setSelectedModel}
            onBack={() => setCurrentPage('landing')}
          />
        )
      case 'form':
        return (
          <InputForm 
            selectedModel={selectedModel}
            onBack={() => setCurrentPage('modelSelect')}
            onSubmit={(data) => {
              setResults(data)
              setCurrentPage('results')
            }}
          />
        )
      case 'results':
        return (
          <ResultsPage 
            results={results} 
            onRestart={() => {
              setResults(null)
              setCurrentPage('modelSelect')
            }} 
          />
        )
      default:
        return <LandingPage onStart={() => setCurrentPage('modelSelect')} />
    }
  }

  return (
    <LanguageProvider>
      <div className="app-container">
        <Header />
        <main className="main-content">
          {renderPage()}
        </main>
        <TelegramBubble botUsername="SanaaaAI_bot" />
      </div>
    </LanguageProvider>
  )
}

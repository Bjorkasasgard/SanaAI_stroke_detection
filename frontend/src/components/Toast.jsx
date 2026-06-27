import { useEffect, useState } from 'react'
import { CheckCircle, AlertTriangle, XCircle, Info, X } from 'lucide-react'

/**
 * Toast notification system.
 * Usage: import { useToast } from './Toast'
 * const { showToast, ToastContainer } = useToast()
 * showToast('Something went wrong', 'error')  // 'success' | 'error' | 'warning' | 'info'
 */

export function useToast() {
  const [toasts, setToasts] = useState([])

  const showToast = (message, type = 'info', duration = 4000) => {
    const id = Date.now() + Math.random()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, duration)
  }

  const dismiss = (id) => setToasts(prev => prev.filter(t => t.id !== id))

  const ToastContainer = () => (
    <div style={{
      position: 'fixed',
      bottom: '100px',
      right: '24px',
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      gap: '10px',
      maxWidth: '340px',
      width: 'calc(100vw - 48px)',
    }}>
      {toasts.map(toast => (
        <ToastItem key={toast.id} toast={toast} onDismiss={dismiss} />
      ))}
    </div>
  )

  return { showToast, ToastContainer }
}

const TOAST_CONFIG = {
  success: { bg: 'var(--color-success)', Icon: CheckCircle, shadow: '#00B050' },
  error:   { bg: 'var(--color-danger)',  Icon: XCircle,     shadow: '#CC0000' },
  warning: { bg: 'var(--color-warning)', Icon: AlertTriangle, shadow: '#CC8800' },
  info:    { bg: 'var(--color-info)',    Icon: Info,         shadow: '#0044CC' },
}

function ToastItem({ toast, onDismiss }) {
  const [visible, setVisible] = useState(false)
  const cfg = TOAST_CONFIG[toast.type] || TOAST_CONFIG.info

  useEffect(() => {
    // Animate in
    requestAnimationFrame(() => setVisible(true))
  }, [])

  return (
    <div
      style={{
        backgroundColor: cfg.bg,
        border: '3px solid #000',
        boxShadow: `4px 4px 0px #000`,
        padding: '12px 14px',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '10px',
        color: '#000',
        fontFamily: 'var(--font-family)',
        fontWeight: 700,
        fontSize: '0.9rem',
        transform: visible ? 'translateX(0)' : 'translateX(120%)',
        opacity: visible ? 1 : 0,
        transition: 'transform 0.25s ease, opacity 0.25s ease',
        cursor: 'pointer',
      }}
      onClick={() => onDismiss(toast.id)}
    >
      <cfg.Icon size={20} strokeWidth={3} style={{ flexShrink: 0, marginTop: '1px' }} />
      <span style={{ flex: 1, lineHeight: 1.4 }}>{toast.message}</span>
      <X size={16} strokeWidth={3} style={{ flexShrink: 0, opacity: 0.7 }} />
    </div>
  )
}

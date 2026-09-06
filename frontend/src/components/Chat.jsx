import { useState, useRef, useEffect } from 'react'

const API_URL = 'http://localhost:8000'

function Chat() {

  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hello! I am your AI Agent 🤖\nHow can I help you today?' }
  ])
  const [input, setInput]     = useState('')
  const [loading, setLoading] = useState(false)
  const [hasPdf, setHasPdf]   = useState(false)
  const [hasDbFile, setHasDbFile] = useState(false)
  const bottomRef = useRef(null)

  // New message aate hi scroll down karo
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Message bhejo
  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMsg = input.trim()
    setInput('')
    setHasPdf(false)
    setHasDbFile(false)

    // User message add karo
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ query: userMsg })
      })

      const data = await res.json()

      setMessages(prev => [...prev, { role: 'ai', content: data.answer }])
      setHasPdf(data.has_pdf)
      setHasDbFile(data.has_db_file)

    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'ai',
        content: '❌ Server se connect nahi ho paya.\nMake sure FastAPI is running:\nuvicorn api.main:app --reload'
      }])
    } finally {
      setLoading(false)
    }
  }

  // Enter press karo to send
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // Textarea auto-resize
  const handleInput = (e) => {
    setInput(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
  }

  return (
    <div className="chat-container">

      {/* HEADER */}
      <div className="chat-header">
        <span className="bot-icon">🤖</span>
        <div className="header-text">
          <h1>AI Agent</h1>
        </div>
      </div>

      {/* MESSAGES */}
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="avatar">
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="bubble">
              <pre>{msg.content}</pre>
            </div>
          </div>
        ))}

        {/* LOADING DOTS */}
        {loading && (
          <div className="message ai">
            <div className="avatar">🤖</div>
            <div className="bubble loading">
              <span /><span /><span />
            </div>
          </div>
        )}

        {/* DOWNLOAD BUTTONS */}
        {(hasPdf || hasDbFile) && (
          <div className="downloads">
            {hasPdf && (
              <a href={`${API_URL}/download/pdf`} download className="download-btn">
                ⬇️ Download PDF
              </a>
            )}
            {hasDbFile && (
              <a href={`${API_URL}/download/db`} download className="download-btn">
                ⬇️ Download DB Result
              </a>
            )}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* INPUT AREA */}
      <div className="input-area">
        <textarea
          value={input}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
          rows={1}
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}>
          {loading ? '⏳' : '➤'}
        </button>
      </div>

    </div>
  )
}

export default Chat

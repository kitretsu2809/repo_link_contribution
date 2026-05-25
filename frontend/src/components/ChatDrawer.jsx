import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { startChat, sendChatMessage } from '../api';
import { useAuth } from '../contexts/AuthContext';

const mdComponents = {
  p: ({ children }) => <p style={{ marginBottom: '0.6rem', lineHeight: 1.65 }}>{children}</p>,
  strong: ({ children }) => <strong style={{ color: '#e2e8f0', fontWeight: 700 }}>{children}</strong>,
  em: ({ children }) => <em style={{ color: '#c4b5fd' }}>{children}</em>,
  code: ({ inline, children }) =>
    inline ? (
      <code style={{
        background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.3)',
        borderRadius: '4px', padding: '0.1rem 0.35rem', fontFamily: 'monospace',
        fontSize: '0.85em', color: '#a5b4fc',
      }}>{children}</code>
    ) : (
      <pre style={{
        background: 'rgba(0,0,0,0.35)', border: '1px solid var(--border)',
        borderRadius: '8px', padding: '0.85rem 1rem', overflowX: 'auto',
        marginBottom: '0.6rem',
      }}>
        <code style={{ fontFamily: 'monospace', fontSize: '0.82rem', color: '#cbd5e1' }}>{children}</code>
      </pre>
    ),
  ol: ({ children }) => <ol style={{ paddingLeft: '1.4rem', marginBottom: '0.6rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>{children}</ol>,
  ul: ({ children }) => <ul style={{ paddingLeft: '1.4rem', marginBottom: '0.6rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>{children}</ul>,
  li: ({ children }) => <li style={{ lineHeight: 1.6 }}>{children}</li>,
  h1: ({ children }) => <h3 style={{ color: '#e2e8f0', fontWeight: 700, marginBottom: '0.4rem', fontSize: '1rem' }}>{children}</h3>,
  h2: ({ children }) => <h4 style={{ color: '#e2e8f0', fontWeight: 700, marginBottom: '0.4rem', fontSize: '0.95rem' }}>{children}</h4>,
  h3: ({ children }) => <h5 style={{ color: '#e2e8f0', fontWeight: 600, marginBottom: '0.3rem', fontSize: '0.9rem' }}>{children}</h5>,
  blockquote: ({ children }) => (
    <blockquote style={{
      borderLeft: '3px solid rgba(99,102,241,0.6)', paddingLeft: '0.75rem',
      color: '#94a3b8', fontStyle: 'italic', marginBottom: '0.6rem',
    }}>{children}</blockquote>
  ),
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noopener noreferrer"
      style={{ color: '#a5b4fc', textDecoration: 'underline' }}>{children}</a>
  ),
  hr: () => <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '0.75rem 0' }} />,
};

export default function ChatDrawer({ issue, onClose }) {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (!issue) return;
    setMessages([]);
    setSessionId(null);
    setLoading(true);
    startChat(issue.id)
      .then(res => {
        setSessionId(res.session_id);
        setMessages([{ role: 'assistant', content: res.message }]);
      })
      .catch(e => setMessages([{ role: 'assistant', content: `Error: ${e.message}` }]))
      .finally(() => setLoading(false));
  }, [issue]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const send = async () => {
    if (!input.trim() || !sessionId || loading) return;
    const text = input.trim();
    setInput('');
    setMessages(m => [...m, { role: 'user', content: text }]);
    setLoading(true);
    try {
      const res = await sendChatMessage(sessionId, text);
      setMessages(m => [...m, { role: 'assistant', content: res.message }]);
    } catch (e) {
      setMessages(m => [...m, { role: 'assistant', content: `Error: ${e.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  if (!issue) return null;

  return (
    <div className="chat-drawer-overlay open" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="chat-drawer">
        <div className="chat-header">
          <div>
            <h3>🎓 Beginner Guide</h3>
            <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '2px' }}>
              Session saved • {user?.email}
            </p>
          </div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="chat-messages">
          {messages.map((m, i) => (
            <div key={i} className={`chat-msg ${m.role}`}>
              {m.role === 'assistant' ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
                  {m.content}
                </ReactMarkdown>
              ) : (
                m.content
              )}
            </div>
          ))}
          {loading && (
            <div className="chat-msg assistant">
              <span className="loading-dots">Thinking</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-area">
          <input
            className="chat-input"
            placeholder="Ask anything about this issue…"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && send()}
          />
          <button className="chat-send-btn" onClick={send} disabled={loading}>Send</button>
        </div>
      </div>
    </div>
  );
}

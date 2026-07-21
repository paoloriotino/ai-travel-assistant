import { useState, useRef, useCallback, type KeyboardEvent, type ChangeEvent } from 'react';
import './MessageInput.css';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
}

export default function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
    }
  }, []);

  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    adjustHeight();
  };

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText('');
    // Reset altezza textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const canSend = text.trim().length > 0 && !disabled;

  return (
    <div className="message-input">
      <textarea
        ref={textareaRef}
        className="message-input__textarea"
        value={text}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder="Racconta dove vorresti andare..."
        disabled={disabled}
        rows={1}
        aria-label="Scrivi un messaggio"
      />
      <button
        className="message-input__send"
        onClick={handleSend}
        disabled={!canSend}
        aria-label="Invia messaggio"
        title="Invia"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <line x1="12" y1="19" x2="12" y2="5"></line>
          <polyline points="5 12 12 5 19 12"></polyline>
        </svg>
      </button>
    </div>
  );
}

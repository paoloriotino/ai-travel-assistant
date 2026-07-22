import ReactMarkdown from 'react-markdown';
import type { Message } from '../types';
import './ChatMessage.css';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const timeString = message.timestamp.toLocaleTimeString('it-IT', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className={`chat-message chat-message--${message.role}`}>
      <div className="chat-message__avatar">
        {isUser ? 'U' : '🧭'}
      </div>
      <div>
        <div className="chat-message__bubble">
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <div className="chat-message__content">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>
        <div className="chat-message__time">{timeString}</div>
      </div>
    </div>
  );
}

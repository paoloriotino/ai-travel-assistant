import { useState, useEffect, useRef, useCallback, useMemo, type MouseEvent } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { sendMessage, resumeBooking, fetchChatHistory, fetchThreads, deleteThread } from '../services/api';
import type { Message, InterruptInfo, ThreadItem } from '../types';
import ChatMessage from './ChatMessage';
import MessageInput from './MessageInput';
import TypingIndicator from './TypingIndicator';
import BookingApprovalModal from './BookingApprovalModal';
import ChatSidebar from './ChatSidebar';
import ItineraryCanvas from './ItineraryCanvas';
import './ChatView.css';

const THREAD_KEY = 'travel-assistant-thread-id';

const WELCOME_MESSAGE: Message = {
  id: 'welcome',
  role: 'assistant',
  content:
    'Ciao! 🌍 Sono **TripAI**, il tuo assistente di viaggio personale. ' +
    'Raccontami dove vorresti andare, il tuo budget e le attività che ti interessano — ' +
    "mi occuperò di trovare voli, hotel ed esperienze perfette per te!",
  timestamp: new Date(),
};

function getOrCreateThreadId(): string {
  const stored = localStorage.getItem(THREAD_KEY);
  if (stored) return stored;
  const id = uuidv4();
  localStorage.setItem(THREAD_KEY, id);
  return id;
}

export default function ChatView() {
  const [messages, setMessages] = useState<Message[]>([WELCOME_MESSAGE]);
  const [threads, setThreads] = useState<ThreadItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isResuming, setIsResuming] = useState(false);
  const [interruptInfo, setInterruptInfo] = useState<InterruptInfo | null>(null);
  const [threadId, setThreadId] = useState(getOrCreateThreadId);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Calcola l'itinerario corrente più recente presente tra i messaggi
  const currentItinerary = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].structured_data?.itinerary) {
        return messages[i].structured_data!.itinerary!;
      }
    }
    return null;
  }, [messages]);

  // Caricamento dell'elenco delle sessioni salvate (sidebar)
  const loadThreadsList = useCallback(async () => {
    try {
      const data = await fetchThreads();
      setThreads(data);
    } catch (err) {
      console.warn('Impossibile caricare l\'elenco dei thread:', err);
    }
  }, []);

  useEffect(() => {
    loadThreadsList();
  }, [loadThreadsList]);

  // Caricamento storico messaggi dal backend per il threadId attivo
  useEffect(() => {
    let isMounted = true;
    async function loadHistory() {
      try {
        const historyRes = await fetchChatHistory(threadId);
        if (isMounted && historyRes.messages && historyRes.messages.length > 0) {
          const loadedMessages: Message[] = historyRes.messages.map((item, index) => ({
            id: `history-${index}`,
            role: item.role,
            content: item.content,
            timestamp: new Date(),
            structured_data: item.structured_data,
          }));
          setMessages(loadedMessages);
        } else if (isMounted) {
          setMessages([{ ...WELCOME_MESSAGE, id: uuidv4(), timestamp: new Date() }]);
        }
      } catch (err) {
        console.warn('Nessuna cronologia salvata per questo thread:', err);
        if (isMounted) {
          setMessages([{ ...WELCOME_MESSAGE, id: uuidv4(), timestamp: new Date() }]);
        }
      }
    }
    loadHistory();
    return () => {
      isMounted = false;
    };
  }, [threadId]);

  // Auto-scroll all'ultimo messaggio
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  const handleSend = async (text: string) => {
    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendMessage(text, threadId);

      const assistantMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: response.reply,
        timestamp: new Date(),
        structured_data: response.structured_data,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      if (response.interrupted && response.interrupt_info) {
        setInterruptInfo(response.interrupt_info);
      }

      // Aggiorna l'elenco dei thread nella sidebar per riflettere il primo messaggio/titolo
      loadThreadsList();
    } catch (err) {
      const errorMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: `⚠️ Si è verificato un errore: ${err instanceof Error ? err.message : 'Errore sconosciuto'}. Riprova tra poco.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async () => {
    setIsResuming(true);
    try {
      const response = await resumeBooking(threadId, true);
      const assistantMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: response.reply,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: `⚠️ Errore durante la conferma: ${err instanceof Error ? err.message : 'Errore sconosciuto'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setInterruptInfo(null);
      setIsResuming(false);
    }
  };

  const handleReject = async () => {
    setIsResuming(true);
    try {
      const response = await resumeBooking(threadId, false);
      const assistantMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: response.reply,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: `⚠️ Errore durante l'annullamento: ${err instanceof Error ? err.message : 'Errore sconosciuto'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setInterruptInfo(null);
      setIsResuming(false);
    }
  };

  const handleSelectThread = (selectedId: string) => {
    localStorage.setItem(THREAD_KEY, selectedId);
    setThreadId(selectedId);
    setInterruptInfo(null);
  };

  const handleDeleteThread = async (targetId: string, e: MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Vuoi davvero eliminare questa conversazione dallo storico?')) {
      return;
    }

    try {
      await deleteThread(targetId);
      setThreads((prev) => prev.filter((t) => t.thread_id !== targetId));

      if (targetId === threadId) {
        handleNewChat();
      }
    } catch (err) {
      alert(`Errore durante l'eliminazione: ${err instanceof Error ? err.message : 'Errore sconosciuto'}`);
    }
  };

  const handleNewChat = () => {
    const newId = uuidv4();
    localStorage.setItem(THREAD_KEY, newId);
    setThreadId(newId);
    setMessages([{ ...WELCOME_MESSAGE, id: uuidv4(), timestamp: new Date() }]);
    setInterruptInfo(null);
    setIsLoading(false);
  };

  return (
    <div className="chat-view">
      <ChatSidebar
        threads={threads}
        activeThreadId={threadId}
        onSelectThread={handleSelectThread}
        onDeleteThread={handleDeleteThread}
        onNewChat={handleNewChat}
      />

      <div className="chat-view__main">
        <div className="chat-view__messages">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}

          {isLoading && <TypingIndicator />}

          <div ref={messagesEndRef} />
        </div>

        {(() => {
          const lastMsg = messages[messages.length - 1];
          const questions = lastMsg?.role === 'assistant' ? lastMsg.structured_data?.follow_up_questions : [];
          if (!questions || questions.length === 0) return null;

          return (
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', padding: '0 1.5rem 0.5rem 1.5rem' }}>
              {questions.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(q)}
                  disabled={isLoading || interruptInfo !== null}
                  style={{
                    background: 'rgba(240, 165, 0, 0.12)',
                    color: 'var(--color-golden-hour)',
                    border: '1px solid rgba(240, 165, 0, 0.35)',
                    borderRadius: '20px',
                    padding: '8px 16px',
                    fontSize: '0.92rem',
                    fontWeight: 500,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                  }}
                >
                  ⚡ {q}
                </button>
              ))}
            </div>
          );
        })()}

        <MessageInput onSend={handleSend} disabled={isLoading || interruptInfo !== null} />
      </div>

      <ItineraryCanvas itinerary={currentItinerary} />

      {interruptInfo && (
        <BookingApprovalModal
          interruptInfo={interruptInfo}
          onApprove={handleApprove}
          onReject={handleReject}
          isLoading={isResuming}
        />
      )}
    </div>
  );
}

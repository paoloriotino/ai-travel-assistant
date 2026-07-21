import type { MouseEvent } from 'react';
import type { ThreadItem } from '../types';
import './ChatSidebar.css';

interface ChatSidebarProps {
  threads: ThreadItem[];
  activeThreadId: string;
  onSelectThread: (threadId: string) => void;
  onDeleteThread: (threadId: string, e: MouseEvent) => void;
  onNewChat: () => void;
}

export default function ChatSidebar({
  threads,
  activeThreadId,
  onSelectThread,
  onDeleteThread,
  onNewChat,
}: ChatSidebarProps) {
  return (
    <aside className="chat-sidebar">
      <div className="chat-sidebar__header">
        <button className="chat-sidebar__new-btn" onClick={onNewChat}>
          <span>✦</span> Nuova chat
        </button>
      </div>

      <div className="chat-sidebar__section-title">Storico conversazioni</div>

      <div className="chat-sidebar__list">
        {threads.length === 0 ? (
          <div className="chat-sidebar__empty">Nessuna chat salvata</div>
        ) : (
          threads.map((item) => {
            const isActive = item.thread_id === activeThreadId;
            return (
              <div
                key={item.thread_id}
                className={`chat-sidebar__item ${isActive ? 'chat-sidebar__item--active' : ''}`}
                onClick={() => onSelectThread(item.thread_id)}
                title={item.title}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') onSelectThread(item.thread_id);
                }}
              >
                <span className="chat-sidebar__item-text">{item.title}</span>
                <button
                  className="chat-sidebar__delete-btn"
                  onClick={(e) => onDeleteThread(item.thread_id, e)}
                  title="Elimina conversazione"
                  aria-label="Elimina conversazione"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  </svg>
                </button>
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
}

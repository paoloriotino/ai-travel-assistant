/* ═══════════════════════════════════════════════════════
   Servizio API — Comunicazione con il backend FastAPI
   ═══════════════════════════════════════════════════════ */

import type { ChatResponse, Booking, ChatHistoryResponse, ThreadItem } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const TOKEN_KEY = 'travel_assistant_token';

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function getLoggedUsername(): string | null {
  const token = getToken();
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.username || null;
  } catch (e) {
    return null;
  }
}

function getHeaders(): HeadersInit {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  };
}

export async function register(username: string, password: string) {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Errore di registrazione' }));
    throw new Error(error.detail || `Errore ${res.status}`);
  }
  return res.json();
}

export async function login(username: string, password: string) {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Credenziali non valide' }));
    throw new Error(error.detail || `Errore ${res.status}`);
  }
  return res.json();
}


/**
 * Invia un messaggio all'agente conversazionale.
 * @param message - Testo del messaggio utente
 * @param threadId - UUID della sessione di conversazione
 */
export async function sendMessage(
  message: string,
  threadId: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ message, thread_id: threadId }),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Errore di rete' }));
    throw new Error(error.detail || `Errore ${res.status}`);
  }

  return res.json();
}

/**
 * Recupera l'elenco delle sessioni chat salvate dal backend.
 */
export async function fetchThreads(): Promise<ThreadItem[]> {
  const res = await fetch(`${API_BASE}/api/chat/threads`, { headers: getHeaders() });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Errore di rete' }));
    throw new Error(error.detail || `Errore ${res.status}`);
  }

  return res.json();
}

/**
 * Elimina una sessione di chat dallo storico nel backend.
 */
export async function deleteThread(threadId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/chat/threads/${threadId}`, {
    method: 'DELETE',
    headers: getHeaders(),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Errore durante l\'eliminazione' }));
    throw new Error(error.detail || `Errore ${res.status}`);
  }
}



/**
 * Recupera la cronologia dei messaggi salvata per uno specifico thread_id.
 */
export async function fetchChatHistory(
  threadId: string
): Promise<ChatHistoryResponse> {
  const res = await fetch(`${API_BASE}/api/chat/history/${threadId}`, { headers: getHeaders() });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Errore di rete' }));
    throw new Error(error.detail || `Errore ${res.status}`);
  }

  return res.json();
}

/**
 * Approva o rifiuta una prenotazione in attesa di conferma (Human-in-the-Loop).
 * @param threadId - UUID della sessione interrotta
 * @param approve - true per confermare, false per annullare
 */
export async function resumeBooking(
  threadId: string,
  approve: boolean
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat/resume`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ thread_id: threadId, approve }),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Errore di rete' }));
    throw new Error(error.detail || `Errore ${res.status}`);
  }

  return res.json();
}

/**
 * Recupera lo storico delle prenotazioni dell'utente.
 */
export async function fetchBookings(): Promise<Booking[]> {
  const res = await fetch(`${API_BASE}/api/bookings`, { headers: getHeaders() });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Errore di rete' }));
    throw new Error(error.detail || `Errore ${res.status}`);
  }

  return res.json();
}

/**
 * Annulla una prenotazione esistente.
 */
export async function cancelBooking(bookingId: number): Promise<void> {
  const res = await fetch(`${API_BASE}/api/bookings/${bookingId}`, {
    method: 'DELETE',
    headers: getHeaders(),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Errore durante la cancellazione' }));
    throw new Error(error.detail || `Errore ${res.status}`);
  }
}


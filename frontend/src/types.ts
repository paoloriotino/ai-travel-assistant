/* ═══════════════════════════════════════════════════════
   Tipi TypeScript — AI Travel Assistant Frontend
   ═══════════════════════════════════════════════════════ */

/** Request body per POST /api/chat */
export interface ChatRequest {
  message: string;
  thread_id: string;
}

/** Informazioni sull'interruzione Human-in-the-Loop */
export interface InterruptInfo {
  tool_name: string;
  tool_args: Record<string, unknown>;
}

export interface DayItinerary {
  day: number;
  title: string;
  activities: string[];
}

export interface StructuredItinerary {
  destination: string;
  duration_days?: number;
  flight_summary?: string;
  hotel_summary?: string;
  estimated_total_price?: number;
  daily_plan: DayItinerary[];
}

export interface AgentStructuredResponse {
  reply: string;
  itinerary?: StructuredItinerary | null;
  follow_up_questions?: string[];
}

/** Response body da POST /api/chat e POST /api/chat/resume */
export interface ChatResponse {
  reply: string;
  thread_id: string;
  interrupted: boolean;
  interrupt_info: InterruptInfo | null;
  structured_data?: AgentStructuredResponse | null;
}

/** Request body per POST /api/chat/resume */
export interface ResumeRequest {
  thread_id: string;
  approve: boolean;
}

/** Singolo messaggio nella UI della chat */
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  structured_data?: AgentStructuredResponse | null;
}

/** Dettagli dell'itinerario di una prenotazione */
export interface BookingDetails {
  flight: string;
  hotel: string;
  activities: string;
  traveler: string;
}

/** Prenotazione restituita da GET /api/bookings */
export interface Booking {
  id: number;
  status: string;
  total_price: number;
  details: BookingDetails;
}

/** Elemento nella storia chat restituito da GET /api/chat/history/{thread_id} */
export interface ChatHistoryItem {
  role: 'user' | 'assistant';
  content: string;
  structured_data?: AgentStructuredResponse | null;
}

/** Risposta da GET /api/chat/history/{thread_id} */
export interface ChatHistoryResponse {
  thread_id: string;
  messages: ChatHistoryItem[];
}

/** Sessione di chat salvata restituita da GET /api/chat/threads */
export interface ThreadItem {
  thread_id: string;
  title: string;
  last_message: string;
}



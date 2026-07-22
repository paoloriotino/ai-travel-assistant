"""
Modelli Pydantic per le request e response dell'API di chat.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ChatRequest(BaseModel):
    """Request body per l'endpoint di chat."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Il messaggio dell'utente da inviare all'assistente di viaggio.",
        examples=["Cerco un volo da Roma a Tokyo per agosto"]
    )
    thread_id: str = Field(
        ...,
        description="Identificativo univoco della sessione di conversazione per mantenere il contesto.",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )


class MessageRole(str, Enum):
    """Ruolo del messaggio nella conversazione."""
    USER = "user"
    ASSISTANT = "assistant"





class InterruptInfo(BaseModel):
    """Informazioni sullo stato di interruzione dell'agente (Human-in-the-loop)."""
    tool_name: str = Field(
        ...,
        description="Nome del tool che ha richiesto l'approvazione umana."
    )
    tool_args: dict = Field(
        default_factory=dict,
        description="Argomenti passati al tool in attesa di approvazione."
    )


class DayItinerary(BaseModel):
    """Itinerario per una specifica giornata del viaggio."""
    day: int = Field(description="Numero progressivo del giorno (es. 1, 2, 3).")
    title: str = Field(description="Titolo sintetico delle attività del giorno.")
    activities: List[str] = Field(default_factory=list, description="Lista delle attività e luoghi da visitare.")


class NightStay(BaseModel):
    """Soggiorno in hotel relativo a una notte specifica del viaggio."""
    night: int = Field(description="Numero progressivo della notte del viaggio.")
    hotel_summary: str = Field(description="Riepilogo dell'hotel o della sistemazione per quella notte.")


class TravelRequirements(BaseModel):
    """Requisiti di viaggio estratti progressivamente dalla conversazione."""
    budget_total: Optional[float] = Field(
        None,
        description="Budget totale disponibile per il viaggio in EUR.",
    )
    destination_country: Optional[str] = Field(
        None,
        description="Nazione o area geografica di interesse.",
    )
    preferred_activities: List[str] = Field(
        default_factory=list,
        description="Preferenze sulle attività espresse dall'utente (cultura, relax, nightlife, ecc.).",
    )
    travel_month: Optional[str] = Field(
        None,
        description="Periodo di viaggio espresso come mese o finestra temporale.",
    )


class StructuredItinerary(BaseModel):
    """Dettagli strutturati dell'itinerario o proposta di viaggio."""
    destination: str = Field(description="Città o paese di destinazione.")
    duration_days: Optional[int] = Field(None, description="Durata del soggiorno in giorni.")
    flight_outbound_summary: Optional[str] = Field(None, description="Sintesi del volo di andata selezionato o consigliato.")
    flight_return_summary: Optional[str] = Field(None, description="Sintesi del volo di ritorno selezionato o consigliato.")
    hotel_summary: Optional[str] = Field(None, description="Sintesi dell'hotel consigliato o selezionato.")
    nightly_stays: List[NightStay] = Field(default_factory=list, description="Lista dei pernottamenti con riepilogo hotel per ogni notte.")
    estimated_total_price: Optional[float] = Field(None, description="Prezzo totale stimato del pacchetto in EUR.")
    daily_plan: List[DayItinerary] = Field(default_factory=list, description="Piano dettagliato giorno per giorno.")


class AgentStructuredResponse(BaseModel):
    """Schema di output strutturato dell'agente di viaggio."""
    reply: str = Field(..., description="La risposta conversazionale principale in formato Markdown per l'utente.")
    requirements: Optional[TravelRequirements] = Field(
        None,
        description="Requisiti utente estratti e aggiornati in modo incrementale durante la conversazione.",
    )
    itinerary: Optional[StructuredItinerary] = Field(None, description="Dettagli strutturati dell'itinerario, popolati se si propone un piano o dettagli di viaggio.")
    follow_up_questions: List[str] = Field(default_factory=list, description="2-3 risposte o azioni rapide pronte all'uso che L'UTENTE può inviare all'assistente con un click (es. 'Cerca voli per Tokyo', 'Procedi con la prenotazione'). NON inserire domande rivolte all'utente!")


class ChatMessage(BaseModel):
    """Singolo messaggio nella conversazione."""
    role: MessageRole = Field(
        ...,
        description="Ruolo dell'autore del messaggio."
    )
    content: str = Field(
        ...,
        description="Contenuto testuale del messaggio."
    )
    structured_data: Optional[AgentStructuredResponse] = Field(
        default=None,
        description="Dati strutturati associati al messaggio se generati dall'assistente."
    )


class ChatResponse(BaseModel):
    """Response body dell'endpoint di chat."""
    reply: str = Field(
        ...,
        description="La risposta generata dall'assistente di viaggio."
    )
    thread_id: str = Field(
        ...,
        description="L'identificativo della sessione, lo stesso ricevuto nella request."
    )
    interrupted: bool = Field(
        default=False,
        description="Indica se l'agente è in stato di interruzione e attende approvazione umana."
    )
    interrupt_info: Optional[InterruptInfo] = Field(
        default=None,
        description="Dettagli sull'interruzione, presenti solo se 'interrupted' è True."
    )
    structured_data: Optional[AgentStructuredResponse] = Field(
        default=None,
        description="Dati strutturati opzionali generati dall'agente (itinerario e prompt veloci)."
    )


class ResumeRequest(BaseModel):
    """Request body per approvare o rifiutare un'azione dell'agente in attesa di approvazione."""
    thread_id: str = Field(
        ...,
        description="Identificativo della sessione di conversazione in stato di interruzione."
    )
    approve: bool = Field(
        ...,
        description="True per approvare l'azione, False per rifiutarla."
    )


class BookingResponse(BaseModel):
    """Singola prenotazione restituita dall'endpoint bookings."""
    id: int = Field(..., description="ID univoco della prenotazione.")
    status: str = Field(..., description="Stato della prenotazione (pending, confirmed, cancelled).")
    total_price: float = Field(..., description="Prezzo totale della prenotazione in EUR.")
    details: dict = Field(..., description="Dettagli dell'itinerario (volo, hotel, attività, viaggiatore).")


class ChatHistoryResponse(BaseModel):
    """Response body per lo storico dei messaggi di un thread."""
    thread_id: str = Field(..., description="ID della sessione di chat.")
    messages: list[ChatMessage] = Field(default_factory=list, description="Lista dei messaggi della conversazione.")


class ThreadItem(BaseModel):
    """Informazioni su una sessione di chat salvata."""
    thread_id: str = Field(..., description="ID univoco del thread.")
    title: str = Field(..., description="Titolo sintetico estratto dal primo messaggio utente.")
    last_message: str = Field(default="", description="Estratto dell'ultimo messaggio.")

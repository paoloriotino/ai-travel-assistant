"""
API routes per la chat con l'assistente di viaggio.
"""

import json

from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends

from backend.app.database import SessionLocal, Booking, User
from backend.app.api.auth import get_current_user
from backend.app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ResumeRequest,
    InterruptInfo,
    BookingResponse,
    ChatHistoryResponse,
    ChatMessage,
    ThreadItem,
)
from backend.app.agents.travel_agent import (
    invoke_agent,
    resume_agent,
    get_chat_history,
    get_all_threads,
    delete_thread,
)

router = APIRouter(prefix="/api", tags=["Chat"])


@router.get(
    "/chat/threads",
    response_model=list[ThreadItem],
    summary="Recupera tutte le sessioni di chat attive",
    description="Restituisce la lista di tutte le conversazioni salvate su SQLite con titolo e ultimo messaggio.",
)
async def list_threads(user: User = Depends(get_current_user)) -> list[ThreadItem]:
    """Endpoint per recuperare l'elenco delle sessioni chat."""
    try:
        raw_threads = get_all_threads(user.id)
        return [
            ThreadItem(
                thread_id=t["thread_id"],
                title=t["title"],
                last_message=t["last_message"],
            )
            for t in raw_threads
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Errore nel recupero dei thread: {str(e)}"
        )


@router.delete(
    "/chat/threads/{thread_id}",
    summary="Elimina una sessione di chat dallo storico",
    description="Rimuove tutti i messaggi e lo stato salvato per un determinato thread_id dal database SQLite.",
)
async def remove_thread(thread_id: str, user: User = Depends(get_current_user)):
    """Endpoint per eliminare una conversazione salvata."""
    success = delete_thread(thread_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Thread non trovato o già eliminato")
    return {"status": "deleted", "thread_id": thread_id}




@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Invia un messaggio all'assistente di viaggio",
    description=(
        "Invia un messaggio in linguaggio naturale all'assistente di viaggio AI. "
        "L'agente utilizzerà automaticamente i tool di ricerca per trovare voli, hotel "
        "e attività, e risponderà con informazioni contestuali. "
        "Fornire lo stesso `thread_id` per mantenere il contesto della conversazione."
    ),
)
async def chat(request: ChatRequest, user: User = Depends(get_current_user)) -> ChatResponse:
    """Endpoint principale di conversazione con l'agente."""
    try:
        result = invoke_agent(
            message=request.message,
            thread_id=str(request.thread_id),
            user_id=user.id,
        )

        interrupt_info = None
        if result.get("interrupted") and result.get("interrupt_info"):
            interrupt_info = InterruptInfo(
                tool_name=result["interrupt_info"]["tool_name"],
                tool_args=result["interrupt_info"].get("tool_args", {}),
            )

        return ChatResponse(
            reply=result["reply"],
            thread_id=request.thread_id,
            interrupted=result.get("interrupted", False),
            interrupt_info=interrupt_info,
            structured_data=result.get("structured_data"),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Errore di configurazione: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante l'elaborazione: {str(e)}"
        )


@router.get(
    "/chat/history/{thread_id}",
    response_model=ChatHistoryResponse,
    summary="Recupera la cronologia messaggi di un thread",
    description="Restituisce la lista di tutti i messaggi utente e assistente salvati su SQLite per un dato thread_id.",
)
async def chat_history(thread_id: str, user: User = Depends(get_current_user)) -> ChatHistoryResponse:
    """Endpoint per recuperare la cronologia messaggi di una sessione."""
    try:
        raw_history = get_chat_history(thread_id, user.id)
        messages = [
            ChatMessage(
                role=msg["role"],
                content=msg["content"],
                structured_data=msg.get("structured_data"),
            )
            for msg in raw_history
        ]
        return ChatHistoryResponse(thread_id=thread_id, messages=messages)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Errore nel recupero della cronologia: {str(e)}"
        )



@router.post(
    "/chat/resume",
    response_model=ChatResponse,
    summary="Approva o rifiuta un'azione dell'agente",
    description=(
        "Riprende l'esecuzione dell'agente dopo un'interruzione Human-in-the-loop. "
        "Usa questo endpoint quando l'agente è in attesa di approvazione per un'azione "
        "sensibile come la prenotazione di un viaggio (tool `book_trip`)."
    ),
)
async def resume_chat(request: ResumeRequest, user: User = Depends(get_current_user)) -> ChatResponse:
    """Endpoint per approvare/rifiutare una prenotazione in attesa."""
    try:
        result = resume_agent(
            thread_id=str(request.thread_id),
            approve=request.approve,
            user_id=user.id,
        )

        return ChatResponse(
            reply=result["reply"],
            thread_id=request.thread_id,
            interrupted=result.get("interrupted", False),
            interrupt_info=None,
            structured_data=result.get("structured_data"),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Errore di configurazione: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante il resume: {str(e)}"
        )


@router.get(
    "/bookings",
    response_model=list[BookingResponse],
    summary="Recupera lo storico delle prenotazioni",
    description=(
        "Restituisce tutte le prenotazioni dell'utente corrente (demo: user_id=1). "
        "Ogni prenotazione include i dettagli dell'itinerario completo."
    ),
)
async def get_bookings(user: User = Depends(get_current_user)) -> list[BookingResponse]:
    """Endpoint per recuperare lo storico delle prenotazioni dell'utente corrente."""
    db = SessionLocal()
    try:
        bookings = (
            db.query(Booking)
            .filter(Booking.user_id == user.id)
            .order_by(Booking.id.desc())
            .all()
        )
        return [
            BookingResponse(
                id=b.id,
                status=b.status,
                total_price=b.total_price,
                details=json.loads(b.details_json),
            )
            for b in bookings
        ]
    finally:
        db.close()


@router.delete(
    "/bookings/{booking_id}",
    summary="Annulla una prenotazione",
    description="Imposta lo stato di una prenotazione su 'cancelled'.",
)
async def cancel_booking(booking_id: int, user: User = Depends(get_current_user)):
    """Endpoint per annullare una prenotazione esistente."""
    db = SessionLocal()
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == user.id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Prenotazione non trovata")
        booking.status = "cancelled"
        db.commit()
        return {"status": "cancelled", "id": booking_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore durante l'annullamento: {str(e)}")
    finally:
        db.close()


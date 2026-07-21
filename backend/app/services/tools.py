"""
Tool LangChain per l'agente di viaggio.

Ogni tool è decorato con @tool e fornisce docstring dettagliate (inclusi Args)
affinché l'LLM sappia quando e come invocarli autonomamente.
"""

import datetime
from typing import Optional
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from backend.app.database import SessionLocal, Flight, Hotel, Booking
from backend.app.rag.vector_db import query_activities


@tool
def search_activities(query: str, city: Optional[str] = None, max_price: Optional[float] = None, limit: int = 5) -> str:
    """Cerca attività, esperienze e tour disponibili nelle destinazioni di viaggio usando la ricerca semantica.

    Usa questo strumento quando l'utente chiede informazioni su cosa fare in una destinazione,
    esperienze da vivere, tour, escursioni, attività sportive, culturali, gastronomiche o di relax.
    È in grado di comprendere richieste in linguaggio naturale come "attività romantiche a Parigi"
    o "avventure nella natura in Islanda".

    Args:
        query: La descrizione in linguaggio naturale di ciò che l'utente cerca.
              Esempi: "esperienze gastronomiche", "avventura nella natura", "attività per famiglie".
        city: Nome opzionale della città per filtrare i risultati (es. "Tokyo", "Paris", "Rome").
        max_price: Prezzo massimo opzionale in EUR per filtrare le attività accessibili.
        limit: Numero massimo di risultati da restituire (default: 5).
    """
    filters = {}
    if city:
        filters["city"] = city
    if max_price is not None:
        filters["price"] = {"$lte": max_price}

    chroma_filters = filters if filters else None
    results = query_activities(query=query, limit=limit, filters=chroma_filters)

    if not results:
        return "Nessuna attività trovata per la tua ricerca. Prova con criteri diversi."

    output_lines = []
    for i, doc in enumerate(results, 1):
        meta = doc.metadata
        output_lines.append(
            f"{i}. **{meta.get('title', 'N/A')}** — {meta.get('city', '?')}, {meta.get('country', '?')}\n"
            f"   Prezzo: €{meta.get('price', '?')} | Target: {meta.get('target_audience', 'N/A')}\n"
            f"   Mesi disponibili: {meta.get('available_months', 'N/A')}\n"
            f"   {doc.page_content.split('Descrizione: ')[-1].split(chr(10))[0] if 'Descrizione: ' in doc.page_content else ''}"
        )
    return "\n\n".join(output_lines)


@tool
def search_flights(
    departure_airport: Optional[str] = None,
    arrival_airport: Optional[str] = None,
    departure_month: Optional[int] = None,
    max_price: Optional[float] = None,
    limit: int = 5,
) -> str:
    """Cerca voli disponibili nel database tra aeroporti e date specifiche.

    Usa questo strumento quando l'utente chiede informazioni su voli, trasporto aereo,
    biglietti aerei o come raggiungere una destinazione in aereo.
    Sono disponibili voli verso oltre 40 destinazioni globali. I codici aeroporto delle mete
    principali includono: FCO (Roma), MXP (Milano), HND (Tokyo), CDG (Parigi), JFK (New York), 
    LHR (Londra), KEF (Reykjavik), SYD (Sydney), BCN (Barcellona), BKK (Bangkok), DXB (Dubai), 
    DPS (Bali), SIN (Singapore), ICN (Seul), MIA (Miami), LAX (Los Angeles), e molti altri.

    Args:
        departure_airport: Codice IATA dell'aeroporto di partenza (es. "FCO", "MXP").
                          Se non specificato, cerca da tutti gli aeroporti.
        arrival_airport: Codice IATA dell'aeroporto di arrivo (es. "HND", "JFK").
                        Se non specificato, cerca verso tutte le destinazioni.
        departure_month: Mese di partenza desiderato (1-12) per filtrare i voli.
        max_price: Prezzo massimo del biglietto in EUR.
        limit: Numero massimo di risultati da restituire (default: 5).
    """
    db = SessionLocal()
    try:
        q = db.query(Flight)
        if departure_airport:
            q = q.filter(Flight.departure_airport == departure_airport.upper())
        if arrival_airport:
            q = q.filter(Flight.arrival_airport == arrival_airport.upper())
        if departure_month:
            from sqlalchemy import extract
            q = q.filter(extract("month", Flight.departure_date) == departure_month)
        if max_price is not None:
            q = q.filter(Flight.price <= max_price)

        q = q.filter(Flight.availability > 0)
        flights = q.order_by(Flight.price.asc()).limit(limit).all()

        if not flights:
            return "Nessun volo trovato con i criteri specificati. Prova con date o aeroporti diversi."

        output_lines = []
        for i, f in enumerate(flights, 1):
            output_lines.append(
                f"{i}. ✈️ {f.departure_airport} → {f.arrival_airport}\n"
                f"   Partenza: {f.departure_date.strftime('%d/%m/%Y')} | Ritorno: {f.return_date.strftime('%d/%m/%Y')}\n"
                f"   Prezzo: €{f.price:.2f} | Posti disponibili: {f.availability}"
            )
        return "\n\n".join(output_lines)
    finally:
        db.close()


@tool
def search_hotels(
    city: Optional[str] = None,
    max_price_per_night: Optional[float] = None,
    check_in_date: Optional[str] = None,
    limit: int = 5,
) -> str:
    """Cerca hotel e alloggi disponibili in una città specifica.

    Usa questo strumento quando l'utente chiede informazioni su dove dormire,
    hotel, ostelli, alloggi, sistemazioni o alberghi in una destinazione.
    Sono disponibili alloggi in oltre 40 città internazionali tra cui: Tokyo, Paris, 
    New York, London, Reykjavik, Sydney, Rome, Milan, Barcelona, Madrid, Cairo, Dubai, 
    Bangkok, Singapore, Bali, Seoul, Rio de Janeiro, Venice, Florence, e molte altre.

    Args:
        city: Nome della città per cercare gli hotel (es. "Tokyo", "Paris", "Rome").
              Se non specificato, cerca in tutte le città.
        max_price_per_night: Prezzo massimo per notte in EUR.
        check_in_date: Data di check-in desiderata in formato "YYYY-MM-DD" per verificare
                      la disponibilità. Se non specificata, vengono restituiti tutti gli hotel.
        limit: Numero massimo di risultati da restituire (default: 5).
    """
    db = SessionLocal()
    try:
        q = db.query(Hotel)
        if city:
            q = q.filter(Hotel.city.ilike(f"%{city}%"))
        if max_price_per_night is not None:
            q = q.filter(Hotel.price_per_night <= max_price_per_night)
        if check_in_date:
            try:
                check_in = datetime.date.fromisoformat(check_in_date)
                q = q.filter(
                    Hotel.available_start_date <= check_in,
                    Hotel.available_end_date >= check_in
                )
            except ValueError:
                pass  # Ignora date non valide e restituisci tutti i risultati

        hotels = q.order_by(Hotel.price_per_night.asc()).limit(limit).all()

        if not hotels:
            return "Nessun hotel trovato con i criteri specificati. Prova con una città diversa o un budget più alto."

        output_lines = []
        for i, h in enumerate(hotels, 1):
            output_lines.append(
                f"{i}. 🏨 **{h.name}** — {h.city}\n"
                f"   Prezzo: €{h.price_per_night:.2f}/notte\n"
                f"   Disponibilità: {h.available_start_date.strftime('%d/%m/%Y')} – {h.available_end_date.strftime('%d/%m/%Y')}"
            )
        return "\n\n".join(output_lines)
    finally:
        db.close()


@tool
def book_trip(
    flight_details: str,
    hotel_details: str,
    activity_details: str,
    total_estimated_price: float,
    traveler_name: str,
    config: RunnableConfig,
) -> str:
    """Prenota un viaggio completo con volo, hotel e attività per il viaggiatore.

    ATTENZIONE: Questo strumento esegue una prenotazione effettiva e un addebito.
    Usa questo strumento SOLO quando l'utente ha confermato esplicitamente di voler
    procedere con la prenotazione e hai raccolto tutti i dettagli necessari
    (volo, hotel, attività e nome del viaggiatore).
    NON chiamare questo tool in fase esplorativa o di ricerca.

    Args:
        flight_details: Riepilogo completo del volo selezionato (es. "FCO → HND, 01/08/2026, €850").
        hotel_details: Riepilogo completo dell'hotel selezionato (es. "Shinjuku Park Hotel, 14 notti, €120/notte").
        activity_details: Riepilogo delle attività selezionate (es. "Tour Shibuya €60, Lezione Samurai €85").
        total_estimated_price: Prezzo totale stimato della prenotazione in EUR.
        traveler_name: Nome completo del viaggiatore per la prenotazione.
    """
    # Questo tool è protetto da HumanInTheLoopMiddleware.
    # Se l'esecuzione arriva qui, significa che l'utente ha approvato la prenotazione.
    import json
    user_id = config.get("metadata", {}).get("user_id", 1) if config else 1
    db = SessionLocal()
    try:
        booking = Booking(
            user_id=user_id,
            status="confirmed",
            total_price=total_estimated_price,
            details_json=json.dumps({
                "flight": flight_details,
                "hotel": hotel_details,
                "activities": activity_details,
                "traveler": traveler_name,
            }, ensure_ascii=False)
        )
        db.add(booking)
        db.commit()

        return (
            f"✅ Prenotazione confermata con successo!\n\n"
            f"📋 Riepilogo:\n"
            f"  👤 Viaggiatore: {traveler_name}\n"
            f"  ✈️ Volo: {flight_details}\n"
            f"  🏨 Hotel: {hotel_details}\n"
            f"  🎯 Attività: {activity_details}\n"
            f"  💰 Totale: €{total_estimated_price:.2f}\n\n"
            f"ID Prenotazione: #{booking.id}\n"
            f"Stato: Confermato"
        )
    except Exception as e:
        db.rollback()
        return f"❌ Errore durante la prenotazione: {str(e)}. Riprova."
    finally:
        db.close()

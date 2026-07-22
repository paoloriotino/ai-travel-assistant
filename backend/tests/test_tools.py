import pytest
from unittest.mock import patch
from backend.app.services.tools import search_flights, search_hotels, modify_booking
from backend.app.database import Booking
import json

def test_search_flights_by_country(db_session):
    """Testa la ricerca dei voli usando la nazione anziché l'aeroporto."""
    # Patchiamo SessionLocal in tools.py affinché restituisca la sessione del test
    with patch("backend.app.services.tools.SessionLocal", return_value=db_session):
        # Nel conftest c'è un volo verso HND e uno verso CDG. HND è in Giappone.
        result = search_flights.invoke({"country": "giappone"})
        assert "HND" in result
        assert "Nessun volo trovato" not in result
        
        # Francia ha CDG
        result = search_flights.invoke({"country": "francia"})
        assert "CDG" in result
        
        # Una nazione senza voli nel db di test
        result = search_flights.invoke({"country": "olanda"})
        assert "Nessun volo trovato" in result

def test_search_hotels_by_country(db_session):
    """Testa la ricerca degli hotel usando la nazione anziché la città."""
    with patch("backend.app.services.tools.SessionLocal", return_value=db_session):
        # Tokyo è in Giappone
        result = search_hotels.invoke({"country": "giappone"})
        assert "Tokyo Grand Hotel" in result
        
        # Parigi è in Francia
        result = search_hotels.invoke({"country": "francia"})
        assert "Paris Elegance" in result
        
        # Nazione senza hotel nel db di test
        result = search_hotels.invoke({"country": "olanda"})
        assert "Nessun hotel trovato" in result

def test_modify_booking(db_session):
    """Testa la modifica di una prenotazione esistente."""
    # 1. Creiamo una prenotazione di test per l'utente 1
    booking = Booking(
        user_id=1,
        details_json=json.dumps({
            "flight": "Volo FCO -> CDG",
            "hotel": "Paris Elegance",
            "activities": "Visita Torre Eiffel",
            "traveler": "Mario Rossi"
        }),
        total_price=1000.0,
        status="confirmed"
    )
    db_session.add(booking)
    db_session.commit()
    
    booking_id = booking.id
    
    with patch("backend.app.services.tools.SessionLocal", return_value=db_session):
        # 2. Modifichiamo la prenotazione
        result = modify_booking.invoke({
            "booking_id": booking_id,
            "flight_details": "Volo FCO -> HND",
            "hotel_details": "Tokyo Grand Hotel",
            "activity_details": "Visita Monte Fuji",
            "total_estimated_price": 2500.0
        })
        
        # 3. Verifiche
        assert "modificata con successo" in result
        
        # Ricarichiamo dal db
        updated_booking = db_session.query(Booking).filter(Booking.id == booking_id).first()
        assert updated_booking.total_price == 2500.0
        details = json.loads(updated_booking.details_json)
        assert details["flight"] == "Volo FCO -> HND"
        assert details["hotel"] == "Tokyo Grand Hotel"
        assert details["activities"] == "Visita Monte Fuji"
        assert details["traveler"] == "Mario Rossi"  # deve mantenere il nome originario


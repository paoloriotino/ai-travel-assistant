import pytest
from backend.app.services.mapping import get_cities_by_country, get_airports_by_country

def test_get_cities_by_country_valid():
    """Testa che per nazioni valide vengano restituite le città corrette."""
    cities = get_cities_by_country("giappone")
    assert "Tokyo" in cities
    assert "Kyoto" in cities
    
    cities = get_cities_by_country("ITALIA")
    assert "Roma" in cities
    assert "Milano" in cities

def test_get_cities_by_country_invalid_or_empty():
    """Testa nazioni non valide o valori vuoti."""
    assert get_cities_by_country("Narnia") == []
    assert get_cities_by_country("") == []
    assert get_cities_by_country(None) == []

def test_get_airports_by_country_valid():
    """Testa che per nazioni valide vengano restituiti gli aeroporti aggregati."""
    airports = get_airports_by_country("giappone")
    assert "HND" in airports
    assert "NRT" in airports
    
    airports = get_airports_by_country("Francia")
    assert "CDG" in airports
    assert "ORY" in airports

def test_get_airports_by_country_invalid_or_empty():
    """Testa che valori vuoti o nazioni inesistenti restituiscano liste vuote."""
    assert get_airports_by_country("Wakanda") == []
    assert get_airports_by_country("") == []
    assert get_airports_by_country(None) == []

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.schemas.auth import UserCreate
from backend.app.services.security import get_password_hash
from backend.app.database import User, Flight, Hotel, Activity

from sqlalchemy.pool import StaticPool

# URL del database SQLite in-memory per i test
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Crea una nuova sessione di database pulita per ogni test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Popola il database con dati mock utili per i test
    # 1. Utente di test
    hashed_password = get_password_hash("testpassword")
    test_user = User(username="testuser", hashed_password=hashed_password)
    db.add(test_user)
    
    # 2. Voli mock
    import datetime
    flight1 = Flight(
        departure_airport="FCO",
        arrival_airport="HND",
        departure_date=datetime.date(2026, 8, 1),
        return_date=datetime.date(2026, 8, 15),
        price=800.0,
        availability=10
    )
    flight2 = Flight(
        departure_airport="JFK",
        arrival_airport="CDG",
        departure_date=datetime.date(2026, 9, 10),
        return_date=datetime.date(2026, 9, 20),
        price=500.0,
        availability=5
    )
    db.add_all([flight1, flight2])
    
    # 3. Hotel mock
    hotel1 = Hotel(
        name="Tokyo Grand Hotel",
        city="Tokyo",
        price_per_night=150.0,
        available_start_date=datetime.date(2026, 1, 1),
        available_end_date=datetime.date(2027, 12, 31)
    )
    hotel2 = Hotel(
        name="Paris Elegance",
        city="Parigi",
        price_per_night=200.0,
        available_start_date=datetime.date(2026, 1, 1),
        available_end_date=datetime.date(2027, 12, 31)
    )
    db.add_all([hotel1, hotel2])
    
    db.commit()
    
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Fornisce un TestClient configurato per usare il DB in-memory."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

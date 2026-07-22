import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text, Date
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Determinazione dinamica del percorso del database SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db')
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(DB_DIR, 'travel_assistant.db')}")

# Configurazione del database engine
# connect_args={"check_same_thread": False} è necessario per SQLite in contesti multi-thread
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    bookings = relationship("Booking", back_populates="user")

class Flight(Base):
    __tablename__ = "flights"
    
    id = Column(Integer, primary_key=True, index=True)
    departure_airport = Column(String(3), nullable=False)  # es. FCO, MXP
    arrival_airport = Column(String(3), nullable=False)    # es. HND, JFK
    departure_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=False)
    price = Column(Float, nullable=False)
    availability = Column(Integer, nullable=False)  # Numero di posti disponibili

class Hotel(Base):
    __tablename__ = "hotels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    price_per_night = Column(Float, nullable=False)
    available_start_date = Column(Date, nullable=False)
    available_end_date = Column(Date, nullable=False)

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    target_audience = Column(String, nullable=False)  # es. "famiglie, giovani, coppie"
    available_months = Column(String, nullable=False)  # es. "6,7,8" (Giugno, Luglio, Agosto)

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending, confirmed, cancelled
    total_price = Column(Float, nullable=False)
    details_json = Column(Text, nullable=False)  # Itinerario completo salvato come stringa JSON
    
    user = relationship("User", back_populates="bookings")

def init_db():
    """Inizializza le tabelle nel database SQLite"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency per ottenere la sessione DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

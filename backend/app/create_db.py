import os
import sys
import argparse

# Aggiunge la directory corrente al sys.path per consentire importazioni relative
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from seed_data import seed_database
from rag.ingestion import run_ingestion
from rag.vector_db import query_activities
from database import SessionLocal, Flight, Hotel, Activity

def parse_arguments():
    parser = argparse.ArgumentParser(description="Inizializza i database relazionale e vettoriale per AI Travel Assistant.")
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Esegue le query semantiche di verifica dopo la creazione dei database."
    )
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Sfrutta la GPU (RTX 3060) per il calcolo degli embeddings. Di default viene usata la CPU."
    )
    return parser.parse_args()


def verify_pipeline():
    print("\n--- 3. Esecuzione Test di Verifica (Query Semantiche) ---")
    
    # Test query A: Cibo a Roma
    query_a = "pasta fatta in casa e cibo tradizionale"
    print(f"\nQuery A: '{query_a}' (Filtro Paese: Italy)")
    results_a = query_activities(
        query=query_a,
        limit=2,
        filters={"country": "Italy"}
    )
    
    for i, doc in enumerate(results_a):
        print(f" [{i+1}] {doc.metadata['title']} ({doc.metadata['city']}) - {doc.metadata['price']} EUR")
        print(f"     Descrizione: {doc.metadata['title']}...")
        
    assert len(results_a) > 0, "Errore: Nessuna attività trovata per la Query A"
    assert any(doc.metadata["city"] == "Rome" for doc in results_a), "Errore: Nessuna attività trovata a Roma"
    print(" -> Query A superata con successo!")
    
    # Test query B: Attività sportiva con budget limitato (<= 50 EUR)
    query_b = "avventura all'aria aperta e trekking"
    print(f"\nQuery B: '{query_b}' (Filtro Prezzo: <= 50.0 EUR)")
    results_b = query_activities(
        query=query_b,
        limit=2,
        filters={"price": {"$lte": 50.0}}
    )
    
    for i, doc in enumerate(results_b):
        print(f" [{i+1}] {doc.metadata['title']} ({doc.metadata['city']}) - {doc.metadata['price']} EUR")
        
    assert len(results_b) > 0, "Errore: Nessuna attività trovata per la Query B"
    for doc in results_b:
        assert doc.metadata["price"] <= 50.0, f"Errore: Prezzo {doc.metadata['price']} supera 50 EUR"
    print(" -> Query B superata con successo!")
    
    print("\n=== PIPELINE VERIFICATA CON SUCCESSO! TUTTI I TEST SONO PASSATI ===")

def main():
    args = parse_arguments()
    
    # Configura l'uso della GPU basandosi sul flag della riga di comando
    if args.gpu:
        os.environ["USE_GPU"] = "1"
    else:
        os.environ["USE_GPU"] = "0"
        
    print("=== INIZIALIZZAZIONE PIPELINE DATI ===")
    
    # 1. Seeding del database relazionale SQLite
    print("\n--- 1. Creazione e Seeding Database SQLite ---")

    seed_database()
    
    # Verifica preliminare SQLite
    db = SessionLocal()
    try:
        flights_count = db.query(Flight).count()
        hotels_count = db.query(Hotel).count()
        activities_count = db.query(Activity).count()
        print(f"\nVerifica Record SQLite:")
        print(f" - Voli inseriti: {flights_count}")
        print(f" - Hotel inseriti: {hotels_count}")
        print(f" - Attività inserite: {activities_count}")
    finally:
        db.close()
        
    # 2. Pipeline di Ingestion in ChromaDB
    print("\n--- 2. Creazione e Ingestion Database Vettoriale RAG (ChromaDB) ---")
    run_ingestion()
    
    print("\n=== DATABASES INIZIALIZZATI CON SUCCESSO! ===")
    
    # 3. Se il flag --test è attivo, esegue i test
    if args.test:
        verify_pipeline()

if __name__ == "__main__":
    main()

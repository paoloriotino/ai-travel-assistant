import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir)
sys.path.append(app_dir)

from database import SessionLocal, Activity
from rag.vector_db import get_vector_store
from langchain_core.documents import Document

def run_ingestion():
    print("Avvio della pipeline di ingestion RAG...")
    
    # 1. Recupero delle attività dal database relazionale SQLite
    db = SessionLocal()
    try:
        activities = db.query(Activity).all()
        if not activities:
            print("Nessuna attività trovata nel database relazionale. Esegui prima il seed dei dati.")
            return
        
        print(f"Trovate {len(activities)} attività nel database SQLite. Preparazione all'indicizzazione...")
        
        # 2. Reset della collezione vettoriale esistente per evitare duplicati
        vector_store = get_vector_store()
        try:
            vector_store.delete_collection()
            print("Collezione vettoriale precedente eliminata.")
        except Exception as e:
            print(f"Info: Nessuna collezione precedente da eliminare o errore: {e}")
            
        # Re-inizializziamo il vector store vuoto
        vector_store = get_vector_store()
        
        # 3. Conversione delle attività in oggetti Document di LangChain
        documents = []
        for activity in activities:
            # Testo per la similarità semantica (LLM lo leggerà per associare le richieste dell'utente)
            page_content = (
                f"Attività: {activity.title}\n"
                f"Città: {activity.city}, Paese: {activity.country}\n"
                f"Prezzo: {activity.price} EUR\n"
                f"Descrizione: {activity.description}\n"
                f"Target ideale: {activity.target_audience}\n"
                f"Mesi disponibili: {activity.available_months}"
            )
            
            # Metadati strutturati per filtri precisi
            metadata = {
                "activity_id": activity.id,
                "title": activity.title,
                "city": activity.city,
                "country": activity.country,
                "price": float(activity.price),
                "target_audience": activity.target_audience,
                "available_months": activity.available_months
            }
            
            doc = Document(page_content=page_content, metadata=metadata)
            documents.append(doc)
            
        # 4. Caricamento dei documenti e calcolo degli embeddings su ChromaDB
        print(f"Calcolo degli embeddings e salvataggio di {len(documents)} documenti in ChromaDB...")
        vector_store.add_documents(documents)
        print("Ingestion completata con successo!")
        
    except Exception as e:
        print(f"Errore durante l'ingestion: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_ingestion()

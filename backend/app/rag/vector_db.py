import os
import torch
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Determinazione dinamica delle cartelle per ChromaDB
# backend/app/rag/vector_db.py -> backend/db/chroma_db
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DB_DIR = os.path.join(os.path.dirname(BASE_DIR), "db", "chroma_db")

EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
_embeddings = None

def get_embeddings():
    """Inizializza o restituisce il modello di embeddings di HuggingFace"""
    global _embeddings
    if _embeddings is None:
        # Determina il device: auto-detect CUDA (RTX 3060) se disponibile, a meno che USE_GPU non sia impostato a "0"
        use_gpu_env = os.environ.get("USE_GPU", "auto").lower()
        if use_gpu_env == "0":
            device = "cpu"
        elif torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
        
        print(f"Caricamento del modello di embeddings: {EMBEDDINGS_MODEL} (Device: {device.upper()})...")
        if device == "cuda":
            print(f"GPU NVIDIA Rilevata ed in uso: {torch.cuda.get_device_name(0)}")
        elif use_gpu_env == "1" and not torch.cuda.is_available():
            print("Attenzione: Flag USE_GPU=1 specificato ma CUDA non è disponibile in PyTorch. Fallback su CPU.")
            
        # HuggingFaceEmbeddings scaricherà il modello (~120MB) localmente alla prima chiamata
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDINGS_MODEL,
            model_kwargs={'device': device},
            encode_kwargs={'normalize_embeddings': True}
        )
    return _embeddings



def get_vector_store():
    """Restituisce il client ChromaDB persistito su disco per la collezione 'activities'"""
    embeddings = get_embeddings()
    return Chroma(
        collection_name="activities",
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_DIR
    )

def query_activities(query: str, limit: int = 3, filters: dict = None):
    """
    Esegue una ricerca semantica sulle attività con opzione di filtraggio metadati.
    
    Args:
        query (str): La stringa di ricerca in linguaggio naturale.
        limit (int): Numero massimo di risultati.
        filters (dict): Dizionario di filtri (es. {"country": "Italy", "price": {"$lte": 50.0}})
    """
    store = get_vector_store()
    
    # Chroma supporta filtri complessi (es. dict con operatori $lte, $eq, ecc. o semplici chiavi per match esatto)
    return store.similarity_search(
        query=query,
        k=limit,
        filter=filters
    )

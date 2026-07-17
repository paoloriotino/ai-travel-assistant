# AI Travel Assistant 🌍✈️

Assistente virtuale conversazionale intelligente per il settore Travel & Experiences, in grado di comprendere le esigenze dell'utente, generare itinerari personalizzati completi e gestire le prenotazioni.

Questa repository è strutturata con una netta separazione tra:
*   `backend/`: Server in Python (FastAPI/LangChain/SQLite/ChromaDB).
*   `frontend/`: Interfaccia utente (React/Vite o HTML/CSS/JS moderno).

---

## 🛠️ Prerequisiti

Assicurati di avere installato sul tuo sistema:
*   **Python 3.13** o superiore.
*   **uv**: Il gestore di pacchetti e ambienti Python ultra-veloce (consigliato). Se non lo hai, installalo tramite:
    ```powershell
    # Su Windows (PowerShell)
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    # Su macOS/Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

---

## 🚀 Setup e Installazione

Segui questi passaggi per configurare l'ambiente virtuale e installare le dipendenze del backend:

1.  **Crea l'ambiente virtuale** nella root del progetto:
    ```bash
    uv venv
    ```

2.  **Attiva l'ambiente virtuale**:
    *   **Windows (PowerShell)**:
        ```powershell
        .venv\Scripts\activate
        ```
    *   **macOS/Linux**:
        ```bash
        source .venv/bin/activate
        ```

3.  **Installa le dipendenze** del backend direttamente da `pyproject.toml`:
    *   **Metodo consigliato (Standard `uv`):**
        ```bash
        uv sync
        ```
        *(Questo comando crea automaticamente l'ambiente virtuale `.venv` se non esiste e installa tutte le dipendenze definite in `pyproject.toml` in un unico passaggio).*
    
    *   **Metodo alternativo (`uv pip`):**
        ```bash
        uv pip install -e .
        ```
        *(Installa il progetto in modalità editabile con tutte le sue dipendenze).*


---

## 💾 Inizializzazione dei Database

Per facilitare l'avvio, abbiamo creato uno script unificato `create_db.py` che si occupa di configurare sia il database relazionale (SQLite) che quello vettoriale (ChromaDB).

Esegui lo script stando nella root del progetto:

```bash
# Esecuzione standard (creazione database relazionale + vettoriale su CPU)
uv run python backend/app/create_db.py

# Esecuzione sfruttando la GPU (RTX 3060) per gli embeddings (molto più veloce!)
uv run python backend/app/create_db.py --gpu

# Esecuzione su GPU con test di verifica RAG finali
uv run python backend/app/create_db.py --gpu --test
```

### Opzioni dello Script:
*   `--gpu`: Forza l'utilizzo della GPU NVIDIA (RTX 3060) tramite CUDA per calcolare gli embeddings in frazioni di secondo. Se CUDA non è disponibile, lo script farà un fallback sicuro su CPU.
*   `--test`: Esegue due query semantiche di test con filtri sui metadati (paese e prezzo massimo) per assicurarsi che la ricerca semantica RAG funzioni correttamente.

### Cosa fa questo script?
1.  **Seeding SQLite**: Crea il database `backend/app/travel_assistant.db` e lo popola con dati di seed realistici (voli, hotel, e 29 attività descritte in dettaglio).
2.  **Ingestion RAG**: Inizializza ChromaDB (`backend/db/chroma_db`), carica le attività da SQLite, ne calcola gli embeddings localmente tramite il modello HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (~120MB, offline su CPU o GPU) e li indicizza.
3.  **Verifica (solo con `--test`)**: Esegue due query semantiche di test per assicurarsi che la ricerca semantica RAG funzioni correttamente.


---

## 📂 Struttura del Codice (Backend)

La struttura dei file relativi ai dati e al RAG è organizzata come segue:

*   [`backend/app/database.py`](file:///c:/Users/rioti/Documents/Projects/ai-travel-assistant/backend/app/database.py): Modelli ORM di SQLAlchemy (`User`, `Flight`, `Hotel`, `Activity`, `Booking`) e connessione SQLite.
*   [`backend/app/seed_data.py`](file:///c:/Users/rioti/Documents/Projects/ai-travel-assistant/backend/app/seed_data.py): Script di popolamento iniziale dei dati relazionali.
*   [`backend/app/rag/vector_db.py`](file:///c:/Users/rioti/Documents/Projects/ai-travel-assistant/backend/app/rag/vector_db.py): Configurazione del Vector Store (ChromaDB) e dei modelli di embedding.
*   [`backend/app/rag/ingestion.py`](file:///c:/Users/rioti/Documents/Projects/ai-travel-assistant/backend/app/rag/ingestion.py): Pipeline per il calcolo degli embeddings e l'indicizzazione semantica.
*   [`backend/app/create_db.py`](file:///c:/Users/rioti/Documents/Projects/ai-travel-assistant/backend/app/create_db.py): Script unificato di creazione dei database con flag di test.


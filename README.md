# AI Travel Assistant 🌍✈️

Assistente virtuale conversazionale intelligente per il settore **Travel & Experiences**, in grado di comprendere le esigenze dell'utente, generare itinerari personalizzati completi in tempo reale e gestire le prenotazioni con approvazione umana (Human-in-the-Loop).

---

## 🏗️ Architettura del Sistema

Repository Fullstack con netta separazione tra backend e frontend:

```
ai-travel-assistant/
├── backend/          # Server Python (FastAPI, LangChain/LangGraph, ChromaDB, SQLite)
│   ├── app/
│   │   ├── agents/   # Agente conversazionale TripAI e middleware HITL
│   │   ├── api/      # Endpoint REST (Chat, History, Resume, Bookings)
│   │   ├── rag/      # Database vettoriale ChromaDB e pipeline di ingestion
│   │   ├── schemas/  # Schemi Pydantic v2 di I/O e risposta strutturata
│   │   ├── services/ # Tool LangChain (ricerca voli, hotel, RAG attività, prenotazione)
│   │   └── database.py / seed_data.py / create_db.py
├── frontend/         # Interfaccia utente (React 19, TypeScript, Vite, Vanilla CSS)
│   ├── src/
│   │   ├── components/ # ChatView, ItineraryCanvas, ChatSidebar, DashboardView, ecc.
│   │   ├── services/   # Client API REST per il backend
│   │   └── types.ts    # Interfacce TypeScript
└── tasks/            # Specifiche e tracciamento dei task di sviluppo
```

### Tecnologie Chiave:
*   **Backend**: Python 3.13, FastAPI, LangChain / LangGraph (con `SqliteSaver` per la persistenza delle conversazioni e `HumanInTheLoopMiddleware` per la sicurezza delle prenotazioni), SQLAlchemy (SQLite) e ChromaDB per la ricerca RAG vettoriale.
*   **AI / LLM Flessibile**:
    *   **Cloud**: Supporto nativo a **Google Gemini 1.5 Pro** / **Flash**.
    *   **Locale**: Supporto ad **Ollama** per eseguire modelli locali ad alte prestazioni (es. `qwen2.5:14b` o `gemma2:9b`) sfruttando schede video come la **NVIDIA RTX 3060 (12GB VRAM)**.
*   **Frontend**: React, TypeScript, Vite, Vanilla CSS avanzato con palette *"Golden Hour & Midnight"* e design responsive.

---

## 🌟 Funzionalità Principali

1.  **Conversazione Intelligente & Tool Calling**:
    L'agente conversa in italiano ed usa autonomamente i tool per cercare tra 43 destinazioni globali:
    *   ✈️ **Voli** (215 voli con varie stagionalità dagli hub FCO/MXP).
    *   🏨 **Hotel** (430 alloggi divisi in fascia economica, media e lusso).
    *   🎯 **Attività RAG GetYourGuide-style** (860 tour ed esperienze reali con ricerca semantica).
2.  **Scheda Viaggio Live (`ItineraryCanvas`)**:
    L'itinerario si popola in tempo reale a destra dello schermo non appena viene espressa la destinazione, aggiornandosi man mano che voli, hotel e attività vengono scelti.
3.  **Titoli Chat Dinamici**:
    Ogni nuova conversazione parte con il titolo `"Nuovo viaggio"` e si aggiorna automaticamente in `"Viaggio a {Destinazione}"` non appena la meta viene individuata.
4.  **Prenotazione Protetta (Human-in-the-Loop)**:
    L'agente non può addebitare o prenotare viaggi autonomamente; prima dell'esecuzione del tool `book_trip` si attiva un modale interattivo che richiede la conferma esplicita dell'utente.
5.  **Dashboard Prenotazioni**:
    Vista dedicata per accedere allo storico dei viaggi confermati o in attesa e gestire eventuali cancellazioni.

---

## 🛠️ Prerequisiti

*   **Python 3.13** o superiore.
*   **uv**: Gestore di pacchetti Python ultra-veloce ([Istruzioni di installazione uv](https://astral.sh/uv)).
*   **Node.js 18+** e **npm** (per il frontend).
*   *(Opzionale per AI Locale)*: **Ollama** installato per eseguire LLM in locale su GPU.

---

## 🚀 Guida Rapida all'Esecuzione (Fullstack)

### Step 1: Configurazione Ambiente e Dipendenze Python

Nella root del progetto (`ai-travel-assistant`):

```powershell
# 1. Crea e sincronizza l'ambiente virtuale Python (.venv)
uv sync

# 2. Configura il file delle variabili d'ambiente
cp .env.example .env
```

Apri il file `.env` e configura il provider LLM desiderato:

*   **Per usare Google Gemini (Cloud)**:
    ```env
    LLM_PROVIDER=google
    GOOGLE_API_KEY=la_tua_chiave_google_ai_studio
    LLM_MODEL=gemini-1.5-pro
    ```
*   **Per usare Ollama (Locale su GPU RTX 3060 12GB)**:
    ```env
    LLM_PROVIDER=ollama
    LLM_MODEL=qwen2.5:14b
    OLLAMA_BASE_URL=http://localhost:11434
    ```

---

### Step 2: Inizializzazione Database Relazionale e Vettoriale (Seeding & RAG)

Esegui lo script di popolamento nella root del progetto:

```powershell
# Inizializzazione con calcolo degli embeddings vettoriali su GPU (NVIDIA RTX 3060) e test di verifica
uv run python backend/app/create_db.py --gpu --test
```

*Questo comando popolerà SQLite con 43 destinazioni, 215 voli, 430 hotel e 860 attività stile GetYourGuide, calcolando gli embeddings per ChromaDB.*

---

### Step 3: Avvio del Server Backend (FastAPI)

```powershell
uv run uvicorn backend.app.main:app --reload
```

* Server Backend: **`http://localhost:8000`**
* Documentazione OpenAPI / Swagger UI: **`http://localhost:8000/docs`**

---

### Step 4: Setup ed Avvio del Frontend (React + Vite)

In una **seconda finestra terminale**:

```powershell
# 1. Entra nella cartella frontend
cd frontend

# 2. Installa le dipendenze Node.js
npm install

# 3. Avvia il server di sviluppo Vite
npm run dev
```

* Interfaccia Web App: **`http://localhost:5173`** *(Vite inoltrerà automaticamente le chiamate `/api` al backend su `localhost:8000`)*.

---

## 🔌 API REST Principal (FastAPI)

*   `POST /api/chat`: Invia un messaggio all'agente. Restituisce la risposta conversazionale, l'itinerario strutturato e le domande rapide.
*   `GET /api/chat/history/{thread_id}`: Recupera la cronologia dei messaggi per una determinata chat.
*   `GET /api/chat/threads`: Elenca le chat salvate dell'utente con i rispettivi titoli dinamici.
*   `DELETE /api/chat/threads/{thread_id}`: Elimina una conversazione dallo storico SQLite.
*   `POST /api/chat/resume`: Approva o rifiuta un'azione di prenotazione in stato di interruzione (HITL).
*   `GET /api/bookings`: Restituisce la lista delle prenotazioni effettuate.
*   `POST /api/bookings/{id}/cancel`: Annulla una prenotazione esistente.

---

## 📦 Comandi Utili

| Comando | Descrizione |
| :--- | :--- |
| `uv sync` | Sincronizza l'ambiente virtuale Python `.venv` |
| `uv run python backend/app/create_db.py --gpu --test` | Re-inizializza SQLite, ChromaDB ed esegue i test RAG |
| `uv run uvicorn backend.app.main:app --reload` | Avvia il server backend in modalità live-reload |
| `cd frontend && npm run dev` | Avvia l'interfaccia frontend in sviluppo |
| `cd frontend && npm run build` | Genera la build di produzione del frontend in `dist/` |

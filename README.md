# AI Travel Assistant 🌍✈️

Assistente virtuale conversazionale intelligente per il settore **Travel & Experiences**, in grado di comprendere le esigenze dell'utente, generare itinerari personalizzati completi in tempo reale e gestire le prenotazioni con approvazione umana (Human-in-the-Loop).

---

## 🏗️ Architettura del Sistema

Repository Fullstack con netta separazione tra backend e frontend:

```
ai-travel-assistant/
├── backend/          # Server Python (FastAPI, LangChain/LangGraph, ChromaDB, SQLite)
│   ├── app/          # Codice sorgente dell'applicazione (Core)
│   │   ├── agents/   # Agente conversazionale TripAI e middleware HITL
│   │   ├── api/      # Endpoint REST (Chat, History, Resume, Bookings)
│   │   ├── rag/      # Componenti di accesso al Vector DB (ChromaDB)
│   │   ├── schemas/  # Schemi Pydantic v2 di I/O e risposta strutturata
│   │   ├── services/ # Tool LangChain (ricerca voli, hotel, RAG attività, prenotazione)
│   │   └── database.py / main.py
│   ├── db/           # Cartella centralizzata per i database
│   │   ├── chroma_db/             # Vector Database per la ricerca semantica
│   │   ├── travel_assistant.db    # Relational Database (Voli, Hotel, Prenotazioni)
│   │   └── checkpoints.db         # Storage per la memoria e cronologia chat (LangGraph)
│   ├── scripts/      # Script di utility e bootstrapping
│   │   ├── create_db.py           # Inizializza e popola DB Relazionale e Vettoriale
│   │   ├── clean_data.py          # Svuota prenotazioni e storico chat
│   │   └── seed_data.py           # Dati mock per voli, hotel e attività
│   └── tests/        # Suite di test automatizzati (Pytest)
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
    *   **Cloud**: Supporto nativo a **Google Gemini 2.0 Flash**.
    *   **Locale**: Supporto ad **Ollama** per eseguire modelli locali ad alte prestazioni.
*   **Frontend**: React, TypeScript, Vite, Vanilla CSS avanzato con palette *"Golden Hour & Midnight"* e design responsive.

---

## 🌟 Funzionalità Principali

1.  **Conversazione Intelligente & Tool Calling Avanzato**:
    L'agente conversa in italiano e traduce intuitivamente concetti generici in query complesse. Conosce i dati dei voli (215 voli), hotel (430 alloggi) ed attività GetYourGuide-style (860 tour). 
    *Novità: L'agente è in grado di dedurre autonomamente le città partendo da nazioni o descrizioni generiche fornite dall'utente, senza affidarsi a mappature statiche.*
2.  **Scheda Viaggio Live (`ItineraryCanvas`)**:
    L'itinerario si popola in tempo reale a destra dello schermo non appena viene espressa la destinazione, aggiornandosi man mano che voli, hotel e attività vengono scelti.
3.  **Titoli Chat Dinamici & Separazione Viaggi**:
    Ogni conversazione si aggiorna automaticamente in `"Viaggio a {Destinazione}"`. Se modifichi una prenotazione esistente, viene generato un thread dedicato.
4.  **Prenotazione Protetta (Human-in-the-Loop)**:
    L'agente non può addebitare o prenotare viaggi autonomamente; prima dell'esecuzione del tool `book_trip` si attiva un modale interattivo (senza "grey pills" invasive) che richiede la conferma esplicita dell'utente.

---

## 🛠️ Prerequisiti

*   **Python 3.13** o superiore.
*   **uv**: Gestore di pacchetti Python ultra-veloce ([Istruzioni di installazione uv](https://astral.sh/uv)).
*   **Node.js 18+** e **npm** (per il frontend).

---

## 🚀 Guida Rapida all'Esecuzione (Fullstack)

### Step 1: Configurazione Ambiente e Dipendenze Python

Nella root del progetto (`ai-travel-assistant`):

```powershell
# 1. Crea e sincronizza l'ambiente virtuale Python (.venv)
uv sync

# 2. Configura il file delle variabili d'ambiente (se non esiste)
cp .env.example .env
```

Apri il file `.env` e configura il provider LLM desiderato:

*   **Per usare Google Gemini (Raccomandato)**:
    ```env
    LLM_PROVIDER=google
    GOOGLE_API_KEY=la_tua_chiave_google_ai_studio
    LLM_MODEL=gemini-flash-latest
    ```

---

### Step 2: Inizializzazione e Popolamento Database (Seeding & RAG)

Prima di avviare l'API, devi creare i database relazionali e vettoriali e popolarli con i dati di partenza.
Usa lo script presente in `backend/scripts/`:

```powershell
# Inizializzazione con calcolo degli embeddings vettoriali (aggiungi --gpu se hai una scheda video dedicata, es. RTX 3060) e test di verifica
uv run python backend/scripts/create_db.py --gpu --test
```

*I database verranno generati all'interno della cartella `backend/db/`.*

---

### Step 3: Avvio del Server Backend (FastAPI)

Assicurati di lanciare uvicorn dalla root del progetto:

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

* Interfaccia Web App: **`http://localhost:5173`**

---

## 🧹 Manutenzione e Pulizia Dati

Se hai testato l'agente e desideri svuotare la cronologia delle chat e le prenotazioni effettuate (mantenendo intatti voli, hotel e attività), puoi usare lo script di pulizia dedicato:

```powershell
uv run python backend/scripts/clean_data.py
```
*Questo comando agirà esclusivamente all'interno di `backend/db/` per resettare il tuo profilo utente simulato, pronto per un nuovo test.*

---

## 🔌 API REST Principali (FastAPI)

*   `POST /api/chat`: Invia un messaggio all'agente e ottiene la risposta e l'itinerario.
*   `GET /api/chat/history/{thread_id}`: Recupera la cronologia dei messaggi.
*   `GET /api/chat/threads`: Elenca le chat salvate dell'utente.
*   `DELETE /api/chat/threads/{thread_id}`: Elimina una conversazione dallo storico SQLite.
*   `POST /api/chat/resume`: Approva o rifiuta una prenotazione in stato di interruzione (HITL).
*   `GET /api/bookings`: Restituisce la lista delle prenotazioni.
*   `POST /api/bookings/{id}/cancel`: Annulla una prenotazione.

---

## 📦 Tabella Riassuntiva Comandi

| Comando | Descrizione |
| :--- | :--- |
| `uv sync` | Sincronizza l'ambiente virtuale Python `.venv` |
| `uv run python backend/scripts/create_db.py --gpu --test` | Inizializza i DB (SQLite e ChromaDB in `backend/db/`) |
| `uv run python backend/scripts/clean_data.py` | Svuota prenotazioni e cronologia chat (Checkpoints) |
| `uv run uvicorn backend.app.main:app --reload` | Avvia il server backend in modalità live-reload |
| `cd frontend && npm run dev` | Avvia l'interfaccia frontend in sviluppo |
| `cd frontend && npm run build` | Genera la build di produzione del frontend in `dist/` |

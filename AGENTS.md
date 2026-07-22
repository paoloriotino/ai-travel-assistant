# Agent Profile & Guidelines: Code Development Agent

Questo documento definisce il ruolo, le responsabilità, le competenze e i flussi di lavoro dell'**Agente di Sviluppo Codice** per il progetto **AI Travel Assistant**. L'agente opera come uno sviluppatore Fullstack senior, esperto di Intelligenza Artificiale Conversazionale, sviluppo di API backend stabili, e interfacce utente frontend ricercate e performanti.

---

## 1. Ruolo e Obiettivo
L'agente ha lo scopo di guidare ed eseguire lo sviluppo del sistema **AI Travel Assistant**, che comprende:
- Un **Backend** robusto (es. Python con FastAPI/Flask) che gestisce l'integrazione con LLM, basi di dati relazionali, database vettoriali per approcci RAG, e logiche di prenotazione (voli, alberghi, attività).
- Un **Frontend** (es. React/Vite o HTML/CSS/JS moderno) con interfacce ricche, fluide, reattive e dal design premium (chat con l'assistente, dashboard di prenotazione, gestione itinerari).

L'agente deve applicare rigore ingegneristico, ottimizzazione del codice, e seguire rigorosamente le **Skills** e le **Best Practice** definite nel repository.

---

## 2. Utilizzo delle Skills
L'agente è equipaggiato con tre Skills fondamentali presenti sotto `.agents/skills/`. Esse devono essere utilizzate secondo le linee guida descritte di seguito:

### A. Frontend Design (`frontend-design`)
Quando sviluppa o modifica interfacce utente, l'agente deve agire come il *Design Lead* di uno studio creativo orientato a prodotti unici ed eleganti.
- **Principi Visivi**:
  - Evitare stili predefiniti o template generici. Scegliere palette di colori personalizzate (4-6 valori esadecimali definiti).
  - Accoppiare font di display e font di body con intenzione (es. Google Fonts come Outfit, Inter, Montserrat).
  - Strutturare layout asimmetrici o griglie moderne che riflettono i contenuti reali, non segnaposto.
- **Flusso in Due Passaggi**:
  1. **Pianificazione**: Definire il sistema di token (colori, tipografia, layout in ASCII, ed elemento "Signature" unico).
  2. **Recensione**: Confrontare il piano con le aspettative del brand, eliminare elementi superflui (regola di Chanel: "Rimuovi un accessorio prima di uscire") e poi implementare il codice CSS/HTML.
- **Motion & Micro-interactions**: Inserire transizioni fluide per gli hover, stati di caricamento animati nella chat e caricamento progressivo degli itinerari per stupire l'utente.
- **UX Writing**: Scrivere testi in modo attivo, chiaro ed empatico ("Salva modifiche" invece di "Invia"). Evitare gergo di sistema.

### B. Fondamenti di LangChain (`langchain-fundamentals`)
Per tutta la logica conversazionale dell'assistente di viaggio, l'agente deve seguire i pattern moderni di LangChain e LangGraph.
- **Creazione dell'Agente**: Utilizzare sempre la funzione `create_agent()` (o `createAgent` in TypeScript). Non ricorrere a vecchi pattern deprecati.
- **Definizione dei Tool**:
  - Implementare funzioni con decoratore `@tool` (Python) o `tool()` (JS/TS).
  - Fornire docstring precise, descrittive e complete di argomenti (Args), poiché l'LLM le usa per decidere quando e come chiamare il tool.
- **Gestione dello Stato e Persistenza**:
  - Configurare un `checkpointer` (es. `MemorySaver`) per abilitare la persistenza delle sessioni di chat.
  - Richiedere sempre un `thread_id` nella configurazione di invoke per mantenere il contesto delle conversazioni degli utenti.
- **Controllo e Middleware**:
  - Utilizzare middleware dedicati per intercettare le chiamate (es. `HumanInTheLoopMiddleware` per azioni sensibili come la prenotazione effettiva dei voli o la transazione economica).
  - Impostare limiti di ricorsione (`recursion_limit: 10`) per evitare loop infiniti dell'LLM in produzione.
- **Structured Output**: Richiedere risposte strutturate tramite `response_format` o `.with_structured_output()` per estrarre itinerari, dettagli utente o preferenze in formati JSON tipizzati (usando Pydantic o Zod).

### C. Generatore di Specifiche (`task-generator`)
Prima di iniziare compiti complessi, l'agente deve strutturare il lavoro trasformando appunti grezzi in task specifici.
- **Procedura**:
  1. Elencare i file `task.md` storici dentro la cartella `tasks/` (se esistenti) usando pattern `glob`.
  2. Esaminare la struttura e la nomenclatura precedente (`TASK_#_nome_task`).
  3. Fare domande di chiarimento mirate all'utente (una alla volta).
  4. Redigere un file `task.md` che includa:
     - **Objective**: Obiettivo chiaro e misurabile del task.
     - **Scope**: Sotto-attività suddivise in modo logico (es. Subtask A - Backend, Subtask B - Frontend).
     - **Requirements & Best Practices**: Requisiti tecnici e standard del repository.
     - **Acceptance Criteria**: Criteri di accettazione con checkbox `[ ]` chiari e verificabili.

---

## 3. Linee Guida per il Backend (Python)
L'architettura backend deve supportare l'assistente virtuale in modo scalabile e pulito:
- **Struttura del Codice**:
  - Separazione netta tra i moduli API (FastAPI/Flask), logiche dell'agente LangChain (`agents/`), servizi di database vettoriale (`rag/`), e servizi di prenotazione esterni simulati (`services/`).
  - Utilizzare **Pydantic v2** per la validazione di input/output e per la definizione di schemi di viaggio complessi (struttura dell'itinerario con hotel, voli e attività giornaliere).
- **Integrazione Database**:
  - Relazionale (SQLite/PostgreSQL): Gestire sessioni con SQLAlchemy o ORM equivalenti. Assicurarsi che le tabelle per `Utenti`, `Alberghi`, `Attività`, `Voli` e `Prenotazioni` siano relazionate correttamente.
  - Vettoriale (Chroma/FAISS): Implementare pipeline di ingestion per le descrizioni testuali delle attività ed effettuare ricerche semantiche con embeddings aggiornati (es. OpenAI o HuggingFace).
- **Gestione Errori**:
  - Istruire l'LLM e i tool a gestire le eccezioni (es. "nessun volo trovato", "budget superato") restituendo messaggi puliti che l'agente può spiegare in chat, evitando crash del server.

---

## 4. Linee Guida per il Frontend
L'interfaccia utente deve trasmettere un senso di affidabilità e modernità per ispirare gli utenti a prenotare le proprie vacanze:
- **Tecnologie**: HTML/CSS/JS moderno o React/Vite.
- **UI/UX per l'Assistente Virtuale**:
  - Chat fluida con scroll automatico all'ultimo messaggio, indicatori di digitazione ("l'assistente sta scrivendo...") e rendering pulito dei messaggi Markdown.
  - Visualizzazione degli itinerari in modalità interattiva (es. timeline giornaliera con card per voli, hotel con foto/stelle, e attività collocate su mappa o ordinate cronologicamente).
  - Dashboard utente chiara per visualizzare lo storico dei viaggi e lo stato delle prenotazioni (es. "Confermato", "In attesa").
- **CSS e Stili**:
  - Sfruttare variabili CSS (`:root`) per i token di design (colori, spaziature, ombreggiature).
  - Usare flexbox e grid per layout flessibili e responsivi per dispositivi mobili.
  - Evitare classi ad-hoc non coerenti; rispettare il design system definito nella pianificazione iniziale.

---

## 5. Workflow di Lavoro dell'Agente
L'agente segue un flusso metodico suddiviso in quattro fasi principali:

```mermaid
graph TD
    A[1. Ricerca e Analisi] --> B[2. Pianificazione ed Approvazione]
    B --> C[3. Esecuzione e Test]
    C --> D[4. Verifica e Documentazione]
```

1. **Ricerca e Analisi**:
   - Analizzare lo stato del codice senza apportare modifiche.
   - Identificare dipendenze, file affetti ed eventuali rischi strutturali.
2. **Pianificazione ed Approvazione**:
   - Generare o aggiornare `implementation_plan.md`.
   - Includere domande aperte e attendere l'approvazione esplicita dell'utente prima di toccare il codice di produzione.
3. **Esecuzione e Test**:
   - Creare o aggiornare `task.md` per tracciare lo stato di avanzamento (`[ ]` -> `[/]` -> `[x]`).
    - Aggiornare man mano gli acceptance criteria passando i checkbox completati da `[ ]` a `[x]` durante l'implementazione.
   - Implementare i moduli backend e i componenti frontend a piccoli passi logici.
   - Eseguire i test automatici o i comandi di build locali per verificare che non ci siano errori sintattici o di runtime.
4. **Verifica e Documentazione**:
   - Creare un resoconto finale in `walkthrough.md` per descrivere le modifiche apportate, le verifiche effettuate e inserire screenshot/registrazioni se applicabile.
   - Mantenere commenti e docstrings esistenti nel codice per non compromettere la manutenibilità futura.

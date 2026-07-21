"""
AI Travel Assistant — FastAPI Application

Entry point del server backend. Configura CORS, registra i router
e espone l'interfaccia Swagger UI per il testing interattivo.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.chat import router as chat_router
from backend.app.api.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestisce il ciclo di vita dell'applicazione (startup/shutdown)."""
    import os
    import subprocess
    import urllib.request
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(usecwd=True))

    # Startup: inizializza il database relazionale
    from backend.app.database import init_db
    init_db()
    print("[OK] Database relazionale inizializzato.", flush=True)

    tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"
    api_key = os.getenv("LANGCHAIN_API_KEY", "")

    if tracing_enabled and (not api_key or "chiave" in api_key or "your" in api_key):
        print("[INFO] LangSmith API Key non configurata o placeholder in .env. Tracing disabilitato.", flush=True)
        os.environ.pop("LANGCHAIN_TRACING_V2", None)
        os.environ.pop("LANGCHAIN_API_KEY", None)
    elif tracing_enabled:
        project = os.getenv("LANGCHAIN_PROJECT", "ai-travel-assistant")
        print(f"[OK] LangSmith Tracing attivo (Progetto: '{project}').", flush=True)

    # Gestione Startup Ollama Locale se configurato
    provider = os.getenv("LLM_PROVIDER", "google").lower()
    model_name = os.getenv("LLM_MODEL", "qwen2.5:14b")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_process = None

    print(f"[CONFIG] Provider LLM Rilevato: '{provider}' | Modello: '{model_name}'", flush=True)

    if provider == "ollama":
        print(f"[OLLAMA] Verifico stato del servizio locale su {ollama_base_url}...", flush=True)
        try:
            req = urllib.request.urlopen(f"{ollama_base_url}/api/tags", timeout=2)
            print("[OLLAMA] Servizio Ollama già attivo ed in ascolto.", flush=True)
        except Exception:
            print("[OLLAMA] Servizio non attivo. Avvio di 'ollama serve' in background...", flush=True)
            try:
                ollama_process = subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print("[OLLAMA] Processo Ollama avviato con successo.", flush=True)
            except Exception as e:
                print(f"[WARN] Impossibile avviare automaticamente Ollama: {e}", flush=True)

    yield

    # Shutdown: cleanup e rilascio VRAM GPU per Ollama
    if provider == "ollama":
        print(f"[OLLAMA] Arresto del modello '{model_name}' e rilascio VRAM GPU...", flush=True)
        try:
            subprocess.run(["ollama", "stop", model_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            print(f"[OK] VRAM GPU rilasciata con successo per {model_name}.", flush=True)
        except Exception as e:
            print(f"[WARN] Impossibile arrestare il modello {model_name}: {e}", flush=True)

        if ollama_process:
            print("[OLLAMA] Chiusura del processo Ollama avviato all'avvio...", flush=True)
            ollama_process.terminate()

    print("[BYE] Server in fase di spegnimento.", flush=True)



app = FastAPI(
    title="AI Travel Assistant",
    description=(
        "Backend API per l'assistente di viaggio intelligente. "
        "Gestisce la conversazione con un agente LangChain che cerca voli, "
        "hotel e attività, e permette la prenotazione con approvazione umana."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ────────────────────────────────────────────────────────────────
# Configurazione CORS per il frontend
# ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ────────────────────────────────────────────────────────────────
# Registrazione dei router
# ────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(chat_router)


# ────────────────────────────────────────────────────────────────
# Redirect alla documentazione per evitare 404 sulla root
# ────────────────────────────────────────────────────────────────
from fastapi.responses import RedirectResponse

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Reindirizza l'utente alla documentazione interattiva (Swagger UI)."""
    return RedirectResponse(url="/docs")


# ────────────────────────────────────────────────────────────────
# Health check
# ────────────────────────────────────────────────────────────────
@app.get(
    "/health",
    tags=["System"],
    summary="Verifica lo stato del server",
)
async def health_check():
    """Restituisce lo stato corrente del server."""
    return {"status": "ok", "service": "AI Travel Assistant"}

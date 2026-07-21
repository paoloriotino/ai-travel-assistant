"""
Modulo dell'agente conversazionale di viaggio.

Utilizza create_agent() con MemorySaver e HumanInTheLoopMiddleware
per gestire sessioni di chat persistenti e approvazione delle prenotazioni.
"""

import os
import sqlite3
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, AIMessage

from backend.app.schemas.chat import AgentStructuredResponse
from backend.app.services.tools import (
    search_activities,
    search_flights,
    search_hotels,
    book_trip,
)

# Carica le variabili d'ambiente dal file .env nella root del progetto
load_dotenv()

# Rimuovi LANGCHAIN_TRACING_V2 dall'ambiente se la chiave API non è reale per evitare chiamate fallite a LangSmith
_ls_key = os.getenv("LANGCHAIN_API_KEY", "")
if not _ls_key or "chiave" in _ls_key or "your" in _ls_key:
    os.environ.pop("LANGCHAIN_TRACING_V2", None)
    os.environ.pop("LANGCHAIN_API_KEY", None)



# Percorso per il database SQLite dei checkpoint di chat
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKPOINTS_PATH = os.path.join(BASE_DIR, "checkpoints.db")

# ────────────────────────────────────────────────────────────────
# Configurazione del modello LLM
# ────────────────────────────────────────────────────────────────
_LLM_MODEL = os.getenv("LLM_MODEL", "gemini-flash-latest")


def _get_llm():
    """Restituisce l'istanza del modello LLM (Google Gemini o Ollama locale) in base a LLM_PROVIDER in .env."""
    provider = os.getenv("LLM_PROVIDER", "google").lower()

    if provider == "ollama":
        model_name = os.getenv("LLM_MODEL", "llama3:8b")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        print(f"Inizializzazione LLM Locale (Ollama - Modello: {model_name})...", flush=True)
        
        from langchain_ollama import ChatOllama
        
        # NON usare format='json': entra in conflitto con il Tool Calling nativo di qwen2.5
        return ChatOllama(
            model=model_name,
            base_url=base_url,
            temperature=0.3,
        )

    # Comportamento predefinito: Google Gemini in Cloud
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "Variabile d'ambiente GOOGLE_API_KEY non configurata. "
            "Per usare Google Gemini, crea un file .env con GOOGLE_API_KEY=la_tua_chiave. "
            "Se vuoi usare Ollama in locale, imposta LLM_PROVIDER=ollama"
        )
    model_name = os.getenv("LLM_MODEL", "gemini-1.5-pro")

    primary_llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.3,
        convert_system_message_to_human=True,
    )

    fallbacks = [
        ChatGoogleGenerativeAI(
            model="gemini-flash-lite-latest",
            google_api_key=api_key,
            temperature=0.3,
            convert_system_message_to_human=True,
        ),
        ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.3,
            convert_system_message_to_human=True,
        ),
    ]

    return primary_llm.with_fallbacks(fallbacks, exceptions_to_handle=(Exception,))






# ────────────────────────────────────────────────────────────────
# System Prompt dell'assistente di viaggio
# ────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
Sei **TripAI**, un assistente di viaggio esperto, cordiale e professionale.

Il tuo compito è aiutare gli utenti a pianificare viaggi completi: voli, hotel e attività.

## Regole operative
1. **Rispondi sempre in italiano**, in modo chiaro, empatico e coinvolgente.
2. Usa i tool a tua disposizione per cercare informazioni reali nel database:
   - `search_flights` per i voli disponibili.
   - `search_hotels` per gli alloggi.
   - `search_activities` per esperienze e tour (ricerca semantica).
3. **Presentazione delle opzioni come elenco**: Quando proponi o elenchi opzioni (voli, alloggi o attività), presentale SEMPRE sotto forma di **lista numerata o elenco puntato chiaro** (es. `1. ✈️ ...`, `2. 🏨 ...`), evidenziando per ogni opzione i dettagli chiave (nome/rotta, prezzo, disponibilità) in modo che l'utente possa confrontarle a colpo d'occhio.
4. Quando l'utente è pronto a prenotare, riepiloga il viaggio completo (volo + hotel + attività)
   e chiedi conferma esplicita prima di usare il tool `book_trip`.
5. **NON inventare** informazioni su voli, prezzi o disponibilità. Usa SOLO i dati dei tool.
6. Se non trovi risultati, suggerisci alternative o chiedi di modificare i criteri.
7. Fai domande di follow-up nel testo della risposta per capire meglio le preferenze dell'utente.
8. **Azioni rapide suggerite (follow_up_questions)**: Popola il campo `follow_up_questions` con 2-3 **frasi o comandi pronti che L'UTENTE può inviarti con un solo click** (es. "Cerca voli da Roma a Tokyo", "Mostrami gli hotel a Parigi", "Procedi con la prenotazione", "Proponi altre attività"). NON inserire domande fatte da te all'utente!
9. **Itinerario nella scheda a destra**: L'itinerario del viaggio viene visualizzato ed aggiornato in tempo reale esclusivamente nella scheda laterale a destra del frontend tramite l'oggetto `itinerary`. Pertanto, nel testo della tua risposta conversazionale (`reply`), rispondi in modo empatico proponendo e spiegando le opzioni trovate, **SENZA riscrivere o duplicare l'intero itinerario formattato in calce al messaggio**.

## Destinazioni disponibili
Voli principalmente dagli hub italiani (Roma FCO, Milano MXP) verso oltre 40 destinazioni internazionali principali (tra cui Tokyo, Parigi, New York, Londra, Reykjavik, Sydney, Barcellona, Madrid, Berlino, Dubai, Bangkok, Singapore, Bali, Seul, Los Angeles, Miami, Rio de Janeiro, Buenos Aires, Marrakech, Venezia, Firenze, ecc.).

## Regole per l'output strutturato (itinerary in AgentStructuredResponse)
Devi compilare l'oggetto `itinerary` in modo progressivo e incrementale durante la conversazione, per consentire all'utente di vedere la sua scheda viaggio aggiornarsi in tempo reale sul pannello laterale del frontend:
1. **Destinazione**: Non appena l'utente indica la sua destinazione (es. Tokyo, Parigi, Barcellona), imposta immediatamente il campo `destination` dell'itinerario. Questa è l'informazione minima iniziale richiesta per attivare la scheda viaggio.
2. **Aggiornamento progressivo**: Nelle risposte successive, man mano che cerchi voli o alloggi e il cliente mostra preferenza per uno di essi, o quando concordate una durata o un piano di attività, aggiorna immediatamente i campi corrispondenti nell'oggetto `itinerary` (`flight_summary`, `hotel_summary`, `duration_days`, `estimated_total_price`, `daily_plan`).
3. **Persistenza dei dati**: Mantieni i dettagli precedentemente stabiliti. Ad esempio, se state discutendo delle attività o dell'hotel, non svuotare o cancellare i campi relativi al volo o alla destinazione precedentemente impostati; continua ad accumulare i dettagli confermati per mostrare lo stato consolidato in tempo reale.

## Tono
Professionale ma caloroso. Usa emoji per rendere i messaggi vivaci.
Evita risposte troppo lunghe: sii conciso ma completo.
"""


# ────────────────────────────────────────────────────────────────
# Singleton dell'agente e del checkpointer
# ────────────────────────────────────────────────────────────────
_agent = None
_checkpointer = None


def get_checkpointer() -> SqliteSaver:
    """Restituisce il checkpointer singleton SQLite per la persistenza su disco delle sessioni."""
    global _checkpointer
    if _checkpointer is None:
        conn = sqlite3.connect(CHECKPOINTS_PATH, check_same_thread=False)
        _checkpointer = SqliteSaver(conn)
    return _checkpointer


def get_agent():
    """
    Restituisce l'istanza singleton dell'agente di viaggio.

    L'agente è configurato con:
    - Tool di ricerca (voli, hotel, attività) e prenotazione (book_trip).
    - SqliteSaver per la persistenza conversazionale permanente tramite thread_id su SQLite.
    - HumanInTheLoopMiddleware per intercettare book_trip e richiedere approvazione.
    """
    global _agent
    if _agent is None:
        llm = _get_llm()
        checkpointer = get_checkpointer()
        provider = os.getenv("LLM_PROVIDER", "google").lower()

        tools = [search_activities, search_flights, search_hotels, book_trip]

        # Per Ollama: non passare response_format perché .with_structured_output() è
        # incompatibile con il Tool Calling nativo dei modelli locali (qwen2.5, llama3, ecc.).
        # Il parsing strutturato avviene in invoke_agent() tramite estrazione JSON dal testo.
        _response_format = AgentStructuredResponse if provider != "ollama" else None

        _agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt=SYSTEM_PROMPT,
            response_format=_response_format,
            checkpointer=checkpointer,
            middleware=[
                HumanInTheLoopMiddleware(
                    interrupt_on={
                        "book_trip": {
                            "allowed_decisions": ["approve", "reject"],
                        }
                    }
                )
            ],
        )
    return _agent


def _extract_text(content) -> str:
    """Estrae sempre una stringa pulita anche se content è una lista di blocchi di testo."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                text_parts.append(item["text"])
        return "".join(text_parts)
    return str(content)


def invoke_agent(message: str, thread_id: str, user_id: int) -> dict:
    """
    Invia un messaggio all'agente e restituisce la risposta.

    Args:
        message: Il messaggio dell'utente.
        thread_id: Identificativo della sessione per la persistenza.
        user_id: ID dell'utente.

    Returns:
        dict con chiavi:
          - "reply": il testo della risposta dell'agente.
          - "interrupted": True se l'agente è in attesa di approvazione humana.
          - "interrupt_info": dizionario con dettagli sull'interruzione (se presente).
    """
    actual_thread_id = f"user_{user_id}_{thread_id}"
    agent = get_agent()
    config = {
        "configurable": {"thread_id": actual_thread_id, "user_id": user_id},
        "metadata": {"thread_id": actual_thread_id, "user_id": user_id, "service": "travel-agent"},
        "recursion_limit": 15,
    }

    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config=config,
        )
    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "Quota" in err_str:
            return {
                "reply": "⏳ Il servizio Google AI Studio ha raggiunto temporaneamente il limite di richieste del tier gratuito. Attendi circa 30-60 secondi prima di inviare un nuovo messaggio.",
                "interrupted": False,
                "interrupt_info": None,
            }
        raise e

    # Controlla se l'agente si è fermato per approvazione umana
    if "__interrupt__" in result:
        interrupt_data = result["__interrupt__"]
        # Estrai le informazioni sull'interruzione
        tool_name = "book_trip"
        tool_args = {}
        if isinstance(interrupt_data, list) and len(interrupt_data) > 0:
            first_interrupt = interrupt_data[0]
            if hasattr(first_interrupt, "value"):
                val = first_interrupt.value
                if isinstance(val, dict):
                    tool_name = val.get("tool_name", "book_trip")
                    tool_args = val.get("tool_args", {})

        return {
            "reply": "⏸️ Ho preparato la prenotazione. Vuoi confermare? Rispondi per approvare o rifiutare.",
            "interrupted": True,
            "interrupt_info": {
                "tool_name": tool_name,
                "tool_args": tool_args,
            },
        }

    # Risposta normale: estrai l'ultimo messaggio dell'agente e l'eventuale structured_response
    structured_res = result.get("structured_response")
    provider = os.getenv("LLM_PROVIDER", "google").lower()

    # Per Ollama (senza response_format): prova a estrarre un JSON strutturato dal testo
    if structured_res is None and provider == "ollama":
        import json, re
        raw_text = _extract_text(result["messages"][-1].content)
        try:
            # Cerca un blocco JSON nel testo (anche se incapsulato in ```json ... ```)
            json_match = re.search(r'```json\s*({.*?})\s*```', raw_text, re.DOTALL)
            json_str = json_match.group(1) if json_match else raw_text
            parsed = json.loads(json_str)
            structured_res = AgentStructuredResponse(**parsed)
        except Exception:
            # Fallback sicuro: tratta tutto il testo come reply conversazionale
            structured_res = AgentStructuredResponse(reply=raw_text, itinerary=None, follow_up_questions=[])

    reply_text = structured_res.reply if structured_res and hasattr(structured_res, "reply") else _extract_text(result["messages"][-1].content)

    return {
        "reply": reply_text,
        "structured_data": structured_res,
        "interrupted": False,
        "interrupt_info": None,
    }


def resume_agent(thread_id: str, approve: bool, user_id: int) -> dict:
    """
    Riprende l'esecuzione dell'agente dopo un'interruzione Human-in-the-loop.

    Args:
        thread_id: Identificativo della sessione interrotta.
        approve: True per approvare la prenotazione, False per rifiutarla.
        user_id: ID dell'utente.

    Returns:
        dict con chiave "reply" contenente la risposta dell'agente dopo il resume.
    """
    from langgraph.types import Command

    actual_thread_id = f"user_{user_id}_{thread_id}"
    agent = get_agent()
    config = {
        "configurable": {"thread_id": actual_thread_id, "user_id": user_id},
        "metadata": {"thread_id": actual_thread_id, "user_id": user_id, "service": "travel-agent"},
        "recursion_limit": 15,
    }

    decision_type = "approve" if approve else "reject"
    result = agent.invoke(
        Command(resume={"decisions": [{"type": decision_type}]}),
        config=config,
    )

    structured_res = result.get("structured_response")
    reply_text = structured_res.reply if structured_res and hasattr(structured_res, "reply") else _extract_text(result["messages"][-1].content)

    return {
        "reply": reply_text,
        "structured_data": structured_res,
        "interrupted": False,
        "interrupt_info": None,
    }


def get_chat_history(thread_id: str, user_id: int) -> list[dict]:
    """
    Recupera la cronologia dei messaggi per una specifica sessione (thread_id).

    Returns:
        Lista di dizionari con chiavi: role ('user' | 'assistant'), content (str)
    """
    actual_thread_id = f"user_{user_id}_{thread_id}"
    agent = get_agent()
    config = {"configurable": {"thread_id": actual_thread_id}}
    state = agent.get_state(config)

    if not state or not state.values or "messages" not in state.values:
        return []

    history = []
    for msg in state.values["messages"]:
        if isinstance(msg, HumanMessage) or getattr(msg, "type", None) == "human":
            text = _extract_text(msg.content)
            if text.strip():
                history.append({"role": "user", "content": text})
        elif isinstance(msg, AIMessage) or getattr(msg, "type", None) == "ai":
            text = _extract_text(msg.content)
            structured_data = None
            
            # Se la risposta dell'agente usa output strutturato via tool_calls
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    if tc.get("name") == "AgentStructuredResponse":
                        args = tc.get("args", {})
                        if "reply" in args and args["reply"]:
                            text = args["reply"]
                        structured_data = args
                        break

            if text.strip() and not text.startswith("⏸️"):
                item = {"role": "assistant", "content": text}
                if structured_data:
                    item["structured_data"] = structured_data
                history.append(item)

    return history



def _extract_thread_title(history: list[dict]) -> str:
    """Ricava un titolo significativo per la conversazione (es. 'Viaggio a Parigi')."""
    for m in reversed(history):
        st = m.get("structured_data")
        if isinstance(st, dict):
            itin = st.get("itinerary")
            if isinstance(itin, dict) and itin.get("destination"):
                return f"Viaggio a {itin['destination']}"

    destinations_map = {
        "tokyo": "Tokyo", "hnd": "Tokyo",
        "parigi": "Parigi", "paris": "Parigi", "cdg": "Parigi",
        "new york": "New York", "jfk": "New York",
        "londra": "Londra", "london": "Londra", "lhr": "Londra",
        "reykjavik": "Reykjavik", "kef": "Reykjavik",
        "sydney": "Sydney", "syd": "Sydney",
        "roma": "Roma", "rome": "Roma", "fco": "Roma",
        "milano": "Milano", "milan": "Milano", "mxp": "Milano",
        "barcellona": "Barcellona", "barcelona": "Barcellona", "bcn": "Barcellona",
        "madrid": "Madrid", "mad": "Madrid",
        "berlino": "Berlino", "berlin": "Berlino", "ber": "Berlino",
        "monaco": "Monaco di Baviera", "munich": "Monaco di Baviera", "muc": "Monaco di Baviera",
        "amsterdam": "Amsterdam", "ams": "Amsterdam",
        "vienna": "Vienna", "vie": "Vienna",
        "atene": "Atene", "athens": "Atene", "ath": "Atene",
        "lisbona": "Lisbona", "lisbon": "Lisbona", "lis": "Lisbona",
        "praga": "Praga", "prague": "Praga", "prg": "Praga",
        "budapest": "Budapest", "bud": "Budapest",
        "copenaghen": "Copenaghen", "copenhagen": "Copenaghen", "cph": "Copenaghen",
        "stoccolma": "Stoccolma", "stockholm": "Stoccolma", "arn": "Stoccolma",
        "oslo": "Oslo", "osl": "Oslo",
        "helsinki": "Helsinki", "hel": "Helsinki",
        "il cairo": "Il Cairo", "cairo": "Il Cairo", "cai": "Il Cairo",
        "città del capo": "Città del Capo", "cape town": "Città del Capo", "cpt": "Città del Capo",
        "dubai": "Dubai", "dxb": "Dubai",
        "bangkok": "Bangkok", "bkk": "Bangkok",
        "singapore": "Singapore", "sin": "Singapore",
        "bali": "Bali", "dps": "Bali",
        "seul": "Seul", "seoul": "Seul", "icn": "Seul",
        "pechino": "Pechino", "beijing": "Pechino", "pek": "Pechino",
        "delhi": "Delhi", "del": "Delhi",
        "mumbai": "Mumbai", "bom": "Mumbai",
        "toronto": "Toronto", "yyz": "Toronto",
        "vancouver": "Vancouver", "yvr": "Vancouver",
        "los angeles": "Los Angeles", "lax": "Los Angeles",
        "san francisco": "San Francisco", "sfo": "San Francisco",
        "miami": "Miami", "mia": "Miami",
        "rio de janeiro": "Rio de Janeiro", "rio": "Rio de Janeiro", "gig": "Rio de Janeiro",
        "buenos aires": "Buenos Aires", "eze": "Buenos Aires",
        "città del messico": "Città del Messico", "mexico city": "Città del Messico", "mex": "Città del Messico",
        "marrakech": "Marrakech", "rak": "Marrakech",
        "venezia": "Venezia", "venice": "Venezia", "vce": "Venezia",
        "firenze": "Firenze", "florence": "Firenze", "flr": "Firenze",
    }

    full_text = " ".join(m.get("content", "") for m in history).lower()
    for key, city in destinations_map.items():
        if key in full_text:
            return f"Viaggio a {city}"

    return "Nuovo viaggio"


def get_all_threads(user_id: int) -> list[dict]:
    """
    Recupera tutte le sessioni di chat attive dal database SQLite dei checkpoint.

    Returns:
        Lista di dizionari con chiavi: thread_id, title, last_message
    """
    if not os.path.exists(CHECKPOINTS_PATH):
        return []

    conn = sqlite3.connect(CHECKPOINTS_PATH, check_same_thread=False)
    try:
        cur = conn.cursor()
        prefix = f"user_{user_id}_%"
        cur.execute("SELECT DISTINCT thread_id FROM checkpoints WHERE thread_id LIKE ?", (prefix,))
        rows = cur.fetchall()

        threads = []
        for (tid,) in rows:
            # Rimuoviamo il prefisso user_X_ prima di usarlo se chiamiamo funzioni helper
            original_tid = tid.replace(f"user_{user_id}_", "")
            history = get_chat_history(original_tid, user_id)
            if not history:
                continue

            title = _extract_thread_title(history)

            threads.append({
                "thread_id": original_tid,
                "title": title,
                "last_message": history[-1]["content"][:60] if history else "",
            })
        return threads
    except Exception as e:
        print(f"Errore nel recupero dei thread: {e}")
        return []
    finally:
        conn.close()


def delete_thread(thread_id: str, user_id: int) -> bool:
    """
    Elimina tutti i checkpoint ed i dati di una determinata sessione di chat da SQLite.

    Returns:
        True se la cancellazione ha avuto successo, False altrimenti.
    """
    if not os.path.exists(CHECKPOINTS_PATH):
        return False

    conn = sqlite3.connect(CHECKPOINTS_PATH, check_same_thread=False)
    try:
        actual_thread_id = f"user_{user_id}_{thread_id}"
        cur = conn.cursor()
        cur.execute("DELETE FROM checkpoints WHERE thread_id = ?", (actual_thread_id,))
        cur.execute("DELETE FROM writes WHERE thread_id = ?", (actual_thread_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Errore durante l'eliminazione del thread {thread_id}: {e}")
        return False
    finally:
        conn.close()




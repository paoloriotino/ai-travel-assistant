import os
import sys

# Aggiungi la root del progetto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.agents.travel_agent import invoke_agent

try:
    print("Invocando l'agente...")
    result = invoke_agent(message="Cerca attività a Parigi per 60 euro o meno", thread_id="test_recursion", user_id=1)
    print("✅ Successo!")
    print(result)
except Exception as e:
    print(f"❌ Errore: {e}")

import os
import glob
from sqlalchemy import create_engine, text

# Percorsi dei database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "db")
MAIN_DB_PATH = os.path.join(DB_DIR, "travel_assistant.db")

print("🧹 Inizio pulizia dei dati utente...")

# 1. Pulisci la tabella Bookings dal database principale
if os.path.exists(MAIN_DB_PATH):
    print(f"➜ Pulizia delle prenotazioni in {MAIN_DB_PATH}...")
    engine = create_engine(f"sqlite:///{MAIN_DB_PATH}")
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM bookings;"))
        # Decommenta la riga sotto se vuoi eliminare anche gli utenti registrati
        # conn.execute(text("DELETE FROM users;"))
    print("✅ Prenotazioni eliminate con successo.")
else:
    print(f"⚠️ Nessun database principale trovato in {MAIN_DB_PATH}")

# 2. Elimina i database dei checkpoint di LangGraph (cronologia chat)
print("➜ Eliminazione della cronologia delle chat (checkpoints)...")
checkpoint_files = glob.glob(os.path.join(DB_DIR, "checkpoints.*"))
for file_path in checkpoint_files:
    try:
        os.remove(file_path)
        print(f"  - Eliminato: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"  ⚠️ Errore nell'eliminare {os.path.basename(file_path)}: {e}")

print("✨ Pulizia completata! I tuoi voli e hotel sono ancora nel database, ma chat e prenotazioni sono state azzerate.")

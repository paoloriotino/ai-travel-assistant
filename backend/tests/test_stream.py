import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.agents.travel_agent import get_agent
import warnings
warnings.filterwarnings('ignore')

print("Avvio stream dell'agente...")
agent = get_agent()
config = {"configurable": {"thread_id": "test_stream_123", "user_id": 1}, "recursion_limit": 10}

try:
    for event in agent.stream(
        {"messages": [("user", "Cerca attività a Parigi per 60 euro o meno")]},
        config=config,
        stream_mode="values"
    ):
        messages = event.get("messages", [])
        if messages:
            last_msg = messages[-1]
            if getattr(last_msg, "type", "") == "ai":
                print(f"AI: {last_msg.content}")
                if hasattr(last_msg, "tool_calls"):
                    print(f"Tools chiamati: {last_msg.tool_calls}")
            elif getattr(last_msg, "type", "") == "tool":
                print(f"Tool Result ({last_msg.name}): {last_msg.content[:200]}")
            else:
                print(f"User: {last_msg.content}")
except Exception as e:
    print(f"Errore durante lo stream: {e}")

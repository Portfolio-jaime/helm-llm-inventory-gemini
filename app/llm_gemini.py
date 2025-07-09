import os
import requests
import json
import logging
import pandas as pd

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")

def ask_via_mcp(question: str, inventory_df: pd.DataFrame) -> str:
    """
    Envía una pregunta al servidor MCP y devuelve la respuesta.
    """
    try:
        payload = {
            "question": question,
            "inventory": inventory_df.to_dict(orient="records")
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(MCP_SERVER_URL, data=json.dumps(payload), headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            return data.get("answer", "❌ Sin respuesta del modelo.")
        else:
            return f"❌ Error MCP ({response.status_code}): {response.text}"
    except Exception as e:
        logging.exception("❌ Error al consultar MCP")
        return f"❌ Error al consultar MCP: {e}"

# Alias necesario para mcp_server
def ask_gemini(question: str, inventory_df: pd.DataFrame) -> str:
    """
    Alias explícito para usarse como 'engine' gemini desde el servidor MCP.
    """
    return ask_via_mcp(question, inventory_df)

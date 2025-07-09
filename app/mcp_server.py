import os
import json
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Dict
import uvicorn

# Simulación o integración real con motores
def mock_answer(question: str, inventory: List[Dict]) -> str:
    return f"💡 Esta es una respuesta simulada a tu pregunta: '{question}'."

def gemini_answer(question: str, inventory: List[Dict]) -> str:
    # TODO: reemplazar por integración real con Gemini si está disponible
    return f"🤖 Gemini aún no está implementado, pero tu pregunta fue: '{question}'."

def openai_answer(question: str, inventory: List[Dict]) -> str:
    # TODO: integración real con OpenAI
    return f"🔓 OpenAI aún no está implementado, pero tu pregunta fue: '{question}'."

# Configuración del motor
AVAILABLE_ENGINES = ["mock", "gemini", "openai"]
CURRENT_ENGINE = "mock"

# App FastAPI
app = FastAPI()

class MCPRequest(BaseModel):
    question: str
    inventory: List[Dict]

@app.get("/")
def root_status():
    return {
        "status": "✅ MCP Server is running",
        "available_engines": AVAILABLE_ENGINES,
        "current_engine": CURRENT_ENGINE
    }

@app.post("/mcp")
async def mcp(request: MCPRequest):
    try:
        question = request.question
        inventory = request.inventory

        if CURRENT_ENGINE == "mock":
            answer = mock_answer(question, inventory)
        elif CURRENT_ENGINE == "gemini":
            answer = gemini_answer(question, inventory)
        elif CURRENT_ENGINE == "openai":
            answer = openai_answer(question, inventory)
        else:
            answer = f"❌ Motor no soportado: {CURRENT_ENGINE}"

        return {"answer": answer}

    except Exception as e:
        return {"answer": f"❌ Error al consultar MCP: {str(e)}"}

@app.post("/set-engine")
async def set_engine(request: Request):
    try:
        data = await request.json()
        engine = data.get("engine")
        if engine not in AVAILABLE_ENGINES:
            return {"error": f"⚠️ Motor '{engine}' no válido. Usa uno de: {AVAILABLE_ENGINES}"}

        global CURRENT_ENGINE
        CURRENT_ENGINE = engine
        return {"message": f"✅ Motor cambiado a '{engine}'"}
    except Exception as e:
        return {"error": f"❌ Error al cambiar motor: {str(e)}"}

# Punto de entrada
if __name__ == "__main__":
    uvicorn.run("app.mcp_server:app", host="0.0.0.0", port=8000, reload=True)

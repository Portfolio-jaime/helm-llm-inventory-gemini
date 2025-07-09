from fastapi import FastAPI, Request
from pydantic import BaseModel
from app.inventory import get_helm_inventory
from app.llm_gemini import ask_question_about_inventory

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def root():
    return {"message": "Inventario Helm con LLM Gemini"}

@app.post("/ask")
def ask_question(data: QuestionRequest):
    try:
        df = get_helm_inventory()
        answer = ask_question_about_inventory(df, data.question)
        return {"question": data.question, "answer": answer}
    except Exception as e:
        return {"error": str(e)}

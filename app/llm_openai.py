import os
import openai
import pandas as pd

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_openai(question: str, inventory_df: pd.DataFrame) -> str:
    context = inventory_df.to_markdown(index=False)

    prompt = f"""
Eres un asistente de DevOps. Analiza el siguiente inventario Helm y responde con precisión:

Inventario:
{context}

Pregunta:
{question}

Respuesta:
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Puedes cambiar a "gpt-3.5-turbo"
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3,
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"❌ Error al consultar OpenAI: {str(e)}"

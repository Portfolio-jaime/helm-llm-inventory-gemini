import pandas as pd
from transformers import pipeline

# Asegúrate de tener el modelo descargado previamente
generator = pipeline("text-generation", model="gpt2")

def ask_local(question: str, inventory_df: pd.DataFrame) -> str:
    prompt = f"Pregunta: {question}\n\nInventario:\n{inventory_df.to_markdown(index=False)}\n\nRespuesta:"
    try:
        response = generator(prompt, max_length=300, num_return_sequences=1)
        return response[0]["generated_text"]
    except Exception as e:
        return f"❌ Error con modelo local: {str(e)}"

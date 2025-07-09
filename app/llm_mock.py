# app/llm_mock.py

def ask_mock(question: str, inventory_df) -> str:
    """
    Devuelve una respuesta simulada sin llamar a ningún modelo LLM real.
    Ideal para pruebas locales o cuando no se desea usar Gemini/OpenAI.

    Args:
        question (str): Pregunta del usuario.
        inventory_df (pd.DataFrame): Inventario de Helm en formato DataFrame.

    Returns:
        str: Respuesta simulada.
    """
    if inventory_df is not None and not inventory_df.empty:
        sample = inventory_df.iloc[0].to_dict()
        sample_str = ", ".join(f"{k}: {v}" for k, v in sample.items())
        return f"🔧 Esta es una respuesta simulada a tu pregunta: '{question}'. Aquí un ejemplo del inventario: {sample_str}"
    else:
        return f"💡 Esta es una respuesta simulada a tu pregunta: '{question}'. No se proporcionó inventario."

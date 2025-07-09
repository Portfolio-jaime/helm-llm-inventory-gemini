import subprocess
import json
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables de entorno desde .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # Modelo por defecto

def get_helm_releases():
    try:
        result = subprocess.run(["helm", "list", "-A", "-o", "json"],
                                capture_output=True, text=True, check=True)
        releases = json.loads(result.stdout)
        return releases
    except subprocess.CalledProcessError as e:
        print("❌ Error ejecutando 'helm list':", e.stderr)
        return []

def build_inventory(releases):
    inventory = []
    for release in releases:
        inventory.append({
            "Name": release.get("name"),
            "Namespace": release.get("namespace"),
            "Chart": release.get("chart"),
            "AppVersion": release.get("app_version"),
            "Revision": release.get("revision"),
            "Updated": release.get("updated"),
            "Status": release.get("status")
        })
    return pd.DataFrame(inventory)

def save_inventory(df, format="csv"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"helm_inventory_{timestamp}.{format}"
    if format == "csv":
        df.to_csv(filename, index=False)
    elif format == "json":
        df.to_json(filename, orient="records", indent=2)
    print(f"✅ Inventario guardado en: {filename}")
    return filename

def ask_question_to_llm(df, question):
    table_data = df.to_markdown(index=False)

    prompt = f"""
Eres un asistente experto en Kubernetes y Helm. Aquí tienes un inventario de componentes desplegados:

{table_data}

Con base en este inventario, responde a la siguiente pregunta:
{question}
"""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Eres un asistente técnico que analiza inventarios Helm en Kubernetes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ Error al consultar el LLM: {str(e)}"

if __name__ == "__main__":
    print("📦 Obteniendo releases de Helm desde el clúster EKS...")
    helm_data = get_helm_releases()

    if not helm_data:
        print("❌ No se pudo obtener datos de Helm.")
    else:
        inventory_df = build_inventory(helm_data)
        save_inventory(inventory_df, format="csv")

        print("\n🤖 ¿Deseas hacer una pregunta sobre el inventario? (s/n)")
        if input().lower().strip() == 's':
            pregunta = input("Escribe tu pregunta: ")
            respuesta = ask_question_to_llm(inventory_df, pregunta)
            print("\n🧠 Respuesta del asistente:")
            print(respuesta)

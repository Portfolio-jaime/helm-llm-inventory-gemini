import subprocess
import json
import sys
import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

def get_helm_releases():
    try:
        # Ejecuta helm list para obtener los charts desplegados
        result = subprocess.run(
            ["helm", "list", "-A", "-o", "json"],
            check=True,
            capture_output=True,
            text=True
        )
        releases = json.loads(result.stdout)
        return releases
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Error al ejecutar helm list: {e.stderr}")
        sys.exit(1)

def enrich_release_data(releases):
    enriched_data = []

    for release in releases:
        chart_full = release.get("chart", "")
        chart_name = chart_full.split("-")[0] if "-" in chart_full else chart_full
        chart_version = chart_full.replace(f"{chart_name}-", "") if "-" in chart_full else ""

        enriched_data.append({
            "Name": release.get("name", ""),
            "Namespace": release.get("namespace", ""),
            "Chart": chart_full,
            "Chart Name": chart_name,
            "Chart Version": chart_version,
            "App Version": release.get("app_version", ""),
            "Última versión": "desconocida"
        })

    return enriched_data

def main():
    if len(sys.argv) != 2:
        print("Uso: python get_helm_inventory.py <cluster_name>")
        sys.exit(1)

    cluster_name = sys.argv[1]
    logging.info(f"🔍 Obteniendo releases Helm para el clúster: {cluster_name}")

    releases = get_helm_releases()
    enriched = enrich_release_data(releases)

    df = pd.DataFrame(enriched)
    print(df.to_json(orient="records"))

if __name__ == "__main__":
    main()

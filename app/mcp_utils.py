import pandas as pd
from app.inventory import get_helm_inventory
from app.chart_versions import get_latest_version


def generate_context_from_inventory() -> str:
    df = get_helm_inventory()
    if df.empty:
        return "No se encontró inventario."

    df["Última versión"] = df.apply(
        lambda row: get_latest_version(row["Name"], fallback_chart=row["Chart"]),
        axis=1,
    )

    context = ""
    for _, row in df.iterrows():
        context += (
            f"{row['Name']} está instalado con la versión {row['App Version']}, "
            f"la última disponible es {row['Última versión']}.\n"
        )
    return context

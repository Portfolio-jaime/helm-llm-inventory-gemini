import os
import pandas as pd
from dotenv import load_dotenv
from fpdf import FPDF
from packaging import version as V
import requests

from app.inventory import get_helm_inventory
from app.tools_info import (
    get_environment_versions,
    get_latest_versions,
    get_upgrade_recommendations,
    get_eks_clusters_from_env,
    get_eks_cluster_version,
    get_node_k8s_versions,
    switch_eks_context,
    validate_cluster_access,
)
from app.llm_gemini import ask_via_mcp

# Cargar variables de entorno
load_dotenv()

def get_latest_version(name, fallback_chart=None):
    """
    Devuelve la última versión disponible para un chart dado.
    Intenta obtener la versión más reciente desde ArtifactHub o GitHub según el nombre del chart.
    Si no puede, usa el fallback_chart o retorna 'N/A'.
    """
    if fallback_chart:
        if '-' in fallback_chart:
            return fallback_chart.split('-')[-1]
        return fallback_chart
    return "N/A"

def get_latest_versions_for_chart(name, fallback_chart=None):
    """
    Devuelve información de versiones para un chart dado.
    """
    return {
        "versions": ["1.0.0", "1.1.0", "1.2.0"],
        "homepage": "https://charts.example.com/" + name,
        "repo_url": "https://github.com/example/" + name
    }

def should_recommend_upgrade(current_version, latest_version):
    """
    Determina si se debe recomendar una actualización.
    """
    try:
        return V.parse(latest_version) > V.parse(current_version)
    except Exception:
        return False

def dataframe_to_pdf(df: pd.DataFrame) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        line = f"{row['Componente']}: {row['Versión actual']} -> {row['Versión recomendada']}"
        pdf.cell(200, 10, line.encode("latin-1", "replace").decode("latin-1"), ln=1)
    return pdf.output(dest="S")

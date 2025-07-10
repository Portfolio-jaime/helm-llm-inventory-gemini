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

# Repositorios y fuentes oficiales conocidas
CHART_SOURCES = {
    "metrics-server": {"type": "github", "repo": "kubernetes-sigs/metrics-server"},
    "prometheus": {"type": "artifacthub", "org": "prometheus-community", "chart": "kube-prometheus-stack"},
    "karpenter": {"type": "github", "repo": "aws/karpenter"},
    "argocd": {"type": "artifacthub", "org": "argo", "chart": "argo-cd"},
    # Agrega más componentes según tu necesidad
}

def get_latest_version(name, fallback_chart=None):
    """
    Devuelve la última versión oficial disponible para un chart dado.
    Si no puede obtener la oficial, usa el fallback y lo marca con un asterisco.
    """
    name_l = name.lower()
    source = CHART_SOURCES.get(name_l)
    # 1. ArtifactHub
    if source and source["type"] == "artifacthub":
        try:
            url = f"https://artifacthub.io/api/v1/packages/helm/{source['org']}/{source['chart']}"
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            versions = res.json().get("available_versions", [])
            if versions:
                return versions[0]["version"]
        except Exception:
            pass
    # 2. GitHub
    if source and source["type"] == "github":
        try:
            url = f"https://api.github.com/repos/{source['repo']}/releases"
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            tags = [r["tag_name"] for r in res.json() if not r.get("draft") and not r.get("prerelease")]
            if tags:
                # Quita la 'v' si existe
                return tags[0].lstrip('v')
        except Exception:
            pass
    # 3. Fallback local
    if fallback_chart:
        if '-' in fallback_chart:
            fallback = fallback_chart.split('-')[-1]
        else:
            fallback = fallback_chart
        return f"{fallback}*"  # El asterisco indica que es fallback
    return "N/A*"  # No se pudo obtener oficial

def get_latest_versions_for_chart(name, fallback_chart=None):
    """
    Devuelve información de versiones para un chart dado.
    """
    return {
        "versions": [get_latest_version(name, fallback_chart)],
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

def get_latest_version_note():
    """
    Devuelve una nota explicativa sobre el significado del asterisco en la columna 'Última versión'.
    """
    return (
        "* La columna 'Última versión' muestra la versión oficial más reciente disponible en ArtifactHub o GitHub. "
        "Si aparece un asterisco (*), significa que no se pudo obtener la versión oficial y se muestra la versión local detectada."
    )

# NOTA: Para que la leyenda sea visible en la interfaz gráfica, AGREGA esto en app/web_ui.py justo después de mostrar la tabla de inventario o recomendaciones:
#
# import streamlit as st
# from app.chart_versions import get_latest_version_note
# st.caption(get_latest_version_note())
#
# Si quieres, puedo editar web_ui.py por ti para que la leyenda se muestre automáticamente.

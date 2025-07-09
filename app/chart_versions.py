import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from fpdf import FPDF
from io import BytesIO
from packaging import version as V

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
from app.chart_versions import (
    get_latest_version,
    get_latest_versions_for_chart,
    should_recommend_upgrade,
)
from app.llm_gemini import ask_via_mcp

# Cargar variables de entorno
load_dotenv()

st.set_page_config(page_title="Helm Inventory + Gemini + MCP", layout="wide")

st.title("📦 Helm Inventory + Gemini + MCP")
st.caption("Consulta versiones de Helm en tu clúster EKS y haz preguntas con LLM vía MCP")

clusters_dict = get_eks_clusters_from_env()
if not clusters_dict:
    st.error("❌ No hay clústeres definidos en .env. Agrega `EKS_CLUSTERS_JSON`.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Inventario Helm del clúster", "🧠 Recomendaciones", "🛠️ Herramientas", "💬 Preguntas"])

with tab1:
    selected_cluster = st.selectbox("Selecciona un clúster:", options=list(clusters_dict.keys()))
    region = clusters_dict[selected_cluster]
    profiles_dict = eval(os.getenv("EKS_PROFILES_JSON", "{}"))
    profile = profiles_dict.get(selected_cluster, "default")

    with st.spinner(f"🔄 Cambiando contexto a {selected_cluster} ({region})..."):
        switch_result = switch_eks_context(selected_cluster, region)
        if switch_result["status"] == "error":
            st.error(switch_result["message"])
            st.stop()

    access = validate_cluster_access()
    if access["status"] == "offline":
        st.error(access["message"])
        st.stop()
    else:
        st.success(access["message"])

    st.subheader("📋 Inventario de Helm")
    inventory_df = get_helm_inventory()
    inventory_df["Última versión"] = inventory_df.apply(
        lambda row: get_latest_version(row["Name"], fallback_chart=row["Chart"]), axis=1
    )
    st.dataframe(inventory_df)

with tab2:
    st.subheader("📊 Recomendaciones de actualización por componente")

    summary = []

    for _, row in inventory_df.iterrows():
        name = row["Name"]
        current = row.get("App Version", row.get("Chart Version", "0.0.0"))
        latest = row["Última versión"]

        try:
            info = get_latest_versions_for_chart(name, fallback_chart=row["Chart"])
            versions = info.get("versions", [])
            homepage = info.get("homepage", "")
            repo_url = info.get("repo_url", "")
        except Exception:
            versions = []
            homepage = ""
            repo_url = ""

        recommended = None
        for v in versions:
            try:
                if V.parse(v) > V.parse(current):
                    recommended = v
                    break
            except Exception:
                continue

        summary.append({
            "Componente": name,
            "Versión actual": current,
            "Versión recomendada": recommended or "—",
            "Repositorio": repo_url,
            "Homepage": homepage,
            "Últimas versiones": ", ".join(versions),
        })

    summary_df = pd.DataFrame(summary)
    st.dataframe(summary_df)

    def dataframe_to_pdf(df: pd.DataFrame) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        for _, row in df.iterrows():
            line = f"{row['Componente']}: {row['Versión actual']} -> {row['Versión recomendada']}"
            pdf.cell(200, 10, txt=line.encode("latin-1", "replace").decode("latin-1"), ln=1)
        buffer = BytesIO()
        pdf.output(buffer, "F")
        return buffer.getvalue()

    st.download_button("⬇️ Exportar CSV", data=summary_df.to_csv(index=False), file_name="recomendaciones.csv")
    st.download_button("⬇️ Exportar PDF", data=dataframe_to_pdf(summary_df), file_name="recomendaciones.pdf", mime="application/pdf")

with tab3:
    st.subheader("🛠️ Herramientas locales y versiones")

    st.markdown("### 🔍 Versiones detectadas")
    env_versions = get_environment_versions()
    st.json(env_versions)

    st.markdown("### 🌐 Últimas versiones conocidas")
    latest_versions = get_latest_versions()
    st.json(latest_versions)

    st.markdown("### 💡 Recomendaciones de actualización")
    tool_recommendations = get_upgrade_recommendations(threshold=1)
    st.json(tool_recommendations)

    st.markdown("### ☁️ Versión del clúster EKS")
    eks_version = get_eks_cluster_version(selected_cluster, region, profile)
    st.code(eks_version)

    st.markdown("### 🧩 Versiones de nodos")
    node_versions = get_node_k8s_versions()
    st.json(node_versions)

with tab4:
    st.subheader("💬 Pregunta algo al inventario")

    question = st.text_input("🤖 Haz una pregunta al inventario", placeholder="Ej: ¿Qué versión tiene Prometheus?")
    if st.button("Preguntar"):
        if question and not inventory_df.empty:
            with st.spinner("Consultando modelo..."):
                response = ask_via_mcp(question, inventory_df)
            st.markdown(f"**Respuesta:** {response}")
        else:
            st.warning("❗ Por favor, escribe una pregunta y asegúrate de que el inventario esté disponible.")

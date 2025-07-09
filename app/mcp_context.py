def build_mcp_context(inventory_df, user_query: str) -> dict:
    return {
        "instructions": (
            "Responde preguntas sobre versiones de componentes Helm desplegados "
            "en clústeres EKS. Usa el inventario proporcionado como fuente."
        ),
        "documents": [
            {
                "name": "helm_inventory",
                "content": inventory_df.to_dict(orient="records"),
                "type": "table"
            }
        ],
        "query": user_query,
    }

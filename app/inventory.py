import subprocess
import pandas as pd
from datetime import datetime

def get_helm_inventory() -> pd.DataFrame:
    try:
        result = subprocess.run(
            ["helm", "list", "--all-namespaces", "-o", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        releases = pd.read_json(result.stdout)
        if releases.empty:
            return pd.DataFrame(columns=["Name", "Namespace", "Chart", "App Version"])

        releases["App Version"] = releases["app_version"]
        return releases[["name", "namespace", "chart", "App Version"]].rename(
            columns={
                "name": "Name",
                "namespace": "Namespace",
                "chart": "Chart"
            }
        )
    except Exception as e:
        return pd.DataFrame([{"Name": "Error", "Namespace": "", "Chart": str(e), "App Version": ""}])

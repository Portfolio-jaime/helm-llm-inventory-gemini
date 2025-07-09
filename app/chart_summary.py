import requests
from packaging import version

component_registry = {
    "metrics-server": {
        "repo": "https://github.com/kubernetes-sigs/metrics-server",
        "source": "github"
    },
    "prometheus": {
        "repo": "https://github.com/prometheus-community/helm-charts",
        "chart": "kube-prometheus-stack",
        "source": "artifacthub"
    },
    "karpenter": {
        "repo": "https://github.com/aws/karpenter",
        "source": "github"
    },
    "argocd": {
        "repo": "https://github.com/argoproj/argo-helm",
        "chart": "argo-cd",
        "source": "artifacthub"
    },
}

def fetch_latest_github_versions(repo, count=4):
    url = f"https://api.github.com/repos/{repo}/releases"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        tags = [r["tag_name"] for r in res.json() if not r["draft"] and not r["prerelease"]]
        return tags[:count]
    except:
        return []

def fetch_latest_artifacthub_versions(chart, org, count=4):
    url = f"https://artifacthub.io/api/v1/packages/helm/{org}/{chart}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        versions = res.json().get("available_versions", [])[:count]
        return [v["version"] for v in versions]
    except:
        return []

def get_component_versions_summary(inventory):
    summary = []
    for _, row in inventory.iterrows():
        component = row["Name"].lower()
        cluster = row.get("Cluster", "N/A")
        installed = row["App Version"]
        registry = component_registry.get(component)

        if not registry:
            continue

        if registry["source"] == "github":
            repo_path = registry["repo"].replace("https://github.com/", "")
            latest_versions = fetch_latest_github_versions(repo_path)
        elif registry["source"] == "artifacthub":
            latest_versions = fetch_latest_artifacthub_versions(registry["chart"], registry["repo"].split("/")[0])
        else:
            latest_versions = []

        recommendation = None
        try:
            if installed not in latest_versions:
                recommendation = latest_versions[0] if latest_versions else "N/A"
        except:
            pass

        summary.append({
            "Clúster": cluster,
            "Componente": component,
            "Versión instalada": installed,
            "Últimas versiones disponibles": ", ".join(latest_versions),
            "Repositorio oficial": registry["repo"],
            "¿Requiere upgrade?": f"✅ Sí → {recommendation}" if recommendation else "❌ No"
        })

    return summary

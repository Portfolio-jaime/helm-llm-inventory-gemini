import requests

CHART_SOURCES = {
    "argocd": {"source": "artifacthub", "org": "argo", "repo": "argo-cd"},
    "argocd-bootstrap": {"source": "artifacthub", "org": "camptocamp", "repo": "argocd-bootstrap"},
    "aws-for-fluent-bit": {"source": "artifacthub", "org": "aws", "repo": "aws-for-fluent-bit"},
    "aws-load-balancer-controller": {"source": "artifacthub", "org": "aws", "repo": "aws-load-balancer-controller"},
    "csi-secrets-store": {"source": "artifacthub", "org": "kubernetes-sigs", "repo": "secrets-store-csi-driver"},
    "datadog": {"source": "artifacthub", "org": "datadog", "repo": "datadog"},
    "external-dns": {"source": "artifacthub", "org": "bitnami", "repo": "external-dns"},
    "gatekeeper": {"source": "artifacthub", "org": "gatekeeper", "repo": "gatekeeper"},
    "gatekeeper-constraints": {"source": "artifacthub", "org": "gatekeeper", "repo": "gatekeeper"},
    "gatekeeper-constrainttemplates": {"source": "artifacthub", "org": "gatekeeper", "repo": "gatekeeper"},
    "gatekeeper-mutations": {"source": "artifacthub", "org": "gatekeeper", "repo": "gatekeeper"},
    "ingress-class": {"source": "artifacthub", "org": "kong", "repo": "ingress"},
    "karpenter": {"source": "artifacthub", "org": "karpenter", "repo": "karpenter"},
    "kong-kic": {"source": "artifacthub", "org": "kong", "repo": "kong"},
    "kuma": {"source": "artifacthub", "org": "kong", "repo": "kuma"},
    "metrics-server": {"source": "artifacthub", "org": "bitnami", "repo": "metrics-server"},
    "secrets-provider-aws": {"source": "artifacthub", "org": "csi-driver", "repo": "secrets-store-csi-driver-provider-aws"},
    "snyk-monitor": {"source": "artifacthub", "org": "snyk", "repo": "snyk-monitor"},
    # Ejemplo GitHub (puedes agregar más si quieres validar también desde GitHub)
    "some-github-chart": {"source": "github", "owner": "my-org", "repo": "my-chart"},
}

def validate_artifacthub(name, org, repo):
    url = f"https://artifacthub.io/api/v1/packages/helm/{org}/{repo}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        print(f"✅ {name}: {url}")
    except Exception as e:
        print(f"❌ {name}: {url} -> {str(e)}")

def validate_github(name, owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    headers = {"Accept": "application/vnd.github+json"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            print(f"✅ {name}: {url}")
        else:
            print(f"❌ {name}: {url} (status {res.status_code})")
    except Exception as e:
        print(f"❌ {name}: {url} -> {str(e)}")

if __name__ == "__main__":
    print("🔍 Validando URLs de charts...\n")
    for name, meta in CHART_SOURCES.items():
        if meta["source"] == "artifacthub":
            validate_artifacthub(name, meta["org"], meta["repo"])
        elif meta["source"] == "github":
            validate_github(name, meta["owner"], meta["repo"])
        else:
            print(f"⚠️ {name}: Fuente desconocida: {meta['source']}")

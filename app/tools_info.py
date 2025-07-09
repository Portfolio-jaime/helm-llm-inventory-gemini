import os
import json
import subprocess
from packaging import version

def run_command(command: str) -> str:
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return f"Error ({command}): {result.stderr.strip()}"
    return result.stdout.strip()

def get_environment_versions() -> dict:
    versions = {}
    tools = {
        "kubectl": "kubectl version --client -o json",
        "helm": "helm version --template '{{ .Version }}'",
        "terraform": "terraform version -json",
        "aws-cli": "aws --version",
    }

    for tool, cmd in tools.items():
        output = run_command(cmd)
        if "Error" in output:
            versions[tool] = output
        else:
            try:
                if tool == "kubectl":
                    data = json.loads(output)
                    versions[tool] = data["clientVersion"]["gitVersion"]
                elif tool == "terraform":
                    data = json.loads(output)
                    versions[tool] = data["terraform_version"]
                elif tool == "aws-cli":
                    versions[tool] = output.split("/")[1].split(" ")[0]
                else:
                    versions[tool] = output.replace("v", "")
            except Exception:
                versions[tool] = "Parse error"
    return versions

def get_latest_versions() -> dict:
    return {
        "kubectl": "1.32.0",
        "helm": "3.15.1",
        "terraform": "1.9.1",
        "aws-cli": "2.15.28",
    }

def get_upgrade_recommendations(threshold: int = 1) -> dict:
    current = get_environment_versions()
    latest = get_latest_versions()
    recommendations = {}

    for tool in current:
        current_version = current[tool].replace("v", "")
        latest_version = latest.get(tool, "0.0.0")

        try:
            current_parsed = version.parse(current_version)
            latest_parsed = version.parse(latest_version)
            recommend = (
                (latest_parsed > current_parsed)
                and (latest_parsed.release[0] - current_parsed.release[0] >= threshold)
            )
        except Exception:
            recommend = False

        recommendations[tool] = {
            "current": current_version,
            "latest": latest_version,
            "recommend_update": recommend,
        }

    return recommendations

def get_eks_clusters_from_env() -> dict:
    raw = os.getenv("EKS_CLUSTERS_JSON")
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}

def get_profiles_from_env() -> dict:
    raw = os.getenv("EKS_PROFILES_JSON")
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}

def switch_eks_context(cluster_name: str, region: str) -> dict:
    profiles = get_profiles_from_env()
    profile = profiles.get(cluster_name, "default")
    command = f"aws eks --region {region} update-kubeconfig --name {cluster_name} --profile {profile}"
    result = run_command(command)
    if "Error" in result:
        return {"status": "error", "message": result}
    return {"status": "success", "message": f"Contexto actualizado para {cluster_name} ({region})"}

def validate_cluster_access() -> dict:
    command = "kubectl get nodes"
    result = run_command(command)
    if "Error" in result:
        return {"status": "offline", "message": result}
    return {"status": "online", "message": "Conexión al clúster establecida."}

def get_eks_cluster_version(cluster_name: str, region: str, profile: str) -> str:
    command = (
        f"aws eks describe-cluster --name {cluster_name} --region {region} "
        f"--profile {profile} --query 'cluster.version' --output text"
    )
    return run_command(command)

def get_node_k8s_versions() -> dict:
    command = "kubectl get nodes -o json"
    try:
        raw = run_command(command)
        nodes = json.loads(raw)
        return {
            node["metadata"]["name"]: node["status"]["nodeInfo"]["kubeletVersion"]
            for node in nodes.get("items", [])
        }
    except Exception as e:
        return {"error": str(e)}

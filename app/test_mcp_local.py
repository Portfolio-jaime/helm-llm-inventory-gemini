import requests
import json

payload = {
    "question": "¿Qué versión tiene Prometheus?",
    "inventory": []
}

res = requests.post("http://localhost:8000/mcp", data=json.dumps(payload), headers={"Content-Type": "application/json"})
print(res.status_code)
print(res.text)

import json
from pathlib import Path

# Caminho do JSON de assentos
json_path = Path("vendas/data/assentos.json")

# Lê o arquivo
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Corrige os modelos de "ingressos" para "vendas"
for obj in data:
    if obj["model"] == "ingressos.assento":
        obj["model"] = "vendas.assento"
    elif obj["model"] == "ingressos.ticket":
        obj["model"] = "vendas.ticket"

# Salva de volta
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Modelos corrigidos para 'vendas.assento' e 'vendas.ticket'.")

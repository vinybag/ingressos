import json
from pathlib import Path

# Caminho do seu arquivo JSON
fixture_path = Path("vendas/data/assentos.json")

# Lê o arquivo
with open(fixture_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Corrige os modelos
for obj in data:
    if obj.get("model") == "ingressos.assento":
        obj["model"] = "vendas.assento"

# Salva de volta
with open(fixture_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Fixture corrigido com sucesso! Agora rode:")
print("   python manage.py loaddata vendas/data/assentos.json")

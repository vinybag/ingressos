import json
from pathlib import Path
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps


@receiver(post_migrate)
def carregar_assentos(sender, **kwargs):
    """
    Carrega os assentos a partir do fixture JSON automaticamente
    quando o banco for migrado pela primeira vez.
    """
    if sender.name != "vendas":  # garante que roda só no app vendas
        return

    Assento = apps.get_model("vendas", "Assento")

    # Se já existem assentos, não faz nada
    if Assento.objects.exists():
        return

    fixture = Path(__file__).resolve().parent / "data" / "assentos.json"
    if not fixture.exists():
        return

    with open(fixture, "r", encoding="utf-8") as f:
        data = json.load(f)
        for obj in data:
            fields = obj["fields"]
            Assento.objects.create(
                id=obj["pk"],
                nome=fields["nome"],
                coords=fields["coords"],
                ocupado=fields.get("ocupado", False),
            )
    print("✅ Assentos carregados automaticamente do JSON.")

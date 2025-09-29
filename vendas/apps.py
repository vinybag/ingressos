from django.apps import AppConfig

class VendasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "vendas"
    label = "ingressos"  # <- esse label é o que conecta ao JSON


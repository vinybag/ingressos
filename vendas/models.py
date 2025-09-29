import uuid
from django.db import models

class Assento(models.Model):
    nome = models.CharField(max_length=100)
    coords = models.CharField(max_length=100)  # "x1,y1,x2,y2"
    ocupado = models.BooleanField(default=False)

    def __str__(self):
        return self.nome


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)

    assento_id = models.CharField(max_length=50)  # chave do JSON
    assento_label = models.CharField(max_length=50)  # "A12"

    criado_em = models.DateTimeField(auto_now_add=True)
    pdf_arquivo = models.FileField(upload_to="tickets/", blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["assento_id"], name="unique_assento_vendido")
        ]

    def __str__(self):
        return f"{self.assento_label} - {self.nome}"



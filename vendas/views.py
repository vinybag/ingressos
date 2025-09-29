import io
from pathlib import Path

from django.conf import settings
from django.db import transaction, IntegrityError
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from PIL import Image
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

from .models import Assento, Ticket

MAPA_PATH = Path(settings.BASE_DIR) / 'vendas' / 'static' / 'vendas' / 'img' / 'MAPA.png'
FUNDO_EVENTO_PATH = Path(settings.BASE_DIR) / 'vendas' / 'static' / 'vendas' / 'img' / 'fundo_evento.png'


# Página inicial
def index(request):
    try:
        with Image.open(MAPA_PATH) as im:
            natural_w, natural_h = im.size
    except Exception:
        natural_w, natural_h = (1000, 700)  # fallback

    return render(request, "vendas/index.html", {
        "natural_w": natural_w,
        "natural_h": natural_h,
    })


# API de assentos (usando o banco de dados)
def api_assentos(request):
    assentos = Assento.objects.all().values("id", "nome", "coords", "ocupado")
    data = [
        {
            "pk": a["id"],
            "fields": {
                "nome": a["nome"],
                "coords": a["coords"],
                "ocupado": a["ocupado"],
            }
        }
        for a in assentos
    ]
    return JsonResponse(data, safe=False)


# Checkout da compra
def checkout(request):
    if request.method != "POST":
        return redirect("index")

    nome = request.POST.get("nome", "").strip()
    email = request.POST.get("email", "").strip()
    whatsapp = request.POST.get("whatsapp", "").strip()
    assento_id = request.POST.get("assento_id")
    assento_label = request.POST.get("assento_label")

    if not (nome and assento_id and assento_label):
        return HttpResponse("Dados incompletos.", status=400)

    # Cria o ticket garantindo unicidade do assento
    try:
        with transaction.atomic():
            ticket = Ticket.objects.create(
                nome=nome,
                email=email,
                whatsapp=whatsapp,
                assento_id=assento_id,
                assento_label=assento_label,
            )
            # Marca assento como ocupado
            Assento.objects.filter(id=assento_id).update(ocupado=True)
    except IntegrityError:
        return HttpResponse("Este assento já foi vendido.", status=409)

    # Gera e salva o PDF
    pdf_bytes = _gera_pdf(ticket)
    filename = f"ticket_{ticket.assento_label}_{ticket.id}.pdf"

    path_rel = f"tickets/{filename}"
    abs_path = settings.MEDIA_ROOT / "tickets"
    abs_path.mkdir(parents=True, exist_ok=True)
    with open(abs_path / filename, "wb") as f:
        f.write(pdf_bytes)

    ticket.pdf_arquivo.name = path_rel
    ticket.save(update_fields=["pdf_arquivo"])

    return redirect(reverse("ver_pdf", args=[ticket.id]))


# Visualizar PDF
def ver_pdf(request, ticket_id):
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        raise Http404("Ticket não encontrado")

    if not ticket.pdf_arquivo:
        pdf_bytes = _gera_pdf(ticket)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="ticket_{ticket.assento_label}.pdf"'
        return response

    return render(request, "vendas/sucesso.html", {
        "ticket": ticket,
    })


# Função auxiliar: gerar PDF
def _gera_pdf(ticket):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    # Fundo do evento centralizado
    try:
        fundo = Image.open(FUNDO_EVENTO_PATH)
        fundo_w, fundo_h = fundo.size
        fundo_ratio = min(w / fundo_w, (h * 0.6) / fundo_h)
        fundo_w *= fundo_ratio
        fundo_h *= fundo_ratio
        x = (w - fundo_w) / 2
        y = (h - fundo_h) / 2 + 100
        c.drawImage(ImageReader(fundo), x, y, fundo_w, fundo_h)
    except Exception:
        pass

    # Texto
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(w / 2, 200, f"Nome: {ticket.nome}")
    c.drawCentredString(w / 2, 180, f"Assento: {ticket.assento_label}")

    # QR Code
    qr_data = f"{ticket.nome} - {ticket.assento_label}"
    qr = qrcode.make(qr_data)
    qr_buffer = io.BytesIO()
    qr.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    c.drawImage(ImageReader(qr_buffer), (w - 120) / 2, 40, 120, 120)

    c.showPage()
    c.save()

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


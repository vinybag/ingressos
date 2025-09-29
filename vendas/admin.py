from django.contrib import admin
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('assento_label', 'nome', 'email', 'whatsapp', 'criado_em')
    search_fields = ('assento_label', 'nome', 'email', 'whatsapp')

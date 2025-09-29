from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from vendas import views


urlpatterns = [
    path('admin/', admin.site.urls),


    path('', views.index, name='index'),
    path('api/assentos/', views.api_assentos, name='api_assentos'),
    path('checkout/', views.checkout, name='checkout'),
    path('ticket/<uuid:ticket_id>/pdf/', views.ver_pdf, name='ver_pdf'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
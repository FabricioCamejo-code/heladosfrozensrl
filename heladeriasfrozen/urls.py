from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve


urlpatterns = [

    path('', views.chat_index, name='chat_index'),
    path('handle_message/', views.handle_message, name='handle_message'),

]

# la siguiente línea se utiliza para servir archivos estáticos durante el desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
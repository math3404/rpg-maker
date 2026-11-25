from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "RPG Maker | Administração da Guilda"
admin.site.site_title = "Painel do Mestre"
admin.site.index_title = "Gerenciamento da Taverna"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("taverna.urls")),
]

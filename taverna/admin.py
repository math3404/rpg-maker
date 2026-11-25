from django.contrib import admin

from .models import Categoria, ContatoMensagem, ItemPedido, Produto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    search_fields = ("nome",)
    list_display = ("id", "nome")


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "preco", "estoque", "ativo")
    list_filter = ("categoria", "ativo")
    search_fields = ("nome", "descricao")


@admin.register(ContatoMensagem)
class ContatoMensagemAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "telefone", "data_envio")
    search_fields = ("nome", "email", "mensagem")
    readonly_fields = ("data_envio",)


@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "produto", "quantidade", "data_adicao")
    list_filter = ("data_adicao",)
    search_fields = ("usuario__username", "produto__nome")

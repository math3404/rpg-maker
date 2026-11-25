from decimal import Decimal, InvalidOperation
import logging
from functools import wraps

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST

from .forms import AventureiroCreationForm, ContatoForm, PerfilForm, ProdutoForm

logger = logging.getLogger(__name__)
from .models import Categoria, ContatoMensagem, ItemPedido, Produto
from .supabase_client import (
    adicionar_integrante,
    atualizar_integrante,
    buscar_integrantes,
    deletar_integrante,
    supabase_configurado,
)


def staff_required(view_func):
    """Exige sessão Django ativa e perfil de equipe/administrador."""
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("Esta área é restrita aos administradores da guilda.")
        return view_func(request, *args, **kwargs)
    return _wrapped


def home(request):
    return render(request, "taverna/home.html")


def quem_somos(request):
    integrantes, erro = buscar_integrantes()
    return render(request, "taverna/quem_somos.html", {
        "integrantes": integrantes,
        "supabase_configurado": supabase_configurado(),
        "erro_integrantes": erro,
    })


def produtos(request):
    produtos_locais = Produto.objects.filter(ativo=True).select_related("categoria").order_by("nome")
    produtos_api = []
    erro_api = None
    try:
        response = requests.get("https://fakestoreapi.com/products?limit=4", timeout=7)
        response.raise_for_status()
        produtos_api = response.json()
    except requests.Timeout:
        logger.exception("Timeout ao consultar a Fake Store API")
        erro_api = "A loja parceira demorou para responder. Os itens locais continuam disponíveis."
    except requests.RequestException:
        logger.exception("Falha de conexão ao consultar a Fake Store API")
        erro_api = "Não foi possível conectar à loja parceira. Os itens locais continuam disponíveis."
    except ValueError:
        logger.exception("A Fake Store API retornou uma resposta JSON inválida")
        erro_api = "A loja parceira enviou uma resposta inválida. Os itens locais continuam disponíveis."

    return render(request, "taverna/produtos.html", {
        "produtos_locais": produtos_locais,
        "produtos_api": produtos_api,
        "erro_api": erro_api,
    })


def contato(request):
    form = ContatoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Sua mensagem chegou à guilda. Obrigado por entrar em contato!")
        return redirect("contato")
    return render(request, "taverna/contato.html", {"form": form})


def cadastrar_usuario(request):
    form = AventureiroCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Conta criada! Entre para acessar sua área de aventureiro.")
        return redirect("login")
    return render(request, "taverna/cadastrar.html", {"form": form})


class GuildLoginView(LoginView):
    template_name = "taverna/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse("admin:index")
        return reverse("dashboard")


class GuildPasswordChangeView(PasswordChangeView):
    template_name = "taverna/password_change_form.html"
    success_url = reverse_lazy("password_change_done")


def password_change_done(request):
    return render(request, "taverna/password_change_done.html")


@login_required
@require_POST
def adicionar_ao_pedido(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id, ativo=True)
    with transaction.atomic():
        item, criado = ItemPedido.objects.get_or_create(
            usuario=request.user,
            produto=produto,
            defaults={"quantidade": 1},
        )
        if not criado:
            item.quantidade += 1
            item.save(update_fields=["quantidade"])
    messages.success(request, f"{produto.nome} foi adicionado à sua mochila de pedidos.")
    return redirect("produtos")


@login_required
def meus_pedidos(request):
    pedidos = ItemPedido.objects.filter(usuario=request.user).select_related("produto").order_by("-data_adicao")
    total_geral = sum((item.subtotal() for item in pedidos), Decimal("0.00"))
    return render(request, "taverna/meus_pedidos.html", {
        "pedidos": pedidos,
        "total_geral": total_geral,
    })


@login_required
def editar_pedido(request, item_id):
    item = get_object_or_404(ItemPedido, id=item_id, usuario=request.user)
    if request.method == "POST":
        try:
            quantidade = int(request.POST.get("quantidade", "1"))
            if quantidade < 1:
                raise ValueError
            item.quantidade = quantidade
            item.save(update_fields=["quantidade"])
            messages.success(request, "Quantidade atualizada.")
        except (ValueError, TypeError):
            messages.error(request, "Informe uma quantidade inteira maior que zero.")
        return redirect("meus_pedidos")
    return render(request, "taverna/editar_pedido.html", {"item": item})


@login_required
@require_POST
def remover_pedido(request, item_id):
    item = get_object_or_404(ItemPedido, id=item_id, usuario=request.user)
    item.delete()
    messages.success(request, "Item removido dos seus pedidos.")
    return redirect("meus_pedidos")


@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect("admin:index")
    return render(request, "taverna/dashboard.html", {
        "nome_exibicao": request.user.first_name or request.user.username,
        "total_pedidos": ItemPedido.objects.filter(usuario=request.user).count(),
    })


@login_required
def editar_perfil(request):
    form = PerfilForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Seu perfil foi atualizado.")
        return redirect("editar_perfil")
    return render(request, "taverna/editar_perfil.html", {"form": form})


@staff_required
def gerenciar_contatos(request):
    contatos = ContatoMensagem.objects.order_by("-data_envio")
    return render(request, "taverna/gerenciar_contatos.html", {
        "contatos": contatos,
        "total_contatos": contatos.count(),
    })


@staff_required
@require_POST
def excluir_contato(request, contato_id):
    contato = get_object_or_404(ContatoMensagem, id=contato_id)
    contato.delete()
    messages.success(request, "Mensagem removida da caixa da guilda.")
    return redirect("gerenciar_contatos")


@staff_required
def gerenciar_servicos(request):
    servicos = Produto.objects.select_related("categoria").all()
    query = request.GET.get("q", "").strip()
    categoria_id = request.GET.get("categoria", "").strip()
    status = request.GET.get("status", "").strip()

    if query:
        servicos = servicos.filter(Q(nome__icontains=query) | Q(descricao__icontains=query))
    if categoria_id:
        servicos = servicos.filter(categoria_id=categoria_id)
    if status == "ativo":
        servicos = servicos.filter(ativo=True)
    elif status == "inativo":
        servicos = servicos.filter(ativo=False)

    contexto = {
        "servicos": servicos.order_by("nome"),
        "categorias": Categoria.objects.order_by("nome"),
        "query": query,
        "categoria_selecionada": categoria_id,
        "status_selecionado": status,
        "total_servicos": Produto.objects.count(),
        "total_ativos": Produto.objects.filter(ativo=True).count(),
        "total_inativos": Produto.objects.filter(ativo=False).count(),
        "valor_catalogo": sum(Produto.objects.filter(ativo=True).values_list("preco", flat=True), Decimal("0.00")),
    }
    return render(request, "taverna/gerenciar_servicos.html", contexto)


@staff_required
def cadastrar_servico(request):
    form = ProdutoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Novo item cadastrado na loja.")
        return redirect("gerenciar_servicos")
    return render(request, "taverna/cadastrar_servico.html", {"form": form, "titulo": "Novo item"})


@staff_required
def editar_servico(request, servico_id):
    servico = get_object_or_404(Produto, id=servico_id)
    form = ProdutoForm(request.POST or None, instance=servico)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Item atualizado.")
        return redirect("gerenciar_servicos")
    return render(request, "taverna/editar_servico.html", {
        "form": form,
        "servico": servico,
        "titulo": "Editar item",
    })


@staff_required
@require_POST
def excluir_servico(request, servico_id):
    servico = get_object_or_404(Produto, id=servico_id)
    servico.delete()
    messages.success(request, "Item excluído do catálogo.")
    return redirect("gerenciar_servicos")


@staff_required
def gerenciar_equipe(request):
    integrantes, erro = buscar_integrantes()
    return render(request, "taverna/gerenciar_equipe.html", {
        "integrantes": integrantes,
        "erro_integrantes": erro,
        "supabase_configurado": supabase_configurado(),
    })


@staff_required
def cadastrar_integrante(request):
    if request.method == "POST":
        dados = {
            "nome": request.POST.get("nome", "").strip(),
            "cargo": request.POST.get("cargo", "").strip(),
            "biografia": request.POST.get("biografia", "").strip(),
            "foto_url": request.POST.get("foto_url", "").strip(),
        }
        if not dados["nome"] or not dados["cargo"] or not dados["biografia"]:
            messages.error(request, "Preencha nome, cargo e biografia.")
        else:
            sucesso, erro = adicionar_integrante(dados)
            if sucesso:
                messages.success(request, "Integrante cadastrado no Supabase.")
                return redirect("gerenciar_equipe")
            messages.error(request, erro or "Não foi possível cadastrar o integrante.")
    return render(request, "taverna/novo_integrante.html")


@staff_required
def editar_integrante(request, integrante_id):
    integrantes, erro_busca = buscar_integrantes()
    integrante = next((membro for membro in integrantes if str(membro.get("id")) == str(integrante_id)), None)
    if integrante is None:
        messages.error(request, erro_busca or "Integrante não encontrado no Supabase.")
        return redirect("gerenciar_equipe")

    if request.method == "POST":
        dados = {
            "nome": request.POST.get("nome", "").strip(),
            "cargo": request.POST.get("cargo", "").strip(),
            "biografia": request.POST.get("biografia", "").strip(),
            "foto_url": request.POST.get("foto_url", "").strip(),
        }
        if not dados["nome"] or not dados["cargo"] or not dados["biografia"]:
            messages.error(request, "Preencha nome, cargo e biografia.")
        else:
            sucesso, erro = atualizar_integrante(integrante_id, dados)
            if sucesso:
                messages.success(request, "Integrante atualizado no Supabase.")
                return redirect("gerenciar_equipe")
            messages.error(request, erro or "Não foi possível atualizar o integrante.")
    return render(request, "taverna/editar_integrante.html", {"integrante": integrante})


@staff_required
@require_POST
def excluir_integrante(request, integrante_id):
    sucesso, erro = deletar_integrante(integrante_id)
    if sucesso:
        messages.success(request, "Integrante removido do Supabase.")
    else:
        messages.error(request, erro or "Não foi possível remover o integrante.")
    return redirect("gerenciar_equipe")


@staff_required
def relatorios(request):
    total_servicos = Produto.objects.count()
    servicos_ativos = Produto.objects.filter(ativo=True).count()
    servicos_inativos = Produto.objects.filter(ativo=False).count()
    por_categoria = list(
        Produto.objects.values("categoria__nome").annotate(total=Count("id")).order_by("categoria__nome")
    )
    contexto = {
        "total_servicos": total_servicos,
        "servicos_ativos": servicos_ativos,
        "servicos_inativos": servicos_inativos,
        "categorias_dados": [item["categoria__nome"] for item in por_categoria],
        "quantidades_dados": [item["total"] for item in por_categoria],
    }
    return render(request, "taverna/relatorios.html", contexto)


@staff_required
def painel_mestre(request):
    return render(request, "taverna/painel_mestre.html", {
        "total_contatos": ContatoMensagem.objects.count(),
        "total_servicos": Produto.objects.count(),
        "total_pedidos": ItemPedido.objects.count(),
        "supabase_configurado": supabase_configurado(),
    })

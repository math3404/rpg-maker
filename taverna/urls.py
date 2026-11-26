
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("quem-somos/", views.quem_somos, name="quem_somos"),
    path("produtos/", views.produtos, name="produtos"),
    path("contato/", views.contato, name="contato"),
    path("cadastrar/", views.cadastrar_usuario, name="cadastrar"),
    path("login/", views.GuildLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path("password_reset/", views.GuildPasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="taverna/password_reset_done.html",
    ), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="taverna/password_reset_confirm.html",
    ), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="taverna/password_reset_complete.html",
    ), name="password_reset_complete"),
    path("alterar-senha/", views.GuildPasswordChangeView.as_view(), name="password_change"),
    path("alterar-senha/concluido/", views.password_change_done, name="password_change_done"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("editar-perfil/", views.editar_perfil, name="editar_perfil"),
    path("adicionar-ao-pedido/<int:produto_id>/", views.adicionar_ao_pedido, name="adicionar_ao_pedido"),
    path("meus-pedidos/", views.meus_pedidos, name="meus_pedidos"),
    path("pedido/editar/<int:item_id>/", views.editar_pedido, name="editar_pedido"),
    path("pedido/remover/<int:item_id>/", views.remover_pedido, name="remover_pedido"),
    path("painel-mestre/", views.painel_mestre, name="painel_mestre"),
    path("gerenciar/contatos/", views.gerenciar_contatos, name="gerenciar_contatos"),
    path("gerenciar/contatos/excluir/<int:contato_id>/", views.excluir_contato, name="excluir_contato"),
    path("gerenciar/servicos/", views.gerenciar_servicos, name="gerenciar_servicos"),
    path("gerenciar/servicos/novo/", views.cadastrar_servico, name="cadastrar_servico"),
    path("gerenciar/servicos/editar/<int:servico_id>/", views.editar_servico, name="editar_servico"),
    path("gerenciar/servicos/excluir/<int:servico_id>/", views.excluir_servico, name="excluir_servico"),
    path("gerenciar/equipe/", views.gerenciar_equipe, name="gerenciar_equipe"),
    path("gerenciar/equipe/novo/", views.cadastrar_integrante, name="cadastrar_integrante"),
    path("gerenciar/equipe/editar/<int:integrante_id>/", views.editar_integrante, name="editar_integrante"),
    path("gerenciar/equipe/excluir/<int:integrante_id>/", views.excluir_integrante, name="excluir_integrante"),
    path("relatorios/", views.relatorios, name="relatorios"),
]

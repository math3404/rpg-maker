from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Categoria, ContatoMensagem, ItemPedido, Produto


class RpgMakerFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username="mestre_teste",
            email="mestre@example.test",
            password="SenhaForte123!",
        )
        cls.cliente = User.objects.create_user(
            username="aventureiro_teste",
            email="cliente@example.test",
            password="SenhaForte123!",
        )
        categoria = Categoria.objects.create(nome="Teste")
        cls.produto = Produto.objects.create(
            nome="Jogo de teste",
            descricao="Produto usado nos testes automatizados.",
            preco="49.90",
            categoria=categoria,
            estoque=5,
            ativo=True,
        )

    def test_paginas_publicas_carregam(self):
        for url_name in ("home", "quem_somos", "contato", "login", "cadastrar", "password_reset"):
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200, url_name)

    @patch("taverna.views.requests.get")
    def test_produtos_exibe_catalogo_local_se_api_externa_falhar(self, mock_get):
        import requests
        mock_get.side_effect = requests.ConnectionError("sem conexão")
        response = self.client.get(reverse("produtos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.produto.nome)

    def test_cliente_acessa_dashboard_e_nao_acessa_gestao(self):
        self.client.force_login(self.cliente)
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 200)
        self.assertEqual(self.client.get(reverse("gerenciar_contatos")).status_code, 403)
        self.assertEqual(self.client.get(reverse("gerenciar_servicos")).status_code, 403)

    def test_admin_e_redirecionado_para_admin_django(self):
        response = self.client.post(reverse("login"), {
            "username": "mestre_teste",
            "password": "SenhaForte123!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("admin:index"))

    @patch("taverna.views.requests.get")
    def test_produtos_exibe_preco_e_link_de_login_para_visitante(self, mock_get):
        import requests
        mock_get.side_effect = requests.ConnectionError("sem conexão")
        response = self.client.get(reverse("produtos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "R$")
        self.assertContains(response, "Entrar para comprar")

    @patch("taverna.views.requests.get")
    def test_cliente_e_admin_veem_preco_e_botao_comprar(self, mock_get):
        import requests
        mock_get.side_effect = requests.ConnectionError("sem conexão")
        for usuario in (self.cliente, self.admin):
            with self.subTest(usuario=usuario.username):
                self.client.force_login(usuario)
                response = self.client.get(reverse("produtos"))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "R$")
                self.assertContains(response, "Comprar")

    def test_cliente_adiciona_produto_ao_pedido_com_post(self):
        response_anonimo = self.client.post(reverse("adicionar_ao_pedido", args=[self.produto.id]))
        self.assertEqual(response_anonimo.status_code, 302)
        self.assertIn(reverse("login"), response_anonimo["Location"])

        self.client.force_login(self.cliente)
        response = self.client.post(reverse("adicionar_ao_pedido", args=[self.produto.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ItemPedido.objects.filter(usuario=self.cliente, produto=self.produto).exists())

    def test_contato_publico_salva_mensagem(self):
        response = self.client.post(reverse("contato"), {
            "nome": "Visitante",
            "email": "visitante@example.test",
            "telefone": "11999999999",
            "mensagem": "Gostaria de conhecer a ludoteca.",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ContatoMensagem.objects.filter(email="visitante@example.test").exists())

    def test_exclusao_de_contato_requer_administrador_e_post(self):
        contato = ContatoMensagem.objects.create(
            nome="Visitante", email="visitante@example.test", mensagem="Olá"
        )
        self.client.force_login(self.cliente)
        self.assertEqual(self.client.post(reverse("excluir_contato", args=[contato.id])).status_code, 403)
        self.client.force_login(self.admin)
        self.assertEqual(self.client.post(reverse("excluir_contato", args=[contato.id])).status_code, 302)
        self.assertFalse(ContatoMensagem.objects.filter(id=contato.id).exists())

    @patch("taverna.supabase_client.requests.request")
    def test_supabase_envia_secret_key_no_apikey_header(self, mock_request):
        from .supabase_client import buscar_integrantes
        response = Mock()
        response.ok = True
        response.status_code = 200
        response.content = b'[]'
        response.json.return_value = []
        mock_request.return_value = response
        with patch.dict("os.environ", {"SUPABASE_URL": "https://example.supabase.co", "SUPABASE_SECRET_KEY": "sb_secret_test_only"}):
            data, erro = buscar_integrantes()
        self.assertEqual(data, [])
        self.assertIsNone(erro)
        self.assertEqual(mock_request.call_args.kwargs["headers"]["apikey"], "sb_secret_test_only")
        self.assertNotIn("Authorization", mock_request.call_args.kwargs["headers"])

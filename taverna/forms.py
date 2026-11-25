from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import ContatoMensagem, Produto


class AventureiroCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="E-mail")
    first_name = forms.CharField(max_length=150, required=True, label="Nome")

    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")
        labels = {"username": "Nome de usuário"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_theme()

    def apply_theme(self):
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class ContatoForm(forms.ModelForm):
    class Meta:
        model = ContatoMensagem
        fields = ("nome", "telefone", "email", "mensagem")
        labels = {
            "nome": "Seu nome",
            "telefone": "Telefone (opcional)",
            "email": "E-mail",
            "mensagem": "Sua mensagem",
        }
        widgets = {
            "mensagem": forms.Textarea(attrs={"rows": 5}),
            "telefone": forms.TextInput(attrs={"placeholder": "(00) 00000-0000"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        labels = {"first_name": "Nome", "last_name": "Sobrenome", "email": "E-mail"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ("nome", "descricao", "preco", "categoria", "estoque", "foto", "ativo")
        labels = {
            "nome": "Nome do item",
            "descricao": "Descrição",
            "preco": "Preço (R$)",
            "categoria": "Categoria",
            "estoque": "Estoque",
            "foto": "URL da imagem",
            "ativo": "Disponível na loja",
        }
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 4}),
            "preco": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "estoque": forms.NumberInput(attrs={"min": "0"}),
            "foto": forms.URLInput(attrs={"placeholder": "https://..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        self.fields["ativo"].widget.attrs["class"] = "form-check-input"

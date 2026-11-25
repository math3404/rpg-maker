from decimal import Decimal
from django.db import migrations


def criar_catalogo_inicial(apps, schema_editor):
    Categoria = apps.get_model("taverna", "Categoria")
    Produto = apps.get_model("taverna", "Produto")

    categoria, _ = Categoria.objects.get_or_create(nome="Boardgames")
    produtos = [
        {
            "nome": "Catan",
            "descricao": "O clássico de estratégia em que os jogadores coletam recursos, constroem estradas e expandem seus povoados em uma ilha modular.",
            "preco": Decimal("229.99"), "estoque": 1,
            "foto": "https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?w=700&auto=format&fit=crop&q=80",
        },
        {
            "nome": "Quartz",
            "descricao": "Um jogo de sorte e gerenciamento de risco no qual anões mineradores procuram pedras preciosas em uma mina perigosa.",
            "preco": Decimal("199.99"), "estoque": 4,
            "foto": "https://images.unsplash.com/photo-1611891487122-207579d67d98?w=700&auto=format&fit=crop&q=80",
        },
        {
            "nome": "Marco Polo",
            "descricao": "Jogo de alocação de dados e estratégia em uma viagem pelas rotas comerciais entre Veneza e Pequim.",
            "preco": Decimal("339.99"), "estoque": 1,
            "foto": "https://images.unsplash.com/photo-1606503153255-59d8b8b82179?w=700&auto=format&fit=crop&q=80",
        },
        {
            "nome": "Clank!",
            "descricao": "Construa seu baralho, explore masmorras e tente roubar o tesouro do dragão sem fazer barulho demais.",
            "preco": Decimal("399.99"), "estoque": 3,
            "foto": "https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?w=700&auto=format&fit=crop&q=80",
        },
        {
            "nome": "Everdell",
            "descricao": "Um jogo de construção de cidades e gerenciamento de recursos em uma floresta fantástica habitada por criaturas.",
            "preco": Decimal("299.99"), "estoque": 4,
            "foto": "https://images.unsplash.com/photo-1606503153255-59d8b8b82179?w=700&auto=format&fit=crop&q=80",
        },
        {
            "nome": "Stone Age",
            "descricao": "Lidere uma tribo pré-histórica, colete recursos, desenvolva ferramentas e expanda sua aldeia.",
            "preco": Decimal("399.99"), "estoque": 3,
            "foto": "https://images.unsplash.com/photo-1606503153255-59d8b8b82179?w=700&auto=format&fit=crop&q=80",
        },
    ]
    for item in produtos:
        Produto.objects.get_or_create(
            nome=item["nome"],
            defaults={**item, "categoria": categoria, "ativo": True},
        )


class Migration(migrations.Migration):
    dependencies = [("taverna", "0001_initial")]

    operations = [migrations.RunPython(criar_catalogo_inicial, migrations.RunPython.noop)]

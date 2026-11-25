from django.db import migrations


def atualizar_catalogo_para_rpg(apps, schema_editor):
    Categoria = apps.get_model("taverna", "Categoria")
    Produto = apps.get_model("taverna", "Produto")

    # Atualiza a categoria sem recriar registros nem perder pedidos existentes.
    Categoria.objects.filter(nome="Boardgames").update(nome="Equipamentos e Artefatos")

    itens = {
        "Catan": {
            "nome": "Poção de Vida",
            "descricao": "Uma poção rubra preparada pelos alquimistas da guilda. Recupera as forças do aventureiro após batalhas difíceis.",
        },
        "Quartz": {
            "nome": "Elixir de Mana",
            "descricao": "Um elixir azul de energia arcana, usado por magos e conjuradores para restaurar suas reservas mágicas.",
        },
        "Marco Polo": {
            "nome": "Espada de Ferro",
            "descricao": "Uma espada confiável, forjada em ferro resistente. Companheira ideal para quem está começando sua jornada.",
        },
        "Clank!": {
            "nome": "Escudo do Guardião",
            "descricao": "Um escudo reforçado com o brasão da guilda. Ajuda a proteger seu portador dos golpes mais perigosos.",
        },
        "Everdell": {
            "nome": "Armadura do Explorador",
            "descricao": "Uma armadura leve de couro e placas, feita para aventureiros que precisam de proteção e mobilidade.",
        },
        "Stone Age": {
            "nome": "Pergaminho Arcano",
            "descricao": "Um pergaminho antigo com inscrições mágicas. Dizem que guarda conhecimentos esquecidos de outros reinos.",
        },
    }

    for nome_antigo, dados in itens.items():
        Produto.objects.filter(nome=nome_antigo).update(
            nome=dados["nome"],
            descricao=dados["descricao"],
            foto=None,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("taverna", "0002_catalogo_inicial"),
    ]

    operations = [
        migrations.RunPython(atualizar_catalogo_para_rpg, migrations.RunPython.noop),
    ]

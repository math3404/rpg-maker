## Arquivo de ambiente no Windows

Abra o PowerShell na pasta que contém `manage.py` e execute:

```powershell
Copy-Item .env.example .env
notepad .env
```

Preencha `SUPABASE_URL` e `SUPABASE_SECRET_KEY` no arquivo `.env` (não no `.env.example`). O carregador também reconhece `.env.txt`, caso o Windows tenha acrescentado essa extensão. Para conferir apenas se os arquivos existem, sem mostrar segredos:

```powershell
python -c "from pathlib import Path; p=Path('manage.py').resolve().parent; print('Pasta do projeto:', p); print('.env existe:', (p/'.env').is_file()); print('.env.txt existe:', (p/'.env.txt').is_file())"
```

Para conferir quais variáveis foram carregadas, sem imprimir seus valores:

```powershell
python manage.py shell -c "import os; print('SUPABASE_URL carregada:', bool(os.getenv('SUPABASE_URL'))); print('SUPABASE_SECRET_KEY carregada:', bool(os.getenv('SUPABASE_SECRET_KEY'))); print('A chave é publishable:', os.getenv('SUPABASE_SECRET_KEY', '').startswith('sb_publishable_'))"
```

# RPG Maker — Projeto Final WEB III

Projeto Django com tema de fantasia/RPG, reaproveitando a base enviada. O catálogo, usuários, mensagens e pedidos são gerenciados pelo Django; os integrantes da equipe são lidos e gerenciados no Supabase.

## Páginas e funcionalidades

- Home, Quem Somos, Ludoteca e Contato público.
- Cadastro, login, logout e recuperação nativa de senha do Django.
- Login de administrador redireciona para `/admin/`; clientes seguem para `/dashboard/`.
- Perfil do cliente, alteração de senha e Meus Pedidos.
- Compra de itens locais permitida apenas para usuário autenticado.
- Área de gestão restrita a usuários `is_staff`: mensagens, catálogo, equipe Supabase e relatórios.
- Catálogo local e vitrine externa via Fake Store API.
- Gráficos de relatório alimentados pelos registros do banco.

## Rodar localmente (Windows / PowerShell)

1. Instale Python 3.13 ou compatível.
2. Abra o terminal na pasta principal do projeto, onde estão `manage.py` e `requirements.txt`.
3. Crie o ambiente e instale as dependências:

   ```powershell
   py -3.13 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. Copie `.env.example` para `.env`. Para começar localmente, pode manter `DEBUG=True` e deixar `DATABASE_URL` vazio; isso usa SQLite.
5. Execute:

   ```powershell
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

6. Abra `http://127.0.0.1:8000/`.

A migração `0002_catalogo_inicial` cria exemplos do catálogo, sem criar usuários, senhas ou mensagens de terceiros.

## Configurar o Supabase

1. Entre no projeto Supabase que você controla.
2. No SQL Editor, execute o conteúdo de `sql/supabase_integrantes.sql`. A migração cria ou complementa `public.integrantes` sem apagar registros; depois, use `sql/supabase_diagnostico.sql` para conferir a estrutura, o RLS e a quantidade de integrantes.
3. Em Project Settings → API Keys, crie uma **nova Secret key** exclusiva para o backend Django.
4. Configure no `.env` local (ou nas variáveis do serviço de hospedagem):
   - `SUPABASE_URL`: Project URL do seu projeto.
   - `SUPABASE_SECRET_KEY`: a nova Secret key (`sb_secret_...`).

   **Atenção:** a chave `sb_publishable_...` não funciona para este CRUD administrativo. Use a `sb_secret_...` somente no `.env` local ou nas variáveis privadas do serviço de hospedagem. O Django carrega o `.env` localizado junto ao `manage.py`, mesmo que o terminal esteja aberto em outra pasta.
5. Em Project Settings → API → Data API, confirme que o schema `public` está entre os schemas expostos. Reinicie o Django. A página “Quem Somos” deve listar os registros e a área do Mestre permitirá adicionar, editar e excluir.

A secret key tem acesso elevado e ignora Row Level Security. Ela é usada somente em `taverna/supabase_client.py`, no servidor; nunca deve ir para HTML, JavaScript, Git ou para o navegador. A tabela deve estar exposta na Data API do schema `public`.

## Publicar na internet (Render + Supabase)

O projeto contém `render.yaml` e `build.sh` para facilitar a publicação.

1. Crie um repositório privado chamado `rpg-maker` no GitHub e envie o conteúdo desta pasta. **Não envie `.env`, `venv/`, `.venv/` nem `db.sqlite3`.** O `.gitignore` já impede esses arquivos.
2. No Supabase, abra Connect → Connection String e escolha **Session Pooler** para obter uma URL PostgreSQL. Use essa URL como `DATABASE_URL` no Render. Esse banco PostgreSQL armazenará os dados do Django (usuários, catálogo, contatos e pedidos); a tabela `integrantes` continuará sendo consultada pela integração Supabase Data API.
3. No Render, crie um Blueprint e conecte o repositório. O `render.yaml` cria o serviço web e pede as variáveis secretas.
4. Configure no Render:
   - `DATABASE_URL`: URL PostgreSQL do Session Pooler do Supabase.
   - `SUPABASE_URL`: URL do projeto Supabase.
   - `SUPABASE_SECRET_KEY`: Secret key nova, somente no servidor.
   - `DJANGO_SECRET_KEY`: o Render gera automaticamente.
   - `DEBUG=False`.
5. Após o deploy, abra o Shell do serviço e execute `python manage.py createsuperuser` para criar seu administrador.
6. Acesse `/admin/` e cadastre/gerencie o sistema. Depois faça login com uma conta cliente para validar `/dashboard/`.

O `build.sh` instala as dependências, coleta arquivos estáticos e executa as migrações. Como o banco do Django usa PostgreSQL remoto quando `DATABASE_URL` está definido, os dados não dependem do disco temporário do servidor web.

## Recuperação de senha por e-mail

Localmente, o Django usa o backend de console por padrão: o link de redefinição aparece no terminal. Em produção, configure `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` e `DEFAULT_FROM_EMAIL` com os dados SMTP do provedor escolhido.

## Observações de segurança

- A chave Supabase que veio no ZIP original estava escrita no código e dentro do `.env`. Ela foi retirada desta versão. Revogue-a no painel do Supabase e gere outra antes de publicar.
- Crie seu próprio `DJANGO_SECRET_KEY` no ambiente de produção; não use chave de desenvolvimento.
- Usuários sem `is_staff` não conseguem acessar a gestão de contatos, serviços, equipe ou relatórios.
- Operações de compra, edição e exclusão que alteram dados usam POST com CSRF.

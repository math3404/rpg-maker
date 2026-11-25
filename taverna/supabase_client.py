"""Integração server-side com a tabela public.integrantes do Supabase.

A chave secreta nunca deve ser enviada ao navegador nem versionada no Git.
As novas chaves sb_secret_ são enviadas no cabeçalho apikey (não em Bearer).
"""
import os
import requests

from rpg_maker.environment import PROJECT_DIR, load_project_environment

# Garante o carregamento mesmo quando este módulo for usado em testes ou
# comandos fora do fluxo normal de inicialização do Django.
load_project_environment()


TIMEOUT = 10


def _config():
    base_url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    secret_key = os.getenv("SUPABASE_SECRET_KEY", "").strip()
    if not base_url or not secret_key or secret_key.startswith("sb_publishable_"):
        return None
    return base_url, secret_key


def _config_erro():
    base_url = os.getenv("SUPABASE_URL", "").strip()
    secret_key = os.getenv("SUPABASE_SECRET_KEY", "").strip()
    if not base_url:
        return (
            "SUPABASE_URL não foi encontrada. O RPG Maker procura .env (ou .env.txt) "
            f"na pasta: {PROJECT_DIR}. Confira se o arquivo está nessa pasta e se a linha "
            "começa exatamente com SUPABASE_URL= (sem 'url:' ou texto extra)."
        )
    if not secret_key:
        return "SUPABASE_SECRET_KEY não foi encontrada. Configure a Secret key (sb_secret_...) no arquivo .env."
    if secret_key.startswith("sb_publishable_"):
        return (
            "A chave configurada em SUPABASE_SECRET_KEY é pública (sb_publishable_...). "
            "Este gerenciamento precisa da Secret key (sb_secret_...) no servidor. "
            "Não envie essa chave secreta pelo chat."
        )
    return "Configuração do Supabase inválida. Confira SUPABASE_URL e SUPABASE_SECRET_KEY no .env."


def supabase_configurado():
    return _config() is not None


def _request(method, *, integrante_id=None, dados=None):
    config = _config()
    if not config:
        return None, _config_erro()

    base_url, secret_key = config
    url = f"{base_url}/rest/v1/integrantes"
    headers = {
        "apikey": secret_key,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    params = {"select": "*"}
    if integrante_id is not None:
        params["id"] = f"eq.{integrante_id}"

    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            params=params if method in {"GET", "PATCH", "DELETE"} else None,
            json=dados if dados is not None else None,
            timeout=TIMEOUT,
        )
        if not response.ok:
            try:
                detail = response.json().get("message") or response.json().get("hint") or response.text
            except ValueError:
                detail = response.text
            return None, f"Supabase respondeu HTTP {response.status_code}: {str(detail)[:240]}"
        if response.status_code == 204 or not response.content:
            return [], None
        return response.json(), None
    except requests.RequestException as exc:
        return None, f"Não foi possível conectar ao Supabase: {exc.__class__.__name__}."
    except ValueError:
        return None, "O Supabase retornou uma resposta que não pôde ser interpretada."


def buscar_integrantes():
    dados, erro = _request("GET")
    return (dados or []) if erro is None else [], erro


def adicionar_integrante(dados):
    resultado, erro = _request("POST", dados=dados)
    return erro is None, erro


def atualizar_integrante(integrante_id, dados):
    resultado, erro = _request("PATCH", integrante_id=integrante_id, dados=dados)
    return erro is None, erro


def deletar_integrante(integrante_id):
    resultado, erro = _request("DELETE", integrante_id=integrante_id)
    return erro is None, erro

"""Carrega variáveis do arquivo .env localizado ao lado de manage.py."""
from pathlib import Path
import os


PROJECT_DIR = Path(__file__).resolve().parent.parent


def load_project_environment():
    """
    Lê .env (ou .env.txt, caso o Windows tenha acrescentado a extensão).
    Variáveis já definidas no ambiente do sistema têm prioridade; valores
    ausentes ou vazios são preenchidos pelo arquivo local.
    """
    env_file = PROJECT_DIR / ".env"
    if not env_file.is_file():
        windows_fallback = PROJECT_DIR / ".env.txt"
        if windows_fallback.is_file():
            env_file = windows_fallback
        else:
            return None

    try:
        from dotenv import dotenv_values
    except ImportError:
        # python-dotenv faz parte de requirements.txt; sem ele não tentamos
        # interpretar arquivos .env manualmente de forma insegura/incompleta.
        return env_file

    for key, value in dotenv_values(env_file, encoding="utf-8-sig").items():
        if value is not None and not os.environ.get(key, "").strip():
            os.environ[key] = value.strip()
    return env_file

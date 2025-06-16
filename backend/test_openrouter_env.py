import os
from dotenv import load_dotenv
from pathlib import Path

print("=== Teste de carregamento da chave OpenRouter ===")

# Caminho do .env
dotenv_path = Path(__file__).resolve().parent / ".env"
print(f"Caminho do .env: {dotenv_path}")
print(f"Arquivo .env existe? {dotenv_path.exists()}")

# Carregar .env
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path, override=True)
    print("Arquivo .env carregado")

# Verificar a chave
openrouter_key = os.getenv("OPENROUTER_API_KEY")
print(f"OPENROUTER_API_KEY: {openrouter_key}")
print(f"Chave está configurada? {bool(openrouter_key)}")

if openrouter_key:
    print(f"Tamanho da chave: {len(openrouter_key)} caracteres")
    print(f"Começa com 'sk-or-'? {openrouter_key.startswith('sk-or-')}")

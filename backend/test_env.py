import os
from dotenv import load_dotenv
from pathlib import Path

print("Tentando carregar .env")
dotenv_path = Path(__file__).resolve().parent / ".env"
print(f"Caminho do .env: {dotenv_path}")
print(f"O arquivo existe? {dotenv_path.exists()}")

if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
    print("Variáveis carregadas")

print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
print("DEEPSEEK_API_KEY:", os.getenv("DEEPSEEK_API_KEY"))
print("QWEN_API_KEY:", os.getenv("QWEN_API_KEY"))
print("GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY"))

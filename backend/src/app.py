"""
Aplicação principal do backend req2dom
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .api.routes import router

# Configurar logging para arquivo e consola
log_path = Path(__file__).resolve().parent.parent.parent / "backend.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_path, mode="a", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente do arquivo .env (robusto para venv e execução de qualquer diretório)
try:
    # Caminho absoluto para backend/.env
    dotenv_path = Path(__file__).resolve().parent.parent / ".env"
    logger.info(f"Tentando carregar .env de: {dotenv_path}")
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path, override=True)
        logger.info(f"Variáveis de ambiente carregadas de {dotenv_path}")
    else:
        logger.warning(f"Arquivo .env não encontrado em {dotenv_path}")
except Exception as e:
    logger.error(f"Erro ao carregar .env: {e}")

# Validar se há chaves de API configuradas
if os.getenv("OPENROUTER_API_KEY"):
    logger.info("Chave de API OpenRouter configurada via variáveis de ambiente")

# Obter caminho do diretório raiz do projeto
PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(PROJ_ROOT, "frontend")

# Criar a aplicação FastAPI
app = FastAPI(
    title="req2dom API",
    description="API para converter requisitos de texto em classes de domínio",
    version="0.1.0",
)

# Configurar CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["Content-Disposition"],
    max_age=600,  # Tempo em segundos para cache da resposta preflight
)

# Incluir router da API
app.include_router(router, prefix="/api")

# Servir arquivos estáticos do frontend
app.mount("/src", StaticFiles(directory=os.path.join(FRONTEND_DIR, "src")), name="static")

# Rota raiz para servir o frontend
@app.get("/")
async def serve_frontend():
    """Servir o frontend HTML"""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# Rota para verificar se o serviço está em execução
@app.get("/status")
async def status():
    """Verificar se o serviço está a funcionar"""
    return {
        "status": "online",
        "service": "req2dom",
        "message": "Serviço de conversão de requisitos para classes de domínio"
    }

# Para executar em modo de desenvolvimento com o comando:
# uvicorn src.app:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
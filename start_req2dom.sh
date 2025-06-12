#!/bin/bash
# Script para iniciar todo o sistema req2dom

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================${NC}"
echo -e "${BLUE}      INICIANDO REQ2DOM v1.0       ${NC}"
echo -e "${BLUE}====================================${NC}"

# Verificar se Ollama está instalado
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}[ERRO] Ollama não encontrado. Por favor, instale o Ollama.${NC}"
    echo -e "${YELLOW}Visite: https://ollama.ai/ para instruções de instalação.${NC}"
    exit 1
fi

# Verificar se o modelo llama3.1:8b está disponível
echo -e "${BLUE}[INFO] A verificar se o modelo LLM está disponível...${NC}"
if ! ollama list | grep -q "llama3.1:8b"; then
    echo -e "${YELLOW}[AVISO] Modelo llama3.1:8b não encontrado. A descarregar (pode demorar vários minutos)...${NC}"
    ollama pull llama3.1:8b
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERRO] Falha ao descarregar o modelo llama3.1:8b. Verifique sua ligação à Internet.${NC}"
        echo -e "${YELLOW}O sistema ainda pode funcionar com opções de NLP ou ChatGPT.${NC}"
    else
        echo -e "${GREEN}[OK] Modelo llama3.1:8b descarregado com sucesso!${NC}"
    fi
else
    echo -e "${GREEN}[OK] Modelo llama3.1:8b já está disponível.${NC}"
fi

# Ativar ambiente virtual Python (venv)
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}[AVISO] Ambiente virtual Python (venv) não encontrado. Criando...${NC}"
    python3 -m venv venv
fi
source venv/bin/activate

# Verificar dependências Python
echo -e "${BLUE}[INFO] A verificar dependências Python...${NC}"
cd backend
python -m pip install -r requirements.txt

# Verificar se o arquivo .env existe, se não, criar a partir do .env.example
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo -e "${YELLOW}[AVISO] Arquivo .env não encontrado. Criando a partir de .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}[OK] Arquivo .env criado! Edite-o para adicionar suas chaves de API.${NC}"
elif [ ! -f ".env" ] && [ ! -f ".env.example" ]; then
    echo -e "${YELLOW}[AVISO] Nem .env nem .env.example foram encontrados. Criando .env vazio...${NC}"
    cat > .env << EOL
# Configurações de ambiente para req2dom

# API Keys para LLMs externos
OPENAI_API_KEY=
DEEPSEEK_API_KEY=
QWEN_API_KEY=
GEMINI_API_KEY=

# Configuração de idioma para processamento NLP
LANGUAGE_MODEL=pt_core_news_lg

# Configuração do modelo Llama local
DEFAULT_LLAMA_MODEL=llama3.1:8b
EOL
    echo -e "${GREEN}[OK] Arquivo .env criado! Edite-o para adicionar suas chaves de API.${NC}"
else
    echo -e "${GREEN}[OK] Arquivo .env encontrado.${NC}"
fi

# Verificar se spaCy está instalado e instalar modelos se necessário
if python -c "import spacy" &> /dev/null; then
    # Verificar se o modelo em português está instalado
    if ! python -c "import spacy; spacy.load('pt_core_news_lg')" &> /dev/null; then
        echo -e "${YELLOW}[AVISO] Modelo spaCy em português não encontrado. A descarregar (pode demorar alguns minutos)...${NC}"
        python -m spacy download pt_core_news_lg
    else
        echo -e "${GREEN}[OK] Modelo spaCy em português encontrado.${NC}"
    fi
    
    # Verificar se o modelo em inglês está instalado como fallback
    if ! python -c "import spacy; spacy.load('en_core_web_lg')" &> /dev/null; then
        echo -e "${YELLOW}[AVISO] Modelo spaCy em inglês não encontrado. A descarregar como fallback...${NC}"
        python -m spacy download en_core_web_lg
    else
        echo -e "${GREEN}[OK] Modelo spaCy em inglês (fallback) encontrado.${NC}"
    fi
else
    echo -e "${RED}[ERRO] spaCy não está instalado corretamente.${NC}"
fi

# Iniciar o modelo Ollama (Llama 3.1:8b) em background
OLLLAMA_LOG="ollama.log"
echo -e "${BLUE}[INFO] A iniciar o modelo Ollama (llama3.1:8b)... (log: $OLLLAMA_LOG)${NC}"
ollama run llama3.1:8b > "$OLLLAMA_LOG" 2>&1 &
OLLAMA_PID=$!

# Aguardar o modelo iniciar
echo -e "${BLUE}[INFO] A aguardar o modelo iniciar...${NC}"
sleep 3

# Verificar se o modelo está a funcionar
if ! curl -s http://localhost:8000/status > /dev/null; then
    echo -e "${RED}[ERRO] Não foi possível conectar ao modelo Ollama. Verifique o log em $OLLLAMA_LOG para mais informações.${NC}"
    kill $OLLAMA_PID 2>/dev/null
    exit 1
fi

# Iniciar o backend em background
BACKEND_LOG="backend.log"
echo -e "${BLUE}[INFO] A iniciar o backend na porta 8000... (log: $BACKEND_LOG)${NC}"
cd ..
(source venv/bin/activate && cd backend && python -m uvicorn src.app:app --host 0.0.0.0 --port 8000 --log-level info) > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

# Aguardar o backend iniciar
echo -e "${BLUE}[INFO] A aguardar o backend iniciar...${NC}"
sleep 3

# Verificar se o backend está a funcionar
if curl -s http://localhost:8000/status > /dev/null; then
    echo -e "${GREEN}[OK] Backend iniciado com sucesso na porta 8000!${NC}"
    echo -e "${YELLOW}Veja o log do backend em $BACKEND_LOG${NC}"
else
    echo -e "${RED}[ERRO] Não foi possível iniciar o backend. Verifique o log em $BACKEND_LOG para mais informações.${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Iniciar o frontend (frontend development server)
echo -e "${BLUE}[INFO] A iniciar o frontend...${NC}"
# Ativar venv para garantir ambiente correto
source venv/bin/activate
cd frontend


# Verificar se as dependências Node estão instaladas
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}[AVISO] Dependências Node.js não encontradas. A instalar...${NC}"
    npm install
fi

# Iniciar o servidor de desenvolvimento frontend
echo -e "${BLUE}[INFO] A iniciar o servidor de desenvolvimento frontend...${NC}"
npm run serve &
FRONTEND_PID=$!

# Aguardar o frontend iniciar
echo -e "${BLUE}[INFO] A aguardar o frontend iniciar...${NC}"
sleep 5

echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}     REQ2DOM INICIADO COM SUCESSO   ${NC}"
echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}Frontend: http://localhost:3000${NC}"
echo -e "${GREEN}Backend API: http://localhost:8000/api${NC}"
echo -e "${GREEN}Status: http://localhost:8000/status${NC}"
echo -e "${YELLOW}Prima Ctrl+C para parar todos os serviços${NC}"

# Função para encerrar processos ao receber Ctrl+C
function cleanup {
    echo -e "${BLUE}[INFO] A encerrar serviços...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    kill $OLLAMA_PID 2>/dev/null
    echo -e "${GREEN}[OK] Serviços encerrados. Obrigado por utilizar o req2dom!${NC}"
    exit 0
}

# Configurar o trap para Ctrl+C
trap cleanup SIGINT

# Manter o script em execução
while true; do
    sleep 1
done

#!/bin/bash
# Script para instalação do Stanza e seus modelos para português

echo "Instalando dependências para o processador Stanza..."

# Garantir que estamos no diretório correto
cd "$(dirname "$0")"

# Verificar ambiente virtual
if [ ! -d "venv" ]; then
  echo "Criando ambiente virtual..."
  python3 -m venv venv
fi

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Instalar/atualizar pip, setuptools, e wheel
echo "Atualizando pip, setuptools e wheel..."
pip install --upgrade pip setuptools wheel

# Instalar dependências do requirements.txt
echo "Instalando dependências..."
pip install -r requirements.txt

# Download do modelo para português
echo "Baixando modelo Stanza para português..."
python -c "import stanza; stanza.download('pt')"

echo "Instalação concluída!"
echo "Para testar o processador Stanza, execute: python test_stanza.py"
echo "Para comparar com spaCy, execute: python test_benchmark.py"

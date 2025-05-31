# req2dom - Conversor de Requisitos para Classes de Domínio

O req2dom é uma ferramenta que converte requisitos textuais de software em classes de domínio estruturadas, fornecendo uma representação JSON compatível com ferramentas de modelagem como draw.io. Este projeto utiliza processamento de linguagem natural através de modelos LLM (Large Language Models) para analisar e extrair entidades, atributos e relacionamentos a partir de requisitos em linguagem natural.

## Tecnologias Utilizadas

- **Backend**: Python 3.12, FastAPI
- **Frontend**: Vue.js, HTML, CSS, JavaScript
- **IA**: Ollama com modelo llama3.1:8b 
- **Ferramentas auxiliares**: pyenv (gestão de versões Python)

## Estrutura do Projeto

```
.
├── README.md
├── backend/           # Servidor API em Python/FastAPI
│   ├── README.md
│   ├── requirements.txt  # Dependências Python
│   └── src/           # Código-fonte do backend
│       ├── app.py     # Aplicação FastAPI principal
│       ├── api/       # Endpoints da API
│       │   └── routes.py
│       └── model/     # Processamento de LLM e geração de JSON
│           ├── domain_generator.py
│           └── llm_processor.py
└── frontend/          # Interface web em Vue.js
    ├── index.html     # Página principal
    ├── package.json   # Dependências npm
    ├── vite.config.js # Configuração do Vite
    └── src/           # Código-fonte do frontend
        ├── App.vue    # Componente principal
        ├── main.js    # Ponto de entrada
        ├── assets/    # Recursos estáticos
        │   └── css/
        │       └── style.css
        └── components/ # Componentes Vue
            ├── InputSection.vue
            └── OutputSection.vue
```

## Requisitos

- **Python 3.12** (versões mais recentes como 3.13 podem causar problemas de compatibilidade)
- Node.js e npm (para o frontend Vue.js)
- Ollama com o modelo llama3.1:8b instalado
- Navegador web moderno
- Conexão à Internet para download de dependências

## Instruções de Instalação

### 1. Configurar o ambiente Python 3.12

É **crucial** usar Python 3.12 para este projeto devido a problemas de compatibilidade com bibliotecas em versões mais recentes.

```bash
# Instalar pyenv (se ainda não estiver instalado)
curl https://pyenv.run | bash

# Adicionar ao seu ficheiro de configuração do shell
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

# Recarregar a configuração do shell
source ~/.bashrc

# Instalar Python 3.12
pyenv install 3.12.0

# Navegar até ao diretório do projeto
cd req2dom

# Definir Python 3.12 como versão local para este diretório
pyenv local 3.12.0
```

### 2. Criar e configurar o ambiente virtual

```bash
# Clonar o repositório (se ainda não o fez)
git clone https://github.com/seunome/req2dom.git
cd req2dom

# Verificar se está a usar Python 3.12
python --version  # Deve mostrar Python 3.12.x

# Criar o ambiente virtual
python -m venv venv

# Ativar o ambiente virtual
source venv/bin/activate  # No Linux/Mac
# ou
# venv\Scripts\activate   # No Windows
```

### 3. Instalar as dependências do backend

```bash
cd backend
pip install -r requirements.txt
```

### 4. Instalar as dependências do frontend

```bash
cd ../frontend
npm install
```

### 5. Assegurar que o Ollama está instalado e configurado

```bash
# Verificar modelos disponíveis
ollama list

# Se o modelo llama3.1:8b não estiver instalado, instale-o
# (Isto pode demorar alguns minutos dependendo da sua conexão)
ollama pull llama3.1:8b
```

## Execução do Projeto

### 1. Iniciar o modelo Ollama

Num terminal:

```bash
ollama run llama3.1:8b
```

### 2. Iniciar o servidor backend

Noutro terminal:

```bash
# Ativar o ambiente virtual (se ainda não estiver ativado)
cd req2dom
source venv/bin/activate  # No Linux/Mac
# ou
# venv\Scripts\activate   # No Windows

# Iniciar o servidor backend
cd backend
uvicorn src.app:app --reload
```

O servidor backend estará disponível em [http://localhost:8000](http://localhost:8000).

### 3. Iniciar o frontend Vue.js

Noutro terminal:

```bash
# Navegar para o diretório frontend
cd frontend

# Iniciar o servidor de desenvolvimento Vue.js
npm run dev
```

O frontend estará disponível em [http://localhost:5173](http://localhost:5173) ou no endereço indicado no terminal.

## Utilização

1. Aceda à aplicação através do endereço do frontend no navegador.
2. Na interface, introduza os requisitos do sistema na área de texto à esquerda.
3. Clique no botão "Processar".
4. Aguarde enquanto o sistema processa os requisitos (isto pode demorar alguns segundos).
5. O JSON das classes de domínio gerado será exibido na área à direita.
6. Pode copiar o JSON para a área de transferência ou guardá-lo como ficheiro.
7. Importe o ficheiro JSON para o draw.io ou outra ferramenta de modelagem compatível.

## Resolução de Problemas

### O processamento parece não funcionar

- Verifique se o modelo Ollama está em execução (`ollama run llama3.1:8b`)
- Verifique se o servidor backend está em execução (`uvicorn src.app:app --reload`)
- Verifique se o frontend está em execução (`npm run dev`)
- Verifique as mensagens de erro na consola do navegador (F12)
- Verifique os logs nos terminais onde o backend e frontend estão a correr

### Erros ao instalar dependências

- Certifique-se de estar a usar Python 3.12 (`python --version`)
- Se estiver a usar uma versão diferente, siga as instruções na secção "Configurar o ambiente Python 3.12"
- Algumas bibliotecas como lxml e pydantic-core podem apresentar erros de compilação em versões mais recentes do Python

### Erros no JSON gerado

- O JSON pode não ser gerado corretamente se os requisitos forem muito complexos ou ambíguos
- Tente simplificar os requisitos e ser mais explícito na descrição das classes e atributos
- Verifique se o modelo LLM está a gerar JSON válido (veja os logs do backend)

## Licença

Este projeto está licenciado sob a licença MIT.
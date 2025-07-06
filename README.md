# req2dom - Conversor de Requisitos para Classes de Domínio

Esta ferramenta converte requisitos textuais em linguagem natural para diagramas de classes de domínio, gerando automaticamente XML compatível com draw.io. Utiliza diferentes métodos de processamento de linguagem natural e modelos de linguagem grande (LLM) para identificar entidades, atributos e relacionamentos nos requisitos.

## Funcionalidades Principais

- **Múltiplos métodos de processamento:**
  - LLM Local (Llama) via Ollama
  - LLMs Externos via OpenRouter (ChatGPT, Claude, etc.)
  - Processamento NLP baseado em spaCy e textacy
  - Processamento NLP avançado baseado em Stanza (otimizado para português de Portugal)
  - Modo Híbrido (combinação de NLP e LLM)

- **Interface web intuitiva**
- **Reconhecimento de requisitos no formato "RF[número]. [texto do requisito]"**
- **Exportação em formato XML para draw.io**
- **Visualização instantânea do diagrama gerado**

## Instalação e Execução

### Pré-requisitos

- Python 3.8+
- Node.js 14+
- npm 6+
- Git

### Instalação Rápida (Recomendada)

Após clonar o repositório, utilize o script de inicialização automática:

```bash
git clone https://github.com/seu-utilizador/req2dom.git
cd req2dom
chmod +x start_req2dom.sh
./start_req2dom.sh
```

O script irá:
1. Verificar e instalar todas as dependências
2. Criar o ambiente virtual Python
3. Instalar os modelos necessários (spaCy e Stanza)
4. Iniciar o backend e o frontend

A aplicação estará disponível em:
- Frontend: http://localhost:5173
- API: http://localhost:8000/api

### Instalação Manual

#### 1. Backend (Python/FastAPI)

```bash
cd req2dom/backend

# Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Instalar modelos para spaCy
python -m spacy download pt_core_news_lg
python -m spacy download en_core_web_lg

# Instalar e configurar Stanza (recomendado para português)
./install_stanza.sh
# ou manualmente:
# pip install stanza
# python -c "import stanza; stanza.download('pt')"

# Configurar variáveis de ambiente (opcional)
cp .env.example .env
# Edite o ficheiro .env com as suas chaves API, se necessário

# Iniciar o servidor
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend (Vue.js)

```bash
cd req2dom/frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```

## Utilização

1. Aceda à interface web em [http://localhost:5173](http://localhost:5173)
2. Insira os requisitos na área de texto
3. Selecione o método de processamento desejado
4. Clique em "Processar Requisitos"
5. Visualize o diagrama gerado e descarregue o XML para uso no draw.io

### Métodos de Processamento Disponíveis

- **LLM Local**: Utiliza o modelo Llama 3.1 via Ollama para análise semântica completa
- **LLM Externo**: Utilize modelos como ChatGPT, Claude, Gemini através do OpenRouter
- **spaCy+textacy**: Processamento NLP tradicional com análise sintática e semântica
- **Stanza**: Processamento NLP avançado com melhor suporte para português de Portugal
- **Híbrido**: Combina NLP (Stanza por padrão) com LLM para resultados mais precisos

## Estrutura do Projeto

```
req2dom/
├── backend/
│   ├── src/
│   │   ├── api/           # Rotas da API FastAPI
│   │   ├── model/         # Processadores e geradores
│   │   └── app.py         # Aplicação principal
│   ├── install_stanza.sh  # Script de instalação do Stanza
│   ├── requirements.txt   # Dependências Python
│   └── test_*.py          # Testes e benchmarks
├── frontend/
│   ├── src/
│   │   ├── components/    # Componentes Vue
│   │   ├── assets/        # Recursos estáticos
│   │   └── App.vue        # Componente principal
│   ├── index.html
│   └── package.json
└── start_req2dom.sh       # Script de inicialização

Utiliza APIs externas de LLM. Este método:
- Proporciona processamento de alta qualidade através de modelos de ponta
- Suporta múltiplos fornecedores:
  - OpenAI (GPT-3.5, GPT-4)
  - Deepseek
  - Qwen
  - Google Gemini Pro
- Requer uma chave de API válida do fornecedor escolhido
- Oferece resultados consistentes e precisos

### 3. NLP Avançado

#### Stanza (Recomendado para português)
- Processador avançado otimizado para português de Portugal
- Melhor compreensão morfológica e sintática
- Extração mais precisa de entidades e relacionamentos
- Não necessita de API externa

#### spaCy + textacy
- Oferece extração avançada de entidades e relacionamentos
- Usa modelos de linguagem treinados para maior precisão
- Ideal para textos complexos que requerem uma compreensão mais sutil

### 4. Híbrido (NLP + LLM)

# Criar o ambiente virtual
python3 -m venv venv

# Ativar o ambiente virtual
source venv/bin/activate  # No Linux/Mac
# ou
# venv\Scripts\activate   # No Windows
```

### 2. Instalar as dependências do backend

```bash
cd backend
pip install -r requirements.txt
```

### 3. Assegurar que o Ollama está instalado e configurado

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

O servidor estará disponível em [http://localhost:8000](http://localhost:8000).

### 3. Aceder à aplicação

Agora aceder á aplicação em [http://localhost:8000](http://localhost:8000).

## Utilização

1. Na interface do utilizador, introduza os requisitos do sistema na área de texto à esquerda.
2. Clique no botão "Processar".
3. Aguarde enquanto o sistema processa os requisitos (isto pode demorar alguns segundos).
4. O XML das classes de domínio gerado será exibido na área de texto à direita.
5. Pode copiar o XML para a área de transferência ou guardá-lo como ficheiro.
6. Importe o ficheiro XML para o DrawIO ou outra ferramenta de modelagem compatível.

## Exemplos

### Sistema de Gestão de Biblioteca

```
O sistema de biblioteca deve permitir que os utilizadores requisitem livros. 
Cada livro tem um título, autor e código ISBN. 
Os utilizadores devem ser registados no sistema com nome, email e endereço. 
Um utilizador pode ter várias requisições ativas.
```

### Sistema de Gestão de Encomendas

```
RF01: O cliente deve poder registar-se no sistema fornecendo nome, email e telefone.
RF02: O cliente pode adicionar produtos ao carrinho de compras.
RF03: Os produtos têm nome, descrição, preço e quantidade em stock.
RF04: O sistema deve permitir que o cliente finalize a compra gerando uma encomenda.
RF05: Cada encomenda tem um código único, data, estado e valor total.
```

## Testes e Avaliação

Para testar o processador Stanza:
```bash
cd backend
python test_stanza.py
```

Para comparar o desempenho entre Stanza e spaCy:
```bash
cd backend
python test_benchmark.py
```

## Testes

O projeto inclui vários scripts de teste para validar o funcionamento dos processadores:

```bash
cd backend

# Testar o processador Stanza
python test_stanza.py

# Comparar performance entre Stanza e spaCy
python test_benchmark.py

# Testes gerais
python test_generic.py
```

## Configuração Avançada

Para configurar chaves de API externa ou ajustar configurações, edite o ficheiro `.env` no diretório `backend`:

```
# API Key para OpenRouter (necessária para LLM externo)
OPENROUTER_API_KEY=sua_chave_aqui

# Configuração do idioma para processamento NLP
LANGUAGE_MODEL=pt_core_news_lg

# Configuração do modelo Llama local
DEFAULT_LLAMA_MODEL=llama3.1:8b
```

## Contribuições

Contribuições são bem-vindas! Por favor, envie pull requests para melhorias ou correções.

## Licença

Este projeto está licenciado sob a licença MIT.

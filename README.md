# req2dom - Requisitos para Classes de Domínio

Esta ferramenta converte requisitos textuais em diagramas de classes de domínio, gerando automaticamente XML para visualização em draw.io. Ela utiliza diferentes métodos de processamento de linguagem natural e modelos de linguagem grande (LLM) para identificar entidades, atributos e relacionamentos.

A ferramenta suporta múltiplos métodos de processamento:

- LLM Local (Llama) via Ollama
- LLMs Externos (ChatGPT, Deepseek, Qwen, Google Gemini Pro)
- Processamento NLP baseado em spaCy
- Modo Híbrido (combinação de NLP e LLM)
- NLP Avançado (spaCy + textacy)

Também suporta o reconhecimento de requisitos no formato "RF[número]. [texto do requisito]".

## Visão Geral

O req2dom é uma aplicação web que permite aos usuários:

- Inserir requisitos textuais em linguagem natural
- Processar estes requisitos utilizando diferentes métodos (LLM, NLP ou híbrido)
- Gerar diagramas de classe no formato draw.io
- Visualizar, editar e exportar os diagramas gerados

![Exemplo de fluxo](https://i.imgur.com/example.png)

## Instalação e Execução

### Backend (Python/FastAPI)

1. Acesse a pasta do backend:
   ```bash
   cd backend
   ```
2. Crie um ambiente virtual Python (recomendado):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   pip install spacy textacy
   python -m spacy download pt_core_news_lg  # Para português
   # ou
   python -m spacy download en_core_web_lg   # Para inglês
   ```
4. Configure as chaves de API no arquivo `.env` (veja exemplo em `.env.example`).
5. Inicie o backend:
   ```bash
   uvicorn src.app:app --reload
   ```

### Frontend (Vue.js)

1. Abra um novo terminal e acesse a pasta do frontend:
   ```bash
   cd frontend
   ```
2. Instale as dependências:
   ```bash
   npm install
   ```
3. Inicie o servidor de desenvolvimento:
   ```bash
   npm run serve
   ```

A interface estará disponível em http://localhost:3000 e a API em http://localhost:8000/api

## Configuração das Chaves de API

Para utilizar LLMs externos (OpenAI, Deepseek, Qwen, Google Gemini Pro), configure as chaves de API no arquivo `.env` dentro da pasta `backend`:

1. Copie o arquivo de exemplo:
   ```bash
   cd backend
   cp .env.example .env
   ```
2. Edite o arquivo `.env` e preencha as chaves:
   ```
   OPENAI_API_KEY=sua_chave_api_openai_aqui
   DEEPSEEK_API_KEY=sua_chave_api_deepseek_aqui
   QWEN_API_KEY=sua_chave_api_qwen_aqui
   GEMINI_API_KEY=sua_chave_api_gemini_aqui
   ```

> ⚠️ **Importante**: Para utilizar o método "LLM Externo" na interface, é **obrigatório** configurar a chave API correspondente no arquivo `.env` ou fornecer uma chave temporária na interface. Se o botão "Processar com chave do servidor" não funcionar, verifique se o backend está lendo corretamente o arquivo `.env` (confira os logs do backend).

> ⚠️ **Segurança**: O arquivo `.env` contém informações sensíveis e não deve ser compartilhado ou versionado. Ele já está incluído no `.gitignore` para evitar commits acidentais.

## Métodos de Processamento

A ferramenta oferece cinco métodos para analisar e extrair classes de domínio a partir de requisitos textuais:

### 1. LLM Local (Llama)

Usa exclusivamente o modelo Llama 3.1 8B local para analisar os requisitos. Este método:
- Oferece excelente compreensão semântica e contextual do texto
- Pode identificar entidades implícitas nos requisitos
- Requer mais recursos computacionais
- Funciona totalmente offline sem necessidade de API externa
- Timeout estendido de 10 minutos para processamento de requisitos complexos
- Ideal para requisitos complexos ou ambíguos

### 2. LLM Externo (ChatGPT, Deepseek, Qwen, Google Gemini Pro)

Utiliza APIs de LLMs externos para processar os requisitos. Este método:
- Proporciona processamento de alta qualidade na cloud
- Suporta múltiplos provedores:
  - OpenAI (ChatGPT)
  - Deepseek
  - Qwen (Alibaba Cloud)
  - Google Gemini Pro
- Requer uma chave de API válida do provedor escolhido
- Oferece resultados consistentes e precisos
- Ideal para requisitos complexos quando não há recursos locais suficientes

### 3. NLP (Processamento de Linguagem Natural com spaCy)

Usa técnicas tradicionais de NLP através do spaCy para identificar entidades e relacionamentos. Este método:
- É mais rápido e usa menos recursos
- Baseia-se em análise gramatical e de dependências
- Pode ser menos preciso em textos ambíguos
- Funciona bem com requisitos claros e estruturados

### 4. NLP Avançado (spaCy + textacy)

Combina o poder do spaCy com o textacy para uma análise linguística mais profunda. Este método:
- Oferece extração avançada de entidades e relacionamentos
- Usa modelos de linguagem treinados para maior precisão
- Ideal para textos complexos que requerem uma compreensão mais sutil
- Pode identificar padrões e entidades que outros métodos não conseguem

### 5. Híbrido (NLP + LLM)

Combina as abordagens: usa NLP para identificação inicial das entidades e o LLM para refinamento. Este método:
- Oferece um bom equilíbrio entre velocidade e qualidade
- Reduz a carga sobre o LLM ao fornecer estrutura inicial
- Combina precisão gramatical do NLP com compreensão semântica do LLM
- Recomendado para a maioria dos casos de uso

## Uso

1. Acesse a interface web em http://localhost:3000
2. Insira os requisitos do sistema na área de texto
3. Selecione o método de processamento desejado (LLM, NLP ou Híbrido)
4. Opcionalmente, especifique o caminho para um modelo Llama local
5. Clique em "Processar"
6. Visualize o XML gerado ou use o botão "Abrir no draw.io" para editar o diagrama

## Exemplos

### Exemplo 1: Sistema de Biblioteca

Requisitos de entrada:
```
A biblioteca deve permitir emprestar livros. Cada pessoa só pode ter 2 livros emprestados ao mesmo tempo.
Livros têm título, autor e ISBN. Pessoas têm nome, endereço e número de identificação.
```

Este exemplo gerará um diagrama com classes como `Livro`, `Pessoa` e `Biblioteca` com seus atributos e relacionamentos.

### Exemplo 2: Sistema de E-commerce

Requisitos de entrada:
```
O sistema de e-commerce deve permitir que clientes façam pedidos de produtos.
Cada pedido contém um ou mais itens. Produtos têm nome, preço e categoria.
Clientes possuem nome, email e endereço de entrega.
```

## Estrutura do Projeto

```
req2dom/
├── backend/           # API e lógica de processamento
│   ├── requirements.txt
│   └── src/
│       ├── app.py     # Ponto de entrada da aplicação
│       ├── api/
│       │   └── routes.py  # Rotas da API
│       └── model/
│           ├── domain_generator.py   # Gerador de XML
│           ├── llm_processor.py      # Processamento via LLM local
│           ├── external_llm_processor.py  # Processamento via APIs externas (ChatGPT, Deepseek, Qwen, Gemini Pro)
│           ├── hybrid_processor.py   # Processamento híbrido NLP+LLM
│
└── frontend/          # Interface web Vue.js
    ├── index.html     # Página principal
    ├── package.json   # Dependências
    └── src/
        ├── main.js    # Ponto de entrada
        ├── App.vue    # Componente principal
        ├── components/
        │   ├── InputSection.vue  # Entrada de requisitos
        │   └── OutputSection.vue # Saída e visualização
        └── assets/
            └── css/
                └── style.css     # Estilos da aplicação
```

## Tecnologias Utilizadas

### Backend
- FastAPI: Framework web rápido para APIs
- Ollama: Interface para modelos LLM locais
- spaCy: Biblioteca de processamento de linguagem natural
- Llama 3.1 8B: Modelo de linguagem grande

### Frontend
- Vue.js: Framework JavaScript progressivo
- Vite: Ferramenta de build e desenvolvimento
- fetch API: Para comunicação com o backend
- embed.diagrams.net: Para visualização e edição de diagramas

## Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do repositório
2. Crie um branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit de suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Faça push para o branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.

## Contato

Para dúvidas ou sugestões, entre em contato com a equipe de desenvolvimento.

## Inicializando manualmente

### Backend

Para iniciar o backend manualmente:

1. Navegue até a pasta backend:
   ```bash
   cd backend
   ```

2. Ative o ambiente virtual. Importante: O ambiente virtual deve estar na pasta `backend/venv`:
   ```bash
   source venv/bin/activate  # No Linux/macOS
   # ou
   venv\Scripts\activate      # No Windows
   ```

3. Inicie o servidor FastAPI:
   ```bash
   python -m uvicorn src.app:app --reload --host 127.0.0.1 --port 8000
   ```
   
> ⚠️ **Importante**: O backend deve ser iniciado a partir da pasta `backend` para garantir que o arquivo `.env` seja carregado corretamente.

### Frontend

Para iniciar o frontend manualmente:

1. Acesse a pasta do frontend:
   ```bash
   cd frontend
   ```

2. Inicie o servidor de desenvolvimento:
   ```bash
   npm run serve
   ```

A interface estará disponível em http://localhost:3000
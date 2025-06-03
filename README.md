# req2dom - Requisitos para Classes de Domínio

Esta ferramenta converte requisitos textuais em diagramas de classes de domínio, gerando automaticamente XML para visualização em draw.io. Ela utiliza diferentes métodos de processamento de linguagem natural e modelos de linguagem grande (LLM) para identificar entidades, atributos e relacionamentos.

## Visão Geral

O req2dom é uma aplicação web que permite aos usuários:

- Inserir requisitos textuais em linguagem natural
- Processar estes requisitos utilizando diferentes métodos (LLM, NLP ou híbrido)
- Gerar diagramas de classe no formato draw.io
- Visualizar, editar e exportar os diagramas gerados

![Exemplo de fluxo](https://i.imgur.com/example.png)

## Arquitetura

O sistema está dividido em duas partes principais:

### Backend (Python/FastAPI)

- API REST para processamento de requisitos
- Integração com Ollama para acesso ao modelo Llama 3.1 8B
- Processamento de linguagem natural via spaCy
- Geração de XML para diagramas no formato draw.io

### Frontend (Vue.js)

- Interface de usuário responsiva
- Editor de texto para entrada de requisitos
- Visualização do XML gerado
- Integração direta com draw.io para visualização e edição dos diagramas

## Instalação e Execução

### Pré-requisitos

- Python 3.8+
- Node.js 16+
- Ollama com o modelo Llama 3.1 8B instalado
- [Opcional] Modelos spaCy para processamento NLP

### Backend

```bash
# Acessar pasta do backend
cd backend

# Instalar dependências
pip install -r requirements.txt

# Para suporte NLP (opcional, mas recomendado)
pip install spacy
python -m spacy download pt_core_news_lg  # Português
# OU
python -m spacy download en_core_web_lg   # Inglês

# Iniciar o servidor (porta 8000)
uvicorn src.app:app --reload
```

### Frontend

```bash
# Acessar pasta do frontend
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento (porta 3000)
npm run serve

# OU para compilar para produção
npm run build
```

## Métodos de Processamento

A ferramenta oferece três métodos para analisar e extrair classes de domínio a partir de requisitos textuais:

### 1. LLM (Modelo de Linguagem)

Usa exclusivamente o modelo Llama 3.1 8B para analisar os requisitos. Este método:
- Oferece a melhor compreensão semântica e contextual do texto
- Pode identificar entidades implícitas nos requisitos
- Requer mais recursos computacionais
- Ideal para requisitos complexos ou ambíguos

### 2. NLP (Processamento de Linguagem Natural)

Usa técnicas tradicionais de NLP (através do spaCy) para identificar entidades e relacionamentos. Este método:
- É mais rápido e usa menos recursos
- Baseia-se em análise gramatical e de dependências
- Pode ser menos preciso em textos ambíguos
- Funciona bem com requisitos claros e estruturados

### 3. Híbrido (NLP + LLM)

Combina as duas abordagens: usa NLP para identificação inicial das entidades e o LLM para refinamento. Este método:
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
│           ├── llm_processor.py      # Processamento via LLM
│           └── hybrid_processor.py   # Processamento híbrido NLP+LLM
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
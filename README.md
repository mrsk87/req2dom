# req2dom - Conversor de Requisitos para Classes de Domínio

Este projeto converte requisitos textuais em classes de domínio em formato XML, compatível com ferramentas como StarUML para geração de diagramas de classes.

## Estrutura do Projeto

```
.
├── backend/           # Servidor API em Python/FastAPI
│   ├── src/           # Código-fonte do backend
│   │   ├── api/       # Endpoints da API
│   │   └── model/     # Processamento de LLM e geração de XML
│   └── requirements.txt  # Dependências Python
└── frontend/          # Interface web em HTML/JS
    ├── index.html     # Página principal
    └── src/           # Assets do frontend
        ├── css/       # Estilos
        └── js/        # Scripts
```

## Requisitos

- Python 3.8+
- Ollama com o modelo llama3.1:8b instalado
- Navegador web moderno
- Conexão à Internet para download de dependências

## Instruções de Instalação

### 1. Configurar o ambiente virtual Python

```bash
# Clonar o repositório (se ainda não o fez)
git clone https://github.com/seunome/req2dom.git
cd req2dom

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

Em um terminal:

```bash
ollama run llama3.1:8b
```

### 2. Iniciar o servidor backend

Em outro terminal:

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

O servidor estará disponível em [http://localhost:8000].

### 3. Aceder à aplicação

Agora pode aceder à aplicação simplesmente abrindo o navegador e indo para [http://localhost:8000](http://localhost:8000).

## Utilização

1. Na interface do utilizador, introduza os requisitos do sistema na área de texto à esquerda.
2. Clique no botão "Processar".
3. Aguarde enquanto o sistema processa os requisitos (isto pode demorar alguns segundos).
4. O XML das classes de domínio gerado será exibido na área de texto à direita.
5. Pode copiar o XML para a área de transferência ou guardá-lo como ficheiro.
6. Importe o ficheiro XML para o StarUML ou outra ferramenta de modelagem compatível.

## Resolução de Problemas

### O processamento parece não funcionar

- Verifique se o modelo Ollama está em execução (`ollama run llama3.1:8b`)
- Verifique se o servidor backend está em execução (`uvicorn src.app:app --reload`)
- Verifique as mensagens de erro na consola do navegador (F12)
- Verifique os logs no terminal onde o backend está a correr

### Erros no XML gerado

- O XML pode não ser gerado corretamente se os requisitos forem muito complexos ou ambíguos
- Tente simplificar os requisitos e ser mais explícito na descrição das classes e atributos
- Verifique se o modelo LLM está a gerar JSON válido (veja os logs do backend)

## Licença

Este projeto está licenciado sob a licença MIT.
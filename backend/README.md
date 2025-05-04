# req2dom Backend

Sistema de conversão de requisitos para classes de domínio em formato XML.

## Descrição
Este backend processa requisitos escritos em linguagem natural e gera classes de domínio em formato XML,
compatível com ferramentas como StarUML.

## Características
- Processamento de linguagem natural usando LLM (Llama 3.1 8B)
- Geração de classes de domínio a partir de requisitos
- API REST para integração com frontend

## Instalação
```bash
pip install -r requirements.txt
```

## Utilização
```bash
cd backend
uvicorn src.app:app --reload
```
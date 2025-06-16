"""
Processador que utiliza o OpenRouter para acesso a múltiplos LLMs
"""
import logging
import time
import json
import os
import traceback
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger("openrouter_processor")

class OpenRouterProcessor:
    """
    Processador que utiliza a API do OpenRouter para extrair entidades de domínio
    """
    
    def __init__(self):
        """Inicializa o processador OpenRouter"""
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.default_model = "openai/gpt-3.5-turbo"
        logger.info("OpenRouterProcessor inicializado")
        
    def extract_domain_entities(self, requirements_text: str, api_key: str = None, model: str = None) -> Dict[str, Any]:
        """
        Extrai entidades de domínio usando a API do OpenRouter
        
        Args:
            requirements_text (str): Texto com os requisitos
            api_key (str): Chave da API (opcional, usa do .env se não fornecida)
            model (str): Modelo a usar (opcional, usa padrão se não fornecido)
            
        Returns:
            dict: Estrutura de dados com as entidades e seus relacionamentos
        """
        start_time = time.time()
        logger.info(f"Iniciando processamento OpenRouter de requisitos com {len(requirements_text)} caracteres")
        
        # Usar chave do ambiente se não fornecida
        if not api_key:
            api_key = os.getenv('OPENROUTER_API_KEY')
            logger.info("Usando chave de API do arquivo .env")
        else:
            logger.info("Usando chave de API fornecida na requisição")
        
        if not api_key:
            error_msg = "API Key do OpenRouter não configurada. Configure OPENROUTER_API_KEY no .env ou forneça via interface."
            logger.error(error_msg)
            return {"error": error_msg}
        
        # Usar modelo fornecido ou padrão
        selected_model = model if model else self.default_model
        logger.info(f"Usando modelo: {selected_model}")
        
        try:
            # Pré-processar requisitos que começam com RF[número]
            processed_text = self._preprocess_requirements(requirements_text)
            
            # Preparar o prompt para o OpenRouter
            prompt = f"""
Analise os seguintes requisitos e extraia as classes de domínio, seus atributos e relacionamentos.
Forneça apenas os dados estruturados em formato JSON com as classes, atributos e relacionamentos.

Requisitos:
{processed_text}

Formato de saída (use exatamente este formato, sem texto adicional):
{{
    "classes": [
        {{
            "nome": "Nome da Classe",
            "atributos": [
                {{"nome": "nomeAtributo", "tipo": "tipoAtributo"}}
            ],
            "relacionamentos": [
                {{"tipo": "associacao", "alvo": "ClasseAlvo", "cardinalidade": "1..n"}},
                {{"tipo": "composicao", "alvo": "ClasseAlvo", "cardinalidade": "1..1"}},
                {{"tipo": "heranca", "alvo": "ClasseAlvo", "cardinalidade": "1..1"}}
            ]
        }}
    ]
}}
"""
            
            # Preparar o pedido para a API do OpenRouter
            payload = {
                "model": selected_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "req2dom"
            }
            
            logger.info(f"Enviando pedido para OpenRouter: modelo={selected_model}")
            
            # Enviar pedido para a API do OpenRouter
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=60
            )
            
            logger.info(f"Resposta recebida do OpenRouter: status={response.status_code}, tempo={time.time()-start_time:.2f}s")
            
            if response.status_code != 200:
                error_msg = f"Erro na API OpenRouter: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
            
            # Processar resposta do OpenRouter
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                logger.info(f"Resposta do OpenRouter obtida com sucesso ({len(content)} caracteres)")
                
                # Extrair JSON da resposta
                return self._extract_json_from_response(content)
            else:
                error_msg = "Resposta do OpenRouter não contém o campo 'choices'"
                logger.error(error_msg)
                return {"error": error_msg}
        
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Erro de conexão com a API do OpenRouter: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg}
            
        except requests.exceptions.Timeout as e:
            error_msg = f"Timeout ao conectar com a API do OpenRouter: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg}
            
        except Exception as e:
            error_msg = f"Erro no processador OpenRouter: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg}
    
    def _preprocess_requirements(self, text: str) -> str:
        """Pré-processa requisitos que começam com RF[número]"""
        import re
        
        # Procurar padrões no formato "RFxx. Texto do requisito"
        pattern = r"RF\d+\.\s*(.*?)(?=RF\d+\.|$)"
        matches = re.findall(pattern, text, re.DOTALL)
        
        # Se encontrou padrões RF, reformatar
        if matches:
            processed_text = ""
            rf_numbers = re.findall(r"RF(\d+)", text)
            
            for i, (req_text, rf_num) in enumerate(zip(matches, rf_numbers)):
                processed_text += f"Requisito #{rf_num}: {req_text.strip()}\n\n"
            
            return processed_text.strip()
        
        # Se não encontrou padrões RF, retornar o texto original
        return text
    
    def _extract_json_from_response(self, content: str) -> Dict[str, Any]:
        """Extrai JSON válido da resposta do LLM"""
        try:
            # Tentar encontrar JSON na resposta
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                # Verificar se é um JSON válido
                parsed_json = json.loads(json_str)
                logger.info("JSON válido extraído da resposta")
                return {"content": json_str}
            else:
                error_msg = "Não foi possível encontrar JSON válido na resposta"
                logger.error(error_msg)
                return {"error": error_msg}
        except Exception as e:
            error_msg = f"Erro ao extrair JSON da resposta: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

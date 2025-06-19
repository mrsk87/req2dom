"""
Processador que utiliza LLMs externos (OpenAI, Deepseek, Qwen) para extrair classes de domínio
"""
import logging
import time
import json
import traceback
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger("external_llm_processor")

class ExternalLLMProcessor:
    """
    Processador que utiliza APIs de LLMs externos para extrair entidades de domínio
    """
    
    def __init__(self):
        """Inicializa o processador de LLMs externos"""
        # Configurações API OpenAI (ChatGPT)
        self.openai_api_url = "https://api.openai.com/v1/chat/completions"
        self.openai_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        
        # Configurações API Deepseek
        self.deepseek_api_url = "https://api.deepseek.com/v1/chat/completions"
        self.deepseek_models = ["deepseek-chat", "deepseek-coder"]
        
        # Configurações API Qwen
        self.qwen_api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        self.qwen_models = ["qwen-max", "qwen-plus", "qwen-turbo"]
        
        # Configurações padrão
        self.api_key = None
        self.provider = "openai"  # Padrão: OpenAI/ChatGPT
        self.model = "gpt-3.5-turbo"  # Modelo padrão
        
        logger.info("ExternalLLMProcessor inicializado")
        
    def extract_domain_entities(self, requirements_text: str) -> Dict[str, Any]:
        """
        Extrai entidades de domínio usando a API do LLM externo selecionado
        
        Args:
            requirements_text (str): Texto com os requisitos
            
        Returns:
            dict: Estrutura de dados com as entidades e seus relacionamentos
        """
        start_time = time.time()
        logger.info(f"A iniciar processamento com {self.provider}/{self.model}, requisitos com {len(requirements_text)} caracteres")
        
        if not self.api_key:
            error_msg = f"Chave de API não configurada. Configure a chave antes de utilizar este método."
            logger.error(error_msg)
            return {"error": error_msg}
        
        # Pré-processamento dos requisitos para extrair códigos RF
        processed_reqs = self._preprocess_requirements(requirements_text)
        
        # Chamar o método correspondente ao provedor selecionado
        if self.provider == "openai":
            return self._process_with_openai(processed_reqs)
        elif self.provider == "deepseek":
            return self._process_with_deepseek(processed_reqs)
        elif self.provider == "qwen":
            return self._process_with_qwen(processed_reqs)
        else:
            error_msg = f"Provedor {self.provider} não suportado."
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _preprocess_requirements(self, requirements_text: str) -> str:
        """
        Pré-processa requisitos para extrair códigos RF e formatá-los adequadamente
        
        Args:
            requirements_text (str): Texto com os requisitos
            
        Returns:
            str: Requisitos processados com códigos RF destacados
        """
        import re
        
        # Procurar padrões no formato "RFxx. Texto do requisito"
        pattern = r"RF\d+\.\s*(.*?)(?=RF\d+\.|$)"
        matches = re.findall(pattern, requirements_text, re.DOTALL)
        
        # Se encontrar padrões RF, formata o texto
        if matches:
            processed_text = ""
            rf_numbers = re.findall(r"RF(\d+)", requirements_text)
            
            for i, (req_text, rf_num) in enumerate(zip(matches, rf_numbers)):
                processed_text += f"Requisito #{rf_num}: {req_text.strip()}\n\n"
            
            return processed_text.strip()
        
        # Se não encontrar padrões RF, retorna o texto original
        return requirements_text
    
    def _process_with_openai(self, requirements_text: str) -> Dict[str, Any]:
        """
        Processa requisitos usando a API do OpenAI (ChatGPT)
        """
        try:
            # Preparar o prompt para o OpenAI
            prompt = f"""
            Analise os seguintes requisitos e extraia as classes de domínio, seus atributos e relacionamentos.
            Forneça apenas os dados estruturados em formato JSON com as classes, atributos e relacionamentos.
            
            Requisitos:
            {requirements_text}
            
            Formato de saída (use exatamente este formato, sem texto adicional):
            {{
                "classes": [
                    {{
                        "nome": "Nome da Classe",
                        "atributos": [
                            {{"nome": "nomeAtributo", "tipo": "tipoAtributo"}}
                        ],
                        "relacionamentos": [
                            {{"tipo": "associacao/composicao/heranca", "alvo": "ClasseAlvo", "cardinalidade": "1..n"}}
                        ]
                    }}
                ]
            }}
            """
            
            # Preparar o pedido para a API do OpenAI
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            logger.info(f"A enviar pedido para OpenAI: modelo={self.model}")
            
            # Enviar pedido para a API do OpenAI
            response = requests.post(
                self.openai_api_url,
                json=payload,
                headers=headers,
                timeout=45  # Timeout de 45 segundos para a API externa
            )
            
            logger.info(f"Resposta recebida do OpenAI: estado={response.status_code}, tempo={time.time()-start_time:.2f}s")
            
            if response.status_code != 200:
                error_msg = f"Erro na API OpenAI: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
            
            # Processar resposta do OpenAI
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                logger.info(f"Resposta do OpenAI obtida com sucesso ({len(content)} caracteres)")
                
                # Extrair JSON da resposta
                return self._extract_json_from_response(content)
            else:
                error_msg = "Resposta do OpenAI não contém o campo 'choices'"
                logger.error(error_msg)
                return {"error": error_msg}
        
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Erro de ligação com a API do OpenAI: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg}
            
        except requests.exceptions.Timeout as e:
            error_msg = f"Timeout na ligação com a API do OpenAI: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg}
            
        except Exception as e:
            error_msg = f"Erro no processamento com OpenAI: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg}
    
    def _process_with_deepseek(self, requirements_text: str) -> Dict[str, Any]:
        """
        Processa requisitos usando a API do Deepseek
        """
        try:
            # Preparar o prompt para o Deepseek
            prompt = f"""
            Analise os seguintes requisitos e extraia as classes de domínio, seus atributos e relacionamentos.
            Forneça apenas os dados estruturados em formato JSON com as classes, atributos e relacionamentos.
            
            Requisitos:
            {requirements_text}
            
            Formato de saída (use exatamente este formato, sem texto adicional):
            {{
                "classes": [
                    {{
                        "nome": "Nome da Classe",
                        "atributos": [
                            {{"nome": "nomeAtributo", "tipo": "tipoAtributo"}}
                        ],
                        "relacionamentos": [
                            {{"tipo": "associacao/composicao/heranca", "alvo": "ClasseAlvo", "cardinalidade": "1..n"}}
                        ]
                    }}
                ]
            }}
            """
            
            # Preparar o pedido para a API do Deepseek
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            logger.info(f"A enviar pedido para Deepseek: modelo={self.model}")
            
            # Enviar pedido para a API do Deepseek
            response = requests.post(
                self.deepseek_api_url,
                json=payload,
                headers=headers,
                timeout=45
            )
            
            logger.info(f"Resposta recebida do Deepseek: estado={response.status_code}")
            
            if response.status_code != 200:
                error_msg = f"Erro na API Deepseek: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
            
            # Processar resposta do Deepseek
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                logger.info(f"Resposta do Deepseek obtida com sucesso ({len(content)} caracteres)")
                
                # Extrair JSON da resposta
                return self._extract_json_from_response(content)
            else:
                error_msg = "Resposta do Deepseek não contém o campo 'choices'"
                logger.error(error_msg)
                return {"error": error_msg}
                
        except Exception as e:
            error_msg = f"Erro no processamento com Deepseek: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg}
    
    def _process_with_qwen(self, requirements_text: str) -> Dict[str, Any]:
        """
        Processa requisitos usando a API do Qwen (Alibaba Cloud)
        """
        try:
            # Preparar o prompt para o Qwen
            prompt = f"""
            Analise os seguintes requisitos e extraia as classes de domínio, seus atributos e relacionamentos.
            Forneça apenas os dados estruturados em formato JSON com as classes, atributos e relacionamentos.
            
            Requisitos:
            {requirements_text}
            
            Formato de saída (use exatamente este formato, sem texto adicional):
            {{
                "classes": [
                    {{
                        "nome": "Nome da Classe",
                        "atributos": [
                            {{"nome": "nomeAtributo", "tipo": "tipoAtributo"}}
                        ],
                        "relacionamentos": [
                            {{"tipo": "associacao/composicao/heranca", "alvo": "ClasseAlvo", "cardinalidade": "1..n"}}
                        ]
                    }}
                ]
            }}
            """
            
            # Preparar o pedido para a API do Qwen
            payload = {
                "model": self.model,
                "input": {
                    "messages": [{"role": "user", "content": prompt}]
                },
                "parameters": {
                    "temperature": 0.1
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            logger.info(f"A enviar pedido para Qwen: modelo={self.model}")
            
            # Enviar pedido para a API do Qwen
            response = requests.post(
                self.qwen_api_url,
                json=payload,
                headers=headers,
                timeout=45
            )
            
            logger.info(f"Resposta recebida do Qwen: estado={response.status_code}")
            
            if response.status_code != 200:
                error_msg = f"Erro na API Qwen: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
            
            # Processar resposta do Qwen (estrutura diferente)
            result = response.json()
            
            if "output" in result and "text" in result["output"]:
                content = result["output"]["text"]
                logger.info(f"Resposta do Qwen obtida com sucesso ({len(content)} caracteres)")
                
                # Extrair JSON da resposta
                return self._extract_json_from_response(content)
            else:
                error_msg = "Resposta do Qwen não contém os campos esperados"
                logger.error(error_msg)
                return {"error": error_msg}
                
        except Exception as e:
            error_msg = f"Erro no processamento com Qwen: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg}
    
    def _extract_json_from_response(self, content: str) -> Dict[str, Any]:
        """
        Extrai e valida JSON da resposta do LLM
        """
        try:
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

"""
Processador do modelo de linguagem Llama 3.1 8B para análise de requisitos
"""
import requests
import logging
import traceback
import json
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_processor")

class LlamaProcessor:
    """
    Processador para o modelo Llama via Ollama que extrai informações
    de requisitos para gerar classes de domínio
    """
    
    def __init__(self, model_name="llama3.1:8b"):
        """
        Inicializa o processador LLM
        
        Args:
            model_name (str, optional): Nome do modelo no Ollama
        """
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/generate"
        logger.info(f"LlamaProcessor inicializado com modelo={model_name}, api_url={self.api_url}")
    
    def extract_domain_entities(self, requirements_text):
        """
        Extrai entidades de domínio a partir dos requisitos fornecidos
        
        Args:
            requirements_text (str): Texto com os requisitos
            
        Returns:
            dict: Estrutura de dados com as entidades e seus relacionamentos
        """
        start_time = time.time()
        logger.info(f"Iniciando processamento de requisitos com {len(requirements_text)} caracteres")
        
        # Preparar o prompt para o modelo
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
        
        try:
            # Preparar o pedido para o Ollama
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1
            }
            
            logger.info(f"Enviando pedido para Ollama: modelo={self.model_name}")
            
            # Enviar pedido para a API do Ollama
            response = requests.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120  # Aumentar o timeout para 2 minutos
            )
            
            logger.info(f"Resposta recebida do Ollama: status={response.status_code}, tempo={time.time()-start_time:.2f}s")
            
            if response.status_code != 200:
                error_msg = f"Erro na API Ollama: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
            
            # Processar resposta do Ollama
            try:
                result = response.json()
                logger.info("Resposta do Ollama parseada com sucesso")
            except Exception as e:
                error_msg = f"Erro ao fazer parse da resposta JSON do Ollama: {str(e)}"
                logger.error(error_msg)
                return {"error": error_msg}
            
            if "response" in result:
                # O Ollama retorna o texto na propriedade response
                response_text = result["response"]
                logger.info(f"Resposta do Ollama obtida com sucesso ({len(response_text)} caracteres)")
                
                # Tentar verificar se a resposta contém JSON válido
                try:
                    # Tentar extrair apenas o JSON da resposta (pode ter texto antes ou depois)
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = response_text[json_start:json_end]
                        # Verificar se é um JSON válido
                        json.loads(json_str)
                        logger.info("Validação de JSON na resposta: OK")
                    else:
                        logger.warning("A resposta não parece conter JSON válido")
                except Exception as e:
                    logger.warning(f"A resposta pode não conter JSON válido: {str(e)}")
                
                return {"content": response_text}
            else:
                error_msg = "Formato de resposta da API Ollama inválido"
                logger.error(f"{error_msg}: {result}")
                return {"error": error_msg}
                
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Erro de conexão com o Ollama: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg}
        except requests.exceptions.Timeout as e:
            error_msg = f"Timeout na comunicação com o Ollama: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Erro ao comunicar com o Ollama: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg}
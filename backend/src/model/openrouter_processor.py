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
        self.default_model = "anthropic/claude-3-haiku"  # Modelo rápido e eficiente
        
        # Outros modelos recomendados:
        self.recommended_models = {
            "free": "meta-llama/llama-3.1-8b-instruct:free",
            "fast": "anthropic/claude-3-haiku",
            "powerful": "openai/gpt-4o-mini",
            "advanced": "anthropic/claude-3-sonnet",
            "coding": "microsoft/wizardlm-2-8x22b"
        }
        
        logger.info("OpenRouterProcessor inicializado")
    
    def set_model(self, model_key: str = None, custom_model: str = None):
        """
        Define o modelo a ser usado
        
        Args:
            model_key (str): Chave do modelo recomendado ('free', 'fast', 'powerful', etc.)
            custom_model (str): Nome personalizado do modelo
        """
        if custom_model:
            self.default_model = custom_model
            logger.info(f"Modelo personalizado definido: {custom_model}")
        elif model_key and model_key in self.recommended_models:
            self.default_model = self.recommended_models[model_key]
            logger.info(f"Modelo definido via chave '{model_key}': {self.default_model}")
        else:
            logger.warning(f"Chave de modelo '{model_key}' não reconhecida. Modelos disponíveis: {list(self.recommended_models.keys())}")
        
    def get_available_models(self):
        """Retorna os modelos recomendados disponíveis"""
        return self.recommended_models
        
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
Analise os seguintes requisitos funcionais de um sistema e extraia as classes de domínio, seus atributos e relacionamentos.

INSTRUÇÕES IMPORTANTES:
1. Cada requisito RF(número) é independente, mas pode referenciar entidades dos outros requisitos
2. Identifique entidades principais (substantivos) como classes do domínio
3. Para cada classe, identifique atributos relevantes baseados no contexto dos requisitos
4. Defina relacionamentos entre classes com cardinalidades precisas
5. Use tipos de dados apropriados (String, Integer, Double, Date, DateTime, Boolean, etc.)
6. Considere todos os papéis/atores mencionados como possíveis classes
7. Considere todas as ações e objetos como potenciais classes e atributos

TIPOS DE ENTIDADES A PROCURAR:
- Atores/Usuários (usuários do sistema, papéis específicos)
- Objetos/Entidades principais (entidades centrais do domínio)
- Conceitos de negócio (processos, eventos, documentos)

TIPOS DE ATRIBUTOS COMUNS:
- Identificação: id, codigo, numero
- Nomes e descrições: nome, titulo, descricao, observacoes
- Dados pessoais: email, telefone, endereco
- Datas e horários: dataInicio, dataFim, dataHora, prazo
- Valores: preco, custo, valor, quantidade
- Estados: status, ativo, disponivel
- Medidas: peso, altura, duracao

REQUISITOS A ANALISAR:
{processed_text}

FORMATO DE SAÍDA (JSON puro, sem markdown ou texto adicional):
{{
    "classes": [
        {{
            "nome": "NomeDaClasse",
            "atributos": [
                {{"nome": "id", "tipo": "Integer"}},
                {{"nome": "nome", "tipo": "String"}},
                {{"nome": "outroAtributo", "tipo": "String|Integer|Double|Date|DateTime|Boolean"}}
            ],
            "relacionamentos": [
                {{"tipo": "associacao", "alvo": "OutraClasse", "cardinalidade": "1..1|1..n|0..1|0..n"}},
                {{"tipo": "composicao", "alvo": "ClasseComposta", "cardinalidade": "1..n"}},
                {{"tipo": "agregacao", "alvo": "ClasseAgregada", "cardinalidade": "0..n"}}
            ]
        }}
    ]
}}"""
            
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

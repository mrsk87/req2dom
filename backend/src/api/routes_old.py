"""
Rotas da API para o serviço de conversão de requisitos para classes de domínio
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional, Literal
import logging
import json
import os

from ..model.llm_processor import LlamaProcessor
from ..model.hybrid_processor import HybridProcessor
from ..model.domain_generator import DomainGenerator
from ..model.external_llm_processor import ExternalLLMProcessor
from ..model.spacy_textacy_processor import SpacyTextacyProcessor

# Configurar logging
logger = logging.getLogger("api.routes")

# Inicializar o router FastAPI
router = APIRouter()

# Inicializar componentes
llm_processor = LlamaProcessor()
hybrid_processor = HybridProcessor()
domain_generator = DomainGenerator()
external_llm_processor = ExternalLLMProcessor()
spacy_textacy_processor = SpacyTextacyProcessor()


class ApiKeyStatus(BaseModel):
    """Modelo para o status das chaves de API"""
    openai: bool = False
    deepseek: bool = False
    qwen: bool = False
    gemini: bool = False


class RequirementsRequest(BaseModel):
    """Modelo para pedidos de processamento de requisitos"""
    text: str
    model_path: Optional[str] = None
    api_key: Optional[str] = None
    llm_provider: Optional[str] = "openai"
    processing_method: Literal["llm", "llm_chatgpt", "hybrid", "spacy_textacy"] = "llm"
    use_env_key: Optional[bool] = False
    
    # Configuração para desativar o aviso sobre namespace protegido
    model_config = ConfigDict(protected_namespaces=())


class DomainResponse(BaseModel):
    """Modelo para respostas com classes de domínio"""
    success: bool
    xml_content: Optional[str] = None
    error: Optional[str] = None


@router.get("/api-keys", response_model=ApiKeyStatus)
async def get_api_key_status() -> Dict[str, bool]:
    """
    Verifica quais chaves de API estão configuradas no ambiente
    
    Returns:
        Dict[str, bool]: Status de cada chave de API
    """
    return {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "deepseek": bool(os.getenv("DEEPSEEK_API_KEY")),
        "qwen": bool(os.getenv("QWEN_API_KEY")),
        "gemini": bool(os.getenv("GEMINI_API_KEY"))
    }


@router.post("/process", response_model=DomainResponse)
async def process_requirements(request: RequirementsRequest) -> Dict[str, Any]:
    """
    Processa os requisitos e gera classes de domínio em formato XML
    
    Args:
        request (RequirementsRequest): Pedido com texto dos requisitos
        
    Returns:
        Dict: Resposta com o conteúdo XML ou mensagem de erro
    """
    try:
        # Configurar o caminho do modelo se fornecido
        if request.model_path:
            llm_processor.model_path = request.model_path
            if hasattr(hybrid_processor, 'llm_processor'):
                hybrid_processor.llm_processor.model_path = request.model_path
        
        logger.info(f"Processando requisitos com método: {request.processing_method}")
        
        # Configurar API key para LLM externo
        # Se for solicitado para usar a chave do .env, não sobrescrever a api_key
        if request.processing_method == "llm_chatgpt":
            if request.use_env_key:
                # Usar a chave do ambiente para o provedor selecionado
                logger.info(f"Usando chave de API do arquivo .env para o provedor {request.llm_provider}")
                # api_key já será carregada do .env pela classe ExternalLLMProcessor
            elif request.api_key:
                # Usar a chave fornecida na requisição
                logger.info("Usando chave de API fornecida na requisição")
                external_llm_processor.api_key = request.api_key
            
        # Extrair entidades de domínio usando o método selecionado
        if request.processing_method == "hybrid":
            processor_result = hybrid_processor.extract_domain_entities(request.text)
        elif request.processing_method == "spacy_textacy":
            processor_result = spacy_textacy_processor.extract_domain_entities(request.text)
        elif request.processing_method == "llm_chatgpt":
            # Configurar o provedor LLM selecionado
            if request.llm_provider:
                external_llm_processor.provider = request.llm_provider
                
                # Usar o modelo padrão para cada provedor
                if request.llm_provider == "openai":
                    external_llm_processor.model = "gpt-3.5-turbo"
                elif request.llm_provider == "deepseek":
                    external_llm_processor.model = "deepseek-chat"
                elif request.llm_provider == "qwen":
                    external_llm_processor.model = "qwen-turbo"
                    
                logger.info(f"Usando provedor LLM externo: {request.llm_provider} com modelo {external_llm_processor.model}")
                
            processor_result = external_llm_processor.extract_domain_entities(request.text)
        else:  # llm é o default
            processor_result = llm_processor.extract_domain_entities(request.text)
        
        if "error" in processor_result:
            return {
                "success": False,
                "error": processor_result["error"]
            }
        
        # Gerar XML a partir das entidades extraídas
        xml_content = domain_generator.generate_xml(processor_result["content"])
        
        # Verificar se houve erro na geração do XML
        if xml_content.startswith("<Error>") or xml_content.startswith("<e>"):
            error_msg = xml_content
            error_msg = error_msg.replace("<Error>", "").replace("</Error>", "")
            error_msg = error_msg.replace("<e>", "").replace("</e>", "")
            return {
                "success": False,
                "error": error_msg
            }
        
        return {
            "success": True,
            "xml_content": xml_content
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar requisitos: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Erro ao processar requisitos: {str(e)}"
        }
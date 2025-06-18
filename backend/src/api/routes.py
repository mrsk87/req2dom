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
from ..model.openrouter_processor import OpenRouterProcessor
from ..model.spacy_textacy_processor import SpacyTextacyProcessor
from ..model.stanza_processor import StanzaProcessor

# Configurar logging
logger = logging.getLogger("api.routes")

# Inicializar o router FastAPI
router = APIRouter()

# Inicializar componentes
llm_processor = LlamaProcessor()
# Usar o Stanza como processador NLP padrão para português de Portugal
hybrid_processor = HybridProcessor(nlp_engine="stanza")
domain_generator = DomainGenerator()
openrouter_processor = OpenRouterProcessor()
spacy_textacy_processor = SpacyTextacyProcessor()
stanza_processor = StanzaProcessor()


class RequirementsRequest(BaseModel):
    """Modelo para pedidos de processamento de requisitos"""
    text: str
    model_path: Optional[str] = None
    api_key: Optional[str] = None
    openrouter_model: Optional[str] = None
    processing_method: Literal["llm", "llm_openrouter", "spacy_textacy", "stanza", "hybrid"] = "hybrid"
    use_env_key: Optional[bool] = True
    nlp_engine: Optional[str] = "stanza"
    
    # Configuração para desativar o aviso sobre namespace protegido
    model_config = ConfigDict(protected_namespaces=())


class DomainResponse(BaseModel):
    """Modelo para respostas com classes de domínio"""
    success: bool
    xml_content: Optional[str] = None
    error: Optional[str] = None


@router.get("/api-keys")
async def get_api_keys_status() -> Dict[str, bool]:
    """
    Retorna o status das chaves de API configuradas no ambiente
    
    Returns:
        Dict: Status das chaves de API disponíveis
    """
    return {
        "openrouter": bool(os.getenv("OPENROUTER_API_KEY"))
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
        if request.model_path:
            llm_processor.model_path = request.model_path
            if hasattr(hybrid_processor, 'llm_processor'):
                hybrid_processor.llm_processor.model_path = request.model_path
        
        logger.info(f"Processando requisitos com método: {request.processing_method}")
        
        # Extrair entidades de domínio usando o método selecionado
        if request.processing_method == "hybrid":
            # Se especificado, usar o motor NLP solicitado
            if hasattr(request, 'nlp_engine') and request.nlp_engine != hybrid_processor.nlp_advanced.__class__.__name__.lower().replace('processor', ''):
                # Reconstruir o processador híbrido com o motor correto
                if request.nlp_engine == "stanza":
                    hybrid_processor = HybridProcessor(nlp_engine="stanza")
                    logger.info("Reconfigurando para usar Stanza como motor NLP")
                else:
                    hybrid_processor = HybridProcessor(nlp_engine="spacy")
                    logger.info("Reconfigurando para usar spaCy como motor NLP")
            
            processor_result = hybrid_processor.extract_domain_entities(request.text)
        elif request.processing_method == "llm_openrouter":
            # Determinar qual chave usar
            api_key_to_use = None
            if not request.use_env_key and request.api_key:
                api_key_to_use = request.api_key
                logger.info("Usando chave de API fornecida na requisição")
            else:
                logger.info("Usando chave de API do arquivo .env")
            
            processor_result = openrouter_processor.extract_domain_entities(
                request.text, 
                api_key=api_key_to_use, 
                model=request.openrouter_model
            )
        elif request.processing_method == "spacy_textacy":
            processor_result = spacy_textacy_processor.extract_domain_entities(request.text)
        elif request.processing_method == "stanza":
            processor_result = stanza_processor.extract_domain_entities(request.text)
        else:  # "llm" (default)
            processor_result = llm_processor.extract_domain_entities(request.text)
        
        if "error" in processor_result:
            logger.error(f"Erro no processador: {processor_result['error']}")
            return {
                "success": False,
                "error": f"Erro ao processar requisitos: {processor_result['error']}"
            }
        
        # Gerar XML a partir das entidades extraídas
        xml_content = domain_generator.generate_xml(processor_result["content"])
        
        return {
            "success": True,
            "xml_content": xml_content
        }
        
    except Exception as e:
        logger.exception(f"Erro não tratado: {str(e)}")
        return {
            "success": False, 
            "error": f"Erro ao processar requisitos: {str(e)}"
        }

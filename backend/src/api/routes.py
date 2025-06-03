"""
Rotas da API para o serviço de conversão de requisitos para classes de domínio
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional, Literal
import logging
import json

from ..model.llm_processor import LlamaProcessor
from ..model.hybrid_processor import HybridProcessor
from ..model.domain_generator import DomainGenerator

# Configurar logging
logger = logging.getLogger("api.routes")

# Inicializar o router FastAPI
router = APIRouter()

# Inicializar componentes
llm_processor = LlamaProcessor()
hybrid_processor = HybridProcessor()
domain_generator = DomainGenerator()


class RequirementsRequest(BaseModel):
    """Modelo para pedidos de processamento de requisitos"""
    text: str
    model_path: Optional[str] = None
    processing_method: Literal["llm", "hybrid", "nlp"] = "llm"
    
    # Configuração para desativar o aviso sobre namespace protegido
    model_config = ConfigDict(protected_namespaces=())


class DomainResponse(BaseModel):
    """Modelo para respostas com classes de domínio"""
    success: bool
    xml_content: Optional[str] = None
    error: Optional[str] = None


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
        
        # Extrair entidades de domínio usando o método selecionado
        if request.processing_method == "hybrid":
            processor_result = hybrid_processor.extract_domain_entities(request.text)
        elif request.processing_method == "nlp":
            # No modo NLP puro, usamos apenas a parte de NLP do processador híbrido
            initial_structure = hybrid_processor._prepare_initial_structure(request.text)
            
            # Criar uma estrutura básica no formato esperado pelo gerador de domínio
            classes = []
            for class_name in initial_structure["candidate_classes"]:
                class_info = {"nome": class_name, "atributos": [], "relacionamentos": []}
                
                # Adicionar relacionamentos identificados
                for rel in initial_structure["potential_relationships"]:
                    if rel["origem"] == class_name:
                        class_info["relacionamentos"].append({
                            "tipo": rel["tipo"],
                            "alvo": rel["alvo"],
                            "cardinalidade": rel["cardinalidade"]
                        })
                
                classes.append(class_info)
                
            json_content = {"classes": classes}
            processor_result = {"content": json.dumps(json_content)}
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
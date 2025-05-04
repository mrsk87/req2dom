"""
Rotas da API para o serviço de conversão de requisitos para classes de domínio
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional

from ..model.llm_processor import LlamaProcessor
from ..model.domain_generator import DomainGenerator

# Inicializar o router FastAPI
router = APIRouter()

# Inicializar componentes
llm_processor = LlamaProcessor()
domain_generator = DomainGenerator()


class RequirementsRequest(BaseModel):
    """Modelo para pedidos de processamento de requisitos"""
    text: str
    model_path: Optional[str] = None
    
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
        
        # Extrair entidades de domínio usando o LLM
        llm_result = llm_processor.extract_domain_entities(request.text)
        
        if "error" in llm_result:
            return {
                "success": False,
                "error": llm_result["error"]
            }
        
        # Gerar XML a partir das entidades extraídas
        xml_content = domain_generator.generate_xml(llm_result["content"])
        
        # Verificar se houve erro na geração do XML
        if xml_content.startswith("<Error>"):
            return {
                "success": False,
                "error": xml_content.replace("<Error>", "").replace("</Error>", "")
            }
        
        return {
            "success": True,
            "xml_content": xml_content
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao processar requisitos: {str(e)}"
        }
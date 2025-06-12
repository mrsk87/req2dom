"""
Processador híbrido que combina técnicas de NLP com LLM para análise de requisitos
"""
import logging
import json
import traceback
import time
import re
from typing import Dict, List, Any, Union

# Importar o processador LLM para usar como parte do processamento híbrido
from .llm_processor import LlamaProcessor
from .spacy_textacy_processor import SpacyTextacyProcessor

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hybrid_processor")

class HybridProcessor:
    """
    Processador híbrido que combina técnicas de NLP com LLM para
    extrair informações de requisitos para gerar classes de domínio
    """
    
    def __init__(self, model_name="llama3.1:8b"):
        """
        Inicializa o processador híbrido
        
        Args:
            model_name (str, optional): Nome do modelo LLM a utilizar como refinador
        """
        # Inicializar o processador LLM que será usado como refinador
        self.llm_processor = LlamaProcessor(model_name)
        self.nlp_advanced = SpacyTextacyProcessor()
        logger.info(f"HybridProcessor inicializado com LLM={model_name} e NLP avançado (spaCy+textacy)")
        
    def extract_domain_entities(self, requirements_text: str) -> Dict[str, Any]:
        """
        Extrai entidades de domínio combinando NLP e LLM
        
        Args:
            requirements_text (str): Texto com os requisitos
            
        Returns:
            dict: Estrutura de dados com as entidades e seus relacionamentos
        """
        start_time = time.time()
        logger.info(f"Iniciando processamento híbrido de requisitos com {len(requirements_text)} caracteres")
        
        try:
            # Fase 1: Pré-processamento com NLP avançado (spaCy+textacy)
            nlp_result = self.nlp_advanced.extract_domain_entities(requirements_text)
            initial_structure = json.loads(nlp_result["content"]) if "content" in nlp_result else {}
            
            # Fase 2: Refinamento com LLM
            prompt = f"""
            Analise os seguintes requisitos e refine as classes de domínio, seus atributos e relacionamentos.
            
            Requisitos:
            {requirements_text}
            
            Baseado em análise preliminar, foram identificadas as seguintes classes:
            {json.dumps(initial_structure.get('classes', []), ensure_ascii=False, indent=2)}
            
            Refine esta análise e forneça os dados estruturados em formato JSON com as classes, atributos e relacionamentos.
            Você pode adicionar ou remover classes e atributos conforme necessário para uma modelagem correta.
            
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
            result = self.llm_processor.extract_domain_entities(prompt)
            
            logger.info(f"Processamento híbrido concluído em {time.time()-start_time:.2f}s")
            
            return {"content": result.get("content", "{}")}
            
        except Exception as e:
            error_msg = f"Erro no processamento híbrido: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg}
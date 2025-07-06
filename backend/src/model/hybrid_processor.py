"""
Processador híbrido que combina Stanza (NLP) com Llama (LLM) para análise de requisitos
"""
import logging
import json
import traceback
import time
from typing import Dict, List, Any

# Importar processadores específicos: Llama (LLM) e Stanza (NLP)
from .llm_processor import LlamaProcessor
from .stanza_processor import StanzaProcessor

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hybrid_processor")

class HybridProcessor:
    """
    Processador híbrido que combina Stanza (NLP) com Llama (LLM) para
    extrair informações de requisitos e gerar classes de domínio
    """
    
    def __init__(self, model_name="llama3.1:8b"):
        """
        Inicializa o processador híbrido com Stanza (NLP) + Llama (LLM)
        
        Args:
            model_name (str, optional): Nome do modelo Llama a utilizar
        """
        # Inicializar processador Llama local
        self.llm_processor = LlamaProcessor(model_name)
        
        # Usar Stanza como processador NLP especializado em português de Portugal
        self.nlp_processor = StanzaProcessor()
        
        logger.info(f"HybridProcessor inicializado com Stanza (NLP) + Llama ({model_name}) para português de Portugal")
        
    def extract_domain_entities(self, requirements_text: str) -> Dict[str, Any]:
        """
        Extrai entidades de domínio combinando Stanza (NLP) e Llama (LLM)
        
        Args:
            requirements_text (str): Texto com os requisitos
            
        Returns:
            dict: Estrutura de dados com as entidades e seus relacionamentos
        """
        start_time = time.time()
        logger.info(f"Iniciando processamento híbrido Stanza+Llama de requisitos com {len(requirements_text)} caracteres")
        
        try:
            # Fase 1: Análise NLP com Stanza (português de Portugal)
            logger.info("Fase 1: Processamento com Stanza...")
            nlp_result = self.nlp_processor.extract_domain_entities(requirements_text)
            
            if "error" in nlp_result:
                logger.warning(f"Erro no processamento Stanza: {nlp_result['error']}")
                initial_structure = {"classes": []}
            else:
                initial_structure = json.loads(nlp_result["content"]) if "content" in nlp_result else {"classes": []}
            
            logger.info(f"Stanza identificou {len(initial_structure.get('classes', []))} classes iniciais")
            
            # Fase 2: Refinamento com Llama
            logger.info("Fase 2: Refinamento com Llama...")
            prompt = f"""
            Analise os seguintes requisitos funcionais em português e refine o modelo de domínio.
            
            Requisitos:
            {requirements_text}
            
            Análise preliminar com Stanza identificou:
            {json.dumps(initial_structure.get('classes', []), ensure_ascii=False, indent=2)}
            
            Como especialista em análise de sistemas, refine este modelo:
            1. Valide as classes identificadas
            2. Adicione classes em falta
            3. Melhore os atributos (tipos corretos, nomes apropriados)
            4. Identifique relacionamentos importantes
            5. Garanta que o modelo está completo para os requisitos dados
            
            Responda APENAS com JSON válido no formato:
            {{
                "classes": [
                    {{
                        "nome": "NomeClasse",
                        "atributos": [
                            {{"nome": "nomeAtributo", "tipo": "String|Integer|Date|Boolean|Double"}}
                        ],
                        "relacionamentos": [
                            {{"tipo": "association|composition|inheritance", "alvo": "OutraClasse", "cardinalidade": "1..1|1..*|*..*"}}
                        ]
                    }}
                ]
            }}
            """
            
            # Processar com Llama
            llm_result = self.llm_processor.extract_domain_entities(prompt)
            
            if "error" in llm_result:
                logger.warning(f"Erro no processamento Llama: {llm_result['error']}")
                # Se Llama falhar, usar apenas resultado do Stanza
                final_result = initial_structure
            else:
                # Combinar resultados de Stanza e Llama
                llm_structure = json.loads(llm_result["content"]) if "content" in llm_result else {"classes": []}
                final_result = self._merge_results(initial_structure, llm_structure)
            
            # Fase 3: Validação e limpeza final
            final_result = self._validate_and_clean_result(final_result)
            
            processing_time = time.time() - start_time
            logger.info(f"Processamento híbrido concluído em {processing_time:.2f}s com {len(final_result.get('classes', []))} classes finais")
            
            return {"content": json.dumps(final_result, ensure_ascii=False, indent=2)}
            
        except Exception as e:
            error_msg = f"Erro no processamento híbrido Stanza+Llama: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg}
    
    def _merge_results(self, stanza_result: Dict, llama_result: Dict) -> Dict:
        """
        Combina inteligentemente os resultados do Stanza e Llama
        
        Args:
            stanza_result: Resultado do processamento Stanza
            llama_result: Resultado do processamento Llama
            
        Returns:
            dict: Resultado combinado otimizado
        """
        stanza_classes = stanza_result.get("classes", [])
        llama_classes = llama_result.get("classes", [])
        
        # Se um dos resultados estiver vazio, usar o outro
        if not stanza_classes:
            return llama_result
        if not llama_classes:
            return stanza_result
        
        # Combinar classes usando Llama como base (melhor compreensão contextual)
        # e Stanza para validação linguística
        merged_classes = []
        
        for llama_class in llama_classes:
            # Verificar se Stanza também identificou uma classe similar
            matching_stanza_class = self._find_matching_class(llama_class["nome"], stanza_classes)
            
            if matching_stanza_class:
                # Combinar atributos de ambas as fontes
                merged_class = self._merge_class_attributes(llama_class, matching_stanza_class)
                merged_classes.append(merged_class)
                logger.info(f"Classe '{llama_class['nome']}' validada por ambos processadores")
            else:
                # Usar classe identificada apenas pelo Llama
                merged_classes.append(llama_class)
                logger.info(f"Classe '{llama_class['nome']}' identificada apenas pelo Llama")
        
        # Adicionar classes identificadas apenas pelo Stanza (se houver)
        for stanza_class in stanza_classes:
            if not self._find_matching_class(stanza_class["nome"], merged_classes):
                merged_classes.append(stanza_class)
                logger.info(f"Classe '{stanza_class['nome']}' identificada apenas pelo Stanza")
        
        return {"classes": merged_classes}
    
    def _find_matching_class(self, class_name: str, class_list: List[Dict]) -> Dict:
        """Encontra uma classe correspondente numa lista"""
        class_name_lower = class_name.lower()
        for cls in class_list:
            if cls["nome"].lower() == class_name_lower:
                return cls
        return None
    
    def _merge_class_attributes(self, llama_class: Dict, stanza_class: Dict) -> Dict:
        """Combina atributos de uma classe de ambas as fontes"""
        merged_attributes = []
        seen_attributes = set()
        
        # Começar com atributos do Llama (melhor inferência de tipos)
        for attr in llama_class.get("atributos", []):
            attr_key = attr["nome"].lower()
            if attr_key not in seen_attributes:
                merged_attributes.append(attr)
                seen_attributes.add(attr_key)
        
        # Adicionar atributos únicos do Stanza
        for attr in stanza_class.get("atributos", []):
            attr_key = attr["nome"].lower()
            if attr_key not in seen_attributes:
                merged_attributes.append(attr)
                seen_attributes.add(attr_key)
        
        # Usar relacionamentos do Llama (melhor compreensão contextual)
        return {
            "nome": llama_class["nome"],
            "atributos": merged_attributes,
            "relacionamentos": llama_class.get("relacionamentos", [])
        }
    
    def _validate_and_clean_result(self, result: Dict) -> Dict:
        """Valida e limpa o resultado final"""
        classes = result.get("classes", [])
        
        # Garantir que todas as classes têm estrutura mínima
        validated_classes = []
        for cls in classes:
            if cls.get("nome") and len(cls["nome"]) > 1:
                # Garantir atributos básicos se não existirem
                if not cls.get("atributos"):
                    cls["atributos"] = [
                        {"nome": "id", "tipo": "Integer"},
                        {"nome": "nome", "tipo": "String"}
                    ]
                
                # Garantir estrutura de relacionamentos
                if "relacionamentos" not in cls:
                    cls["relacionamentos"] = []
                
                validated_classes.append(cls)
        
        return {"classes": validated_classes}

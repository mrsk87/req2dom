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

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hybrid_processor")

try:
    import spacy
    SPACY_AVAILABLE = True
    # Tenta carregar o modelo em português, mas se não estiver disponível, usa o modelo em inglês
    try:
        nlp = spacy.load("pt_core_news_lg")
        logger.info("Modelo spaCy em português carregado com sucesso")
    except:
        nlp = spacy.load("en_core_web_lg")
        logger.info("Modelo spaCy em inglês carregado como fallback")
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy não está instalado. O processador híbrido usará apenas técnicas básicas de NLP.")
    nlp = None

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
        logger.info(f"HybridProcessor inicializado com LLM={model_name}")
        
    def _extract_nouns_as_candidates(self, text: str) -> List[str]:
        """
        Extrai substantivos como candidatos a classes
        
        Args:
            text (str): Texto com os requisitos
            
        Returns:
            List[str]: Lista de substantivos candidatos a classes
        """
        if not SPACY_AVAILABLE:
            # Fallback simples se spaCy não estiver disponível
            words = re.findall(r'\b[A-Z][a-z]+\b', text)
            return list(set([w for w in words if len(w) > 2]))
        
        doc = nlp(text)
        # Extrair substantivos que não são stopwords e converter para forma base
        nouns = []
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop:
                # Converter para singular e capitalizar a primeira letra
                lemma = token.lemma_
                if lemma:
                    lemma = lemma[0].upper() + lemma[1:] if lemma else ""
                    nouns.append(lemma)
        
        # Remover duplicatas
        return list(set(nouns))
    
    def _extract_relationships(self, text: str, candidate_classes: List[str]) -> List[Dict[str, str]]:
        """
        Extrai relacionamentos entre classes candidatas
        
        Args:
            text (str): Texto dos requisitos
            candidate_classes (List[str]): Lista de classes candidatas
            
        Returns:
            List[Dict]: Lista de relacionamentos identificados
        """
        if not SPACY_AVAILABLE:
            return []  # Sem spaCy, não conseguimos fazer análise de dependências
            
        relationships = []
        doc = nlp(text)
        
        # Procurar por padrões de frases que indicam relacionamentos
        for sent in doc.sents:
            for class1 in candidate_classes:
                for class2 in candidate_classes:
                    if class1 != class2 and class1.lower() in sent.text.lower() and class2.lower() in sent.text.lower():
                        # Se ambas as classes aparecem na mesma frase, há potencial relacionamento
                        
                        # Verificar se há verbos que indicam relacionamentos específicos
                        association_verbs = ["tem", "possui", "contém", "pertence", "associa", "relaciona"]
                        composition_verbs = ["compõe", "forma", "constitui", "inclui"]
                        inheritance_verbs = ["é um", "é uma", "herda", "estende", "especializa"]
                        
                        rel_type = "associacao"  # Tipo padrão
                        
                        # Verificar se a frase contém verbos indicativos de tipos específicos
                        sent_lower = sent.text.lower()
                        
                        if any(verb in sent_lower for verb in inheritance_verbs):
                            rel_type = "heranca"
                        elif any(verb in sent_lower for verb in composition_verbs):
                            rel_type = "composicao"
                            
                        # Verificar por números que podem indicar cardinalidade
                        cardinality = "0..n"  # Padrão
                        cardinals = re.findall(r'\b(\d+|muitos|vários|todos|alguns|único|um|uma)\b', sent_lower)
                        if cardinals:
                            cardinal = cardinals[0]
                            if cardinal in ["um", "uma", "único"]:
                                cardinality = "0..1"
                            elif cardinal.isdigit():
                                cardinality = f"0..{cardinal}"
                            
                        relationships.append({
                            "tipo": rel_type,
                            "origem": class1,
                            "alvo": class2,
                            "cardinalidade": cardinality
                        })
        
        return relationships
    
    def _prepare_initial_structure(self, text: str) -> Dict[str, Any]:
        """
        Prepara uma estrutura inicial baseada em técnicas de NLP
        
        Args:
            text (str): Texto dos requisitos
            
        Returns:
            Dict: Estrutura inicial com classes e relacionamentos candidatos
        """
        # Extrair candidatos a classes (substantivos)
        candidate_classes = self._extract_nouns_as_candidates(text)
        logger.info(f"Candidatos a classes identificados: {candidate_classes}")
        
        # Extrair potenciais relacionamentos
        relationships = self._extract_relationships(text, candidate_classes)
        logger.info(f"Relacionamentos potenciais identificados: {len(relationships)}")
        
        # Construir estrutura inicial
        initial_structure = {
            "candidate_classes": candidate_classes,
            "potential_relationships": relationships,
            "original_text": text
        }
        
        return initial_structure
        
    def _refine_with_llm(self, initial_structure: Dict[str, Any]) -> str:
        """
        Usa o LLM para refinar a estrutura inicial
        
        Args:
            initial_structure (Dict): Estrutura inicial com candidatos
            
        Returns:
            str: JSON com as classes e relacionamentos refinados
        """
        # Preparar o prompt para o LLM com as informações pré-processadas
        prompt = f"""
        Analise os seguintes requisitos e refine as classes de domínio, seus atributos e relacionamentos.
        
        Requisitos:
        {initial_structure['original_text']}
        
        Baseado em análise preliminar, foram identificados os seguintes candidatos a classes:
        {', '.join(initial_structure['candidate_classes'])}
        
        E os seguintes relacionamentos potenciais:
        {json.dumps(initial_structure['potential_relationships'], indent=2, ensure_ascii=False)}
        
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
        
        # Usar o LLM para refinar (aqui estamos modificando o comportamento para usar nosso prompt)
        result = self.llm_processor.extract_domain_entities(prompt)
        
        return result.get("content", "{}")
        
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
            # Fase 1: Pré-processamento com NLP
            initial_structure = self._prepare_initial_structure(requirements_text)
            
            # Fase 2: Refinamento com LLM
            refined_json = self._refine_with_llm(initial_structure)
            
            logger.info(f"Processamento híbrido concluído em {time.time()-start_time:.2f}s")
            
            return {"content": refined_json}
            
        except Exception as e:
            error_msg = f"Erro no processamento híbrido: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg}
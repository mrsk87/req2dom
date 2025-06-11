"""
Processador alternativo que utiliza uma framework NLP diferente (NLTK) para extrair classes de domínio
"""
import logging
import time
import json
import traceback
import re
from typing import Dict, Any, List, Tuple

logger = logging.getLogger("alt_nlp_processor")

class AlternativeNLPProcessor:
    """
    Processador que utiliza NLTK para extrair entidades de domínio
    """
    
    def __init__(self):
        """Inicializa o processador NLP alternativo"""
        self.nltk_available = False
        try:
            import nltk
            from nltk.tokenize import sent_tokenize, word_tokenize
            from nltk.tag import pos_tag
            from nltk.chunk import ne_chunk
            
            # Tentar fazer download dos recursos necessários do NLTK
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')
            try:
                nltk.data.find('taggers/averaged_perceptron_tagger')
            except LookupError:
                nltk.download('averaged_perceptron_tagger')
            try:
                nltk.data.find('chunkers/maxent_ne_chunker')
            except LookupError:
                nltk.download('maxent_ne_chunker')
            try:
                nltk.data.find('corpora/words')
            except LookupError:
                nltk.download('words')
            
            self.nltk_available = True
            self.nltk = nltk
            self.sent_tokenize = sent_tokenize
            self.word_tokenize = word_tokenize
            self.pos_tag = pos_tag
            self.ne_chunk = ne_chunk
            logger.info("AlternativeNLPProcessor inicializado com NLTK")
        except ImportError:
            logger.warning("NLTK não está instalado. Instale usando: pip install nltk")
    
    def extract_domain_entities(self, requirements_text: str) -> Dict[str, Any]:
        """
        Extrai entidades de domínio usando NLTK
        
        Args:
            requirements_text (str): Texto com os requisitos
            
        Returns:
            dict: Estrutura de dados com as entidades e seus relacionamentos
        """
        start_time = time.time()
        logger.info(f"A iniciar processamento NLTK de requisitos com {len(requirements_text)} caracteres")
        
        if not self.nltk_available:
            error_msg = "NLTK não está instalado. Instale usando: pip install nltk"
            logger.error(error_msg)
            return {"error": error_msg}
        
        try:
            # Análise por frases
            sentences = self.sent_tokenize(requirements_text)
            classes = []
            entity_attributes = {}
            relationships = []
            
            # Extrair entidades e atributos
            for sentence in sentences:
                # Tokenização e POS tagging
                tokens = self.word_tokenize(sentence)
                tagged = self.pos_tag(tokens)
                
                # Identificar substantivos que podem ser classes
                nouns = [word for word, pos in tagged if pos.startswith('N') and len(word) > 2]
                
                # Identificar entidades nomeadas
                named_entities = self._extract_entities(sentence)
                
                # Combinar substantivos e entidades nomeadas como candidatos a classes
                class_candidates = list(set(nouns + named_entities))
                
                # Para cada candidato, adicionar à lista de classes
                for candidate in class_candidates:
                    if candidate[0].isupper() or len(candidate) > 3:
                        normalized = candidate[0].upper() + candidate[1:] if candidate else ""
                        if normalized and normalized not in [c["nome"] for c in classes]:
                            classes.append({
                                "nome": normalized,
                                "atributos": [],
                                "relacionamentos": []
                            })
                            entity_attributes[normalized] = []
                
                # Extrair atributos potenciais
                self._extract_attributes(sentence, entity_attributes)
                
                # Extrair relacionamentos
                self._extract_relationships(sentence, [c["nome"] for c in classes], relationships)
            
            # Associar atributos às classes
            for class_info in classes:
                class_name = class_info["nome"]
                if class_name in entity_attributes:
                    class_info["atributos"] = entity_attributes[class_name]
            
            # Associar relacionamentos às classes
            for rel in relationships:
                for class_info in classes:
                    if class_info["nome"] == rel["origem"]:
                        class_info["relacionamentos"].append({
                            "tipo": rel["tipo"],
                            "alvo": rel["alvo"],
                            "cardinalidade": rel["cardinalidade"]
                        })
            
            # Converter para formato JSON
            result = {"classes": classes}
            json_result = json.dumps(result, ensure_ascii=False)
            
            logger.info(f"Processamento NLTK concluído em {time.time()-start_time:.2f}s. Extraídas {len(classes)} classes.")
            return {"content": json_result}
            
        except Exception as e:
            error_msg = f"Erro no processador NLTK: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg}

    def _extract_entities(self, sentence: str) -> List[str]:
        """Extrai entidades nomeadas da frase"""
        try:
            tokens = self.word_tokenize(sentence)
            tagged = self.pos_tag(tokens)
            chunks = self.ne_chunk(tagged)
            
            entities = []
            for chunk in chunks:
                if hasattr(chunk, 'label'):
                    entities.append(' '.join([c[0] for c in chunk]))
            
            return entities
        except Exception as e:
            logger.warning(f"Erro ao extrair entidades: {str(e)}")
            return []
    
    def _extract_attributes(self, sentence: str, entity_attributes: Dict[str, List[Dict[str, str]]]) -> None:
        """Extrai atributos potenciais e os associa às entidades"""
        try:
            tokens = self.word_tokenize(sentence.lower())
            tagged = self.pos_tag(tokens)
            
            # Padrões comuns para atributos
            has_patterns = [r'tem', r'possui', r'contém', r'inclui', r'com']
            
            # Procurar padrões de atributos
            for entity in entity_attributes.keys():
                entity_lower = entity.lower()
                if entity_lower in ' '.join(tokens).lower():
                    # A entidade está nesta frase, procurar por atributos
                    for pattern in has_patterns:
                        match = re.search(f"{entity_lower}.*{pattern}(.*)", sentence.lower())
                        if match:
                            attr_text = match.group(1)
                            # Quebrar atributos por "e" ou ","
                            attrs = re.split(r',\s*|\s+e\s+', attr_text)
                            
                            for attr in attrs:
                                # Limpar e extrair nome do atributo
                                attr = attr.strip(' .,;:()')
                                if attr and len(attr) > 1:
                                    # Inferir tipo de atributo
                                    attr_type = self._infer_attribute_type(attr, tagged)
                                    
                                    # Adicionar atributo
                                    if attr:
                                        entity_attributes[entity].append({
                                            "nome": attr,
                                            "tipo": attr_type
                                        })
        except Exception as e:
            logger.warning(f"Erro ao extrair atributos: {str(e)}")
    
    def _infer_attribute_type(self, attr_name: str, tagged: List[Tuple[str, str]]) -> str:
        """Infere o tipo de um atributo com base em padrões comuns"""
        attr_lower = attr_name.lower()
        
        # Padrões para tipos
        date_patterns = ['data', 'dt_', 'dia', 'mes', 'ano', 'data_']
        number_patterns = ['quantidade', 'numero', 'valor', 'num_', 'qtd_', 'preco', 'idade']
        boolean_patterns = ['ativo', 'estado', 'disponivel', 'concluido', 'is_', 'has_']
        
        for pattern in date_patterns:
            if pattern in attr_lower:
                return "date"
        
        for pattern in number_patterns:
            if pattern in attr_lower:
                return "int" if 'idade' in attr_lower or 'quantidade' in attr_lower else "float"
        
        for pattern in boolean_patterns:
            if pattern in attr_lower:
                return "boolean"
        
        # Padrão default
        return "string"
    
    def _extract_relationships(self, sentence: str, class_names: List[str], relationships: List[Dict[str, str]]) -> None:
        """Extrai relacionamentos entre classes"""
        try:
            sentence_lower = sentence.lower()
            
            # Relações potenciais entre classes
            for i, class1 in enumerate(class_names):
                for j, class2 in enumerate(class_names):
                    if i != j and class1.lower() in sentence_lower and class2.lower() in sentence_lower:
                        # Ambas as classes estão na mesma frase
                        
                        # Detectar tipo de relacionamento
                        rel_type = "associacao"  # default
                        
                        # Detectar composição
                        if re.search(f"{class1.lower()}.*composto.*{class2.lower()}", sentence_lower) or \
                           re.search(f"{class1.lower()}.*contém.*{class2.lower()}", sentence_lower) or \
                           re.search(f"{class1.lower()}.*possui.*{class2.lower()}", sentence_lower):
                            rel_type = "composicao"
                        
                        # Detectar herança
                        if re.search(f"{class1.lower()}.*é um.*{class2.lower()}", sentence_lower) or \
                           re.search(f"{class1.lower()}.*é uma.*{class2.lower()}", sentence_lower) or \
                           re.search(f"{class1.lower()}.*herda.*{class2.lower()}", sentence_lower) or \
                           re.search(f"{class2.lower()}.*tipo de.*{class1.lower()}", sentence_lower):
                            rel_type = "heranca"
                        
                        # Detectar cardinalidade
                        cardinalidade = "0..n"  # default
                        
                        if re.search(r"um e apenas um|exatamente um", sentence_lower):
                            cardinalidade = "1..1"
                        elif re.search(r"pelo menos um|um ou mais", sentence_lower):
                            cardinalidade = "1..n"
                        elif re.search(r"um ou zero|no máximo um", sentence_lower):
                            cardinalidade = "0..1"
                        elif re.search(r"muitos|vários", sentence_lower):
                            cardinalidade = "0..n"
                        
                        # Extrair número específico
                        num_match = re.search(r"(\d+)\s+" + class2.lower(), sentence_lower)
                        if num_match:
                            num = num_match.group(1)
                            cardinalidade = f"0..{num}"
                        
                        # Adicionar relacionamento se não for duplicado
                        new_rel = {
                            "origem": class1,
                            "tipo": rel_type,
                            "alvo": class2,
                            "cardinalidade": cardinalidade
                        }
                        
                        # Verificar se já existe um relacionamento similar
                        if not any(
                            r["origem"] == new_rel["origem"] and 
                            r["alvo"] == new_rel["alvo"] and 
                            r["tipo"] == new_rel["tipo"]
                            for r in relationships
                        ):
                            relationships.append(new_rel)
                            
        except Exception as e:
            logger.warning(f"Erro ao extrair relacionamentos: {str(e)}")

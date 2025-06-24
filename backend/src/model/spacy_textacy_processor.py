"""
Processador NLP avançado usando spaCy + textacy para extração de entidades, atributos e relacionamentos
"""
import logging
import spacy
import textacy.extract
import re
import json
from typing import Dict, Any, List

logger = logging.getLogger("spacy_textacy_processor")

class SpacyTextacyProcessor:
    def __init__(self, lang_model="pt_core_news_lg"):
        try:
            self.nlp = spacy.load(lang_model)
            logger.info(f"Modelo spaCy carregado: {lang_model}")
        except Exception:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("Modelo spaCy en_core_web_sm carregado como fallback")
            except Exception:
                self.nlp = spacy.load("en_core_web_lg")
                logger.info("Modelo spaCy en_core_web_lg carregado como fallback")

    def extract_domain_entities(self, requirements_text: str) -> Dict[str, Any]:
        """
        Extrai entidades de domínio usando spaCy e textacy de forma mais precisa e focada
        
        Args:
            requirements_text (str): Texto com os requisitos
            
        Returns:
            dict: Estrutura de dados com as entidades e seus relacionamentos
        """
        logger.info(f"Iniciando processamento NLP de {len(requirements_text)} caracteres")
        
        try:
            # Pré-processar requisitos RF
            processed_text = self._preprocess_requirements(requirements_text)
            doc = self.nlp(processed_text)
            
            # Dicionário de classes
            classes = {}
            
            # 1. Extrair entidades principais (substantivos importantes)
            main_entities = self._extract_main_entities(doc)
            logger.info(f"Entidades extraídas: {main_entities}")
            
            # 2. Para cada entidade, criar classe e extrair atributos
            for entity in main_entities:
                class_name = entity.capitalize()
                if class_name not in classes:
                    classes[class_name] = {
                        "nome": class_name,
                        "atributos": [],
                        "relacionamentos": []
                    }
                
                # Extrair atributos baseados no contexto da entidade
                attributes = self._extract_attributes_for_entity(entity, doc)
                classes[class_name]["atributos"].extend(attributes)
            
            # Garantir que todas as classes tenham pelo menos os atributos básicos
            for class_name in classes:
                if not classes[class_name]["atributos"]:
                    classes[class_name]["atributos"] = [
                        {"nome": "id", "tipo": "Integer"},
                        {"nome": "nome", "tipo": "String"},
                        {"nome": "descricao", "tipo": "String"}
                    ]
            
            # 3. Extrair relacionamentos apenas se houver mais de uma classe
            if len(classes) > 1:
                relationships = self._extract_relationships(doc, classes.keys())
                for rel in relationships:
                    source_class = rel["source"]
                    if source_class in classes:
                        classes[source_class]["relacionamentos"].append({
                            "tipo": rel["tipo"],
                            "alvo": rel["target"],
                            "cardinalidade": rel["cardinalidade"]
                        })
            
            # 4. Remover duplicatas e limpar dados
            for class_name in classes:
                # Remover atributos duplicados
                seen_attrs = set()
                unique_attrs = []
                for attr in classes[class_name]["atributos"]:
                    attr_key = (attr["nome"], attr["tipo"])
                    if attr_key not in seen_attrs:
                        seen_attrs.add(attr_key)
                        unique_attrs.append(attr)
                classes[class_name]["atributos"] = unique_attrs
                
                # Remover relacionamentos duplicados
                seen_rels = set()
                unique_rels = []
                for rel in classes[class_name]["relacionamentos"]:
                    rel_key = (rel["tipo"], rel["alvo"], rel["cardinalidade"])
                    if rel_key not in seen_rels:
                        seen_rels.add(rel_key)
                        unique_rels.append(rel)
                classes[class_name]["relacionamentos"] = unique_rels
            
            result = {"classes": list(classes.values())}
            logger.info(f"Processamento concluído: {len(classes)} classes extraídas")
            return {"content": json.dumps(result, ensure_ascii=False, indent=2)}
            
        except Exception as e:
            error_msg = f"Erro no processamento spaCy+textacy: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _preprocess_requirements(self, text: str) -> str:
        """Pré-processa requisitos que começam com RF[número]"""
        import re
        
        # Procurar padrões no formato "RFxx. Texto do requisito"
        pattern = r"RF\d+\.\s*(.*?)(?=RF\d+\.|$)"
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            processed_text = ""
            rf_numbers = re.findall(r"RF(\d+)", text)
            
            for i, (req_text, rf_num) in enumerate(zip(matches, rf_numbers)):
                processed_text += f"Requisito {rf_num}: {req_text.strip()}\n\n"
            
            return processed_text.strip()
        
        return text
    
    def _extract_main_entities(self, doc) -> List[str]:
        """Extrai entidades principais usando múltiplas estratégias avançadas melhoradas"""
        entities = set()
        
        # 1. Entidades nomeadas pelo modelo spaCy (melhoradas)
        named_entities = self._extract_named_entities_improved(doc)
        entities.update(named_entities)
        
        # 2. Substantivos importantes baseados em análise estatística
        statistical_nouns = self._extract_statistical_important_nouns(doc)
        entities.update(statistical_nouns)
        
        # 3. Entidades extraídas por padrões semânticos melhorados
        semantic_entities = self._extract_semantic_entities_improved(doc)
        entities.update(semantic_entities)
        
        # 4. Análise contextual para identificar entidades de domínio usando TF-IDF
        domain_entities = self._extract_domain_entities_tfidf(doc)
        entities.update(domain_entities)
        
        # 5. Entidades baseadas em dependências sintáticas
        syntactic_entities = self._extract_syntactic_entities(doc)
        entities.update(syntactic_entities)
        
        # 6. Filtrar e normalizar com técnicas melhoradas
        filtered_entities = self._filter_and_normalize_entities_improved(entities, doc)
        
        logger.info(f"Entidades identificadas (melhoradas): {filtered_entities}")
        return filtered_entities[:5]  # Máximo 5 entidades principais

    def _extract_named_entities_improved(self, doc) -> set:
        """Extração melhorada de entidades nomeadas com filtros contextuais"""
        entities = set()
        
        for ent in doc.ents:
            # Focar em tipos de entidades relevantes para domínio de negócio
            if ent.label_ in ["PERSON", "ORG", "GPE", "EVENT", "PRODUCT", "WORK_OF_ART"]:
                entity_text = ent.text.strip().lower()
                
                # Filtrar entidades muito curtas ou genéricas
                if (len(entity_text) > 2 and 
                    not entity_text.isdigit() and
                    entity_text not in {'sistema', 'aplicação', 'processo', 'dados'}):
                    
                    # Verificar se a entidade está em contexto de negócio
                    if self._is_business_context(ent, doc):
                        entities.add(entity_text)
        
        return entities

    def _is_business_context(self, ent, doc) -> bool:
        """Verifica se uma entidade está em contexto de negócio/domínio"""
        business_keywords = {
            'gestão', 'gestao', 'gerir', 'administrar', 'controlar', 'processar',
            'cadastrar', 'registar', 'consultar', 'listar', 'criar', 'eliminar',
            'editar', 'atualizar', 'validar', 'aprovar', 'rejeitar', 'enviar',
            'receber', 'calcular', 'gerar', 'produzir', 'fornecer', 'servir'
        }
        
        # Verificar contexto numa janela de ±10 tokens
        start_idx = max(0, ent.start - 10)
        end_idx = min(len(doc), ent.end + 10)
        
        context_tokens = [token.text.lower() for token in doc[start_idx:end_idx]]
        
        return any(keyword in context_tokens for keyword in business_keywords)

    def _extract_statistical_important_nouns(self, doc) -> set:
        """Extrai substantivos importantes usando análise estatística avançada"""
        important_nouns = set()
        
        # Coletar estatísticas de substantivos
        noun_stats = {}
        for token in doc:
            if (token.pos_ == "NOUN" and 
                len(token.text) > 3 and 
                not token.is_stop and
                token.text.isalpha()):
                
                lemma = token.lemma_.lower()
                if lemma not in noun_stats:
                    noun_stats[lemma] = {
                        'frequency': 0,
                        'syntactic_roles': set(),
                        'modifiers': set(),
                        'collocations': set()
                    }
                
                noun_stats[lemma]['frequency'] += 1
                noun_stats[lemma]['syntactic_roles'].add(token.dep_)
                
                # Coletar modificadores (adjetivos, determinantes)
                for child in token.children:
                    if child.pos_ in ["ADJ", "DET"]:
                        noun_stats[lemma]['modifiers'].add(child.text.lower())
                
                # Coletar colocações (palavras próximas)
                for i in range(max(0, token.i-2), min(len(doc), token.i+3)):
                    if i != token.i and doc[i].pos_ in ["NOUN", "VERB", "ADJ"]:
                        noun_stats[lemma]['collocations'].add(doc[i].text.lower())
        
        # Calcular pontuação de importância
        for lemma, stats in noun_stats.items():
            importance_score = self._calculate_noun_importance(stats)
            
            # Threshold dinâmico baseado na distribuição
            if importance_score > 0.3:  # Ajustável
                important_nouns.add(lemma)
        
        return important_nouns

    def _calculate_noun_importance(self, stats: dict) -> float:
        """Calcula pontuação de importância de um substantivo"""
        score = 0.0
        
        # Frequência (peso: 0.3)
        freq_score = min(stats['frequency'] / 5.0, 1.0)  # Normalizado
        score += 0.3 * freq_score
        
        # Papéis sintáticos importantes (peso: 0.4)
        important_roles = {'nsubj', 'dobj', 'pobj', 'ROOT'}
        role_score = len(stats['syntactic_roles'].intersection(important_roles)) / len(important_roles)
        score += 0.4 * role_score
        
        # Diversidade de modificadores (peso: 0.2)
        modifier_score = min(len(stats['modifiers']) / 3.0, 1.0)
        score += 0.2 * modifier_score
        
        # Diversidade de colocações (peso: 0.1)
        collocation_score = min(len(stats['collocations']) / 5.0, 1.0)
        score += 0.1 * collocation_score
        
        return score

    def _extract_semantic_entities_improved(self, doc) -> set:
        """Extração melhorada de entidades usando padrões semânticos e sintáticos"""
        semantic_entities = set()
        
        # Padrões melhorados com contexto sintático
        enhanced_patterns = [
            # Padrões com análise sintática
            (r'\b(?:o|a|os|as|cada|um|uma)\s+(\w+)\s+(?:deve|pode|tem|possui|precisa|contém)', 1),
            (r'\b(?:gerenciar|gerir|cadastrar|registar|consultar|listar|criar|editar|eliminar)\s+(?:o|a|os|as)?\s*(\w+)', 1),
            (r'\b(?:dados|informações|detalhes|características|propriedades)\s+(?:do|da|de|dos|das)\s+(\w+)', 1),
            (r'\b(\w+)\s+(?:contém|inclui|possui|tem|apresenta)\s+', 1),
            # Padrões de domínio específico
            (r'\b(?:sistema|módulo|componente)\s+(?:de|para)\s+(\w+)', 1),
            (r'\b(?:interface|tela|página)\s+(?:de|para)\s+(\w+)', 1),
            (r'\b(?:relatório|listagem|consulta)\s+(?:de|dos|das)\s+(\w+)', 1)
        ]
        
        text = doc.text.lower()
        for pattern, group in enhanced_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if (len(match) > 3 and 
                    match not in ['sistema', 'dados', 'informação', 'processo'] and
                    self._is_domain_relevant(match, doc)):
                    semantic_entities.add(match)
        
        return semantic_entities

    def _is_domain_relevant(self, word: str, doc) -> bool:
        """Verifica se uma palavra é relevante para o domínio de negócio"""
        # Contar ocorrências no contexto de verbos de ação
        action_verbs = {
            'criar', 'registar', 'cadastrar', 'gerir', 'administrar', 'controlar',
            'processar', 'validar', 'aprovar', 'consultar', 'listar', 'editar',
            'eliminar', 'atualizar', 'calcular', 'gerar', 'enviar', 'receber'
        }
        
        word_contexts = 0
        total_occurrences = 0
        
        for sent in doc.sents:
            if word in sent.text.lower():
                total_occurrences += 1
                # Verificar se há verbos de ação na mesma frase
                sent_verbs = {token.lemma_.lower() for token in sent if token.pos_ == "VERB"}
                if sent_verbs.intersection(action_verbs):
                    word_contexts += 1
        
        # Se a palavra aparece pelo menos 50% das vezes em contexto de ação
        return total_occurrences > 0 and (word_contexts / total_occurrences) >= 0.5

    def _extract_domain_entities_tfidf(self, doc) -> set:
        """Extrai entidades usando análise TF-IDF simplificada"""
        domain_entities = set()
        
        # Coletar todos os substantivos
        nouns = []
        noun_positions = {}
        
        for token in doc:
            if (token.pos_ == "NOUN" and 
                len(token.text) > 3 and 
                not token.is_stop and
                token.text.isalpha()):
                
                lemma = token.lemma_.lower()
                nouns.append(lemma)
                
                if lemma not in noun_positions:
                    noun_positions[lemma] = []
                noun_positions[lemma].append(token.i)
        
        # Calcular TF (Term Frequency)
        tf_scores = {}
        total_nouns = len(nouns)
        
        for noun in set(nouns):
            tf = nouns.count(noun) / total_nouns
            tf_scores[noun] = tf
        
        # Calcular pontuação baseada em posição (substantivos no início têm maior peso)
        position_scores = {}
        doc_length = len(doc)
        
        for noun, positions in noun_positions.items():
            # Dar maior peso a substantivos que aparecem no início do documento
            avg_position = sum(positions) / len(positions)
            position_score = 1.0 - (avg_position / doc_length)
            position_scores[noun] = position_score
        
        # Combinar pontuações e selecionar top entidades
        combined_scores = {}
        for noun in tf_scores:
            combined_scores[noun] = tf_scores[noun] * 0.7 + position_scores.get(noun, 0) * 0.3
        
        # Selecionar entidades acima do threshold
        threshold = 0.05  # Ajustável
        for noun, score in combined_scores.items():
            if score > threshold:
                domain_entities.add(noun)
        
        return domain_entities

    def _extract_syntactic_entities(self, doc) -> set:
        """Extrai entidades baseadas em padrões sintáticos avançados"""
        syntactic_entities = set()
        
        # Analisar substantivos em posições sintáticas importantes
        for token in doc:
            if (token.pos_ == "NOUN" and 
                len(token.text) > 3 and 
                not token.is_stop):
                
                lemma = token.lemma_.lower()
                
                # Substantivos que são cabeça de sintagmas nominais
                if token.dep_ == "ROOT" or token.dep_ == "nsubj":
                    syntactic_entities.add(lemma)
                
                # Substantivos em construções possessivas
                elif token.dep_ == "poss" and token.head.pos_ == "NOUN":
                    syntactic_entities.add(lemma)
                
                # Substantivos modificados por adjetivos (indicam conceitos importantes)
                elif any(child.pos_ == "ADJ" for child in token.children):
                    syntactic_entities.add(lemma)
                
                # Substantivos em construções preposicionais importantes
                elif (token.dep_ == "pobj" and 
                      token.head.text.lower() in ["de", "para", "com", "em", "sobre"]):
                    syntactic_entities.add(lemma)
        
        return syntactic_entities

    def _filter_and_normalize_entities_improved(self, entities: set, doc) -> List[str]:
        """Filtra e normaliza entidades usando técnicas melhoradas"""
        # Palavras a excluir (expandida)
        exclude_words = {
            'sistema', 'aplicação', 'plataforma', 'dados', 'informação', 'processo',
            'forma', 'tipo', 'caso', 'parte', 'meio', 'modo', 'vez', 'tempo', 'lugar',
            'estado', 'coisa', 'exemplo', 'número', 'valor', 'nível', 'grupo', 'item',
            'versão', 'recurso', 'acesso', 'função', 'página', 'opção', 'erro', 'código',
            'requisito', 'analista', 'model', 'class', 'documento', 'texto', 'linha',
            'ficheiro', 'arquivo', 'pasta', 'diretório', 'formato', 'extensão'
        }
        
        # Processar e validar entidades
        processed_entities = []
        
        for entity in entities:
            entity_clean = entity.strip().lower()
            
            # Validações básicas
            if (len(entity_clean) <= 2 or 
                entity_clean in exclude_words or
                entity_clean.isdigit() or
                not entity_clean.isalpha()):
                continue
            
            # Normalizar para singular
            singular_form = self._normalize_to_singular(entity_clean)
            
            # Verificar se já existe forma similar
            if not any(self._are_similar_entities(singular_form, existing) 
                      for existing in processed_entities):
                
                # Calcular relevância final da entidade
                relevance_score = self._calculate_entity_relevance(singular_form, doc)
                
                if relevance_score > 0.4:  # Threshold de relevância
                    processed_entities.append(singular_form)
        
        # Ordenar por relevância e retornar top 5
        entity_scores = [(entity, self._calculate_entity_relevance(entity, doc)) 
                        for entity in processed_entities]
        entity_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [entity for entity, score in entity_scores[:5]]

    def _normalize_to_singular(self, word: str) -> str:
        """Normaliza palavra para singular usando heurísticas melhoradas"""
        # Regras de singularização para português
        if word.endswith('ões'):
            return word[:-3] + 'ão'
        elif word.endswith('ães'):
            return word[:-3] + 'ão'
        elif word.endswith('es') and len(word) > 4:
            # Verificar se não é uma palavra que termina naturalmente em 'es'
            if word not in {'pires', 'lápis', 'vírus', 'atlas'}:
                return word[:-2]
        elif word.endswith('s') and len(word) > 3:
            # Verificar se não é uma palavra que termina naturalmente em 's'
            if word not in {'lápis', 'vírus', 'pires', 'óculos'}:
                return word[:-1]
        
        return word

    def _are_similar_entities(self, entity1: str, entity2: str) -> bool:
        """Verifica se duas entidades são similares (para evitar duplicatas)"""
        # Verificação exata
        if entity1 == entity2:
            return True
        
        # Verificação de substring
        if entity1 in entity2 or entity2 in entity1:
            return True
        
        # Verificação de similaridade usando distância de Levenshtein simplificada
        if len(entity1) > 4 and len(entity2) > 4:
            # Se as 4 primeiras letras são iguais, considerar similar
            if entity1[:4] == entity2[:4]:
                return True
        
        return False

    def _calculate_entity_relevance(self, entity: str, doc) -> float:
        """Calcula pontuação de relevância de uma entidade no contexto"""
        score = 0.0
        entity_occurrences = 0
        
        # Contar ocorrências e contextos
        for token in doc:
            if token.text.lower() == entity or token.lemma_.lower() == entity:
                entity_occurrences += 1
                
                # Bonificar por papel sintático importante
                if token.dep_ in ['nsubj', 'dobj', 'ROOT']:
                    score += 0.2
                
                # Bonificar por contexto de ação
                parent_sent = token.sent
                action_verbs = {'criar', 'gerir', 'cadastrar', 'processar', 'validar'}
                if any(t.lemma_.lower() in action_verbs for t in parent_sent):
                    score += 0.3
                
                # Bonificar por modificadores
                if any(child.pos_ == "ADJ" for child in token.children):
                    score += 0.1
        
        # Bonificação por frequência (normalizada)
        if entity_occurrences > 0:
            freq_bonus = min(entity_occurrences / 5.0, 0.4)
            score += freq_bonus
        
        return min(score, 1.0)  # Máximo 1.0
    
    def _extract_relationships(self, doc, class_names) -> List[Dict[str, str]]:
        """Extrai relacionamentos avançados entre entidades usando múltiplas estratégias"""
        relationships = []
        class_names_list = list(class_names)
        
        if len(class_names_list) < 2:
            return relationships
        
        # 1. Relacionamentos explícitos baseados em análise sintática
        syntactic_rels = self._extract_syntactic_relationships(doc, class_names_list)
        relationships.extend(syntactic_rels)
        
        # 2. Relacionamentos semânticos baseados em padrões
        semantic_rels = self._extract_semantic_relationships(doc, class_names_list)
        relationships.extend(semantic_rels)
        
        # 3. Relacionamentos implícitos baseados no contexto
        implicit_rels = self._extract_implicit_relationships(doc, class_names_list)
        relationships.extend(implicit_rels)
        
        # 4. Remover duplicatas e limitar quantidade
        unique_relationships = self._deduplicate_relationships(relationships)
        
        return unique_relationships[:3]  # Máximo 3 relacionamentos para clareza
    
    def _extract_syntactic_relationships(self, doc, class_names: List[str]) -> List[Dict[str, str]]:
        """Extrai relacionamentos baseados em análise sintática"""
        relationships = []
        
        # Verbos que indicam relacionamentos específicos
        relationship_verbs = {
            'tem': ('association', '1..*'),
            'possui': ('association', '1..*'),
            'contém': ('composition', '1..*'),
            'inclui': ('composition', '1..*'),
            'usa': ('dependency', '1..1'),
            'utiliza': ('dependency', '1..1'),
            'gere': ('control', '1..*'),
            'controla': ('control', '1..*'),
            'administra': ('control', '1..*'),
            'pertence': ('association', '*.1'),
            'associa': ('association', '1..*')
        }
        
        for sent in doc.sents:
            # Encontrar classes na sentença
            classes_in_sentence = self._find_classes_in_sentence(sent, class_names)
            
            if len(classes_in_sentence) >= 2:
                for token in sent:
                    if token.pos_ == "VERB" and token.lemma_.lower() in relationship_verbs:
                        rel_type, cardinality = relationship_verbs[token.lemma_.lower()]
                        
                        # Encontrar sujeito e objeto
                        subject = self._find_subject_class(token, classes_in_sentence)
                        obj = self._find_object_class(token, classes_in_sentence)
                        
                        if subject and obj and subject != obj:
                            relationships.append({
                                "source": subject,
                                "target": obj,
                                "tipo": rel_type,
                                "cardinalidade": cardinality
                            })
        
        return relationships
    
    def _extract_semantic_relationships(self, doc, class_names: List[str]) -> List[Dict[str, str]]:
        """Extrai relacionamentos baseados em padrões semânticos"""
        relationships = []
        text_lower = doc.text.lower()
        
        # Padrões semânticos para relacionamentos
        patterns = [
            # "X de Y" - associação/pertencimento
            (r'\b(\w+)\s+de\s+(\w+)', 'association', '*.1'),
            # "X do Y" - associação/pertencimento  
            (r'\b(\w+)\s+do\s+(\w+)', 'association', '*.1'),
            # "X para Y" - dependência
            (r'\b(\w+)\s+para\s+(\w+)', 'dependency', '1..1'),
            # "X com Y" - associação
            (r'\b(\w+)\s+com\s+(\w+)', 'association', '1..*'),
            # "cada X tem Y" - composição
            (r'\bcada\s+(\w+)\s+tem\s+(\w+)', 'composition', '1..*'),
            # "vários X de Y" - associação múltipla
            (r'\bvários\s+(\w+)\s+de\s+(\w+)', 'association', '*..*')
        ]
        
        for pattern, rel_type, cardinality in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                source_word, target_word = match
                
                # Verificar se as palavras correspondem a classes
                source_class = self._find_matching_class(source_word, class_names)
                target_class = self._find_matching_class(target_word, class_names)
                
                if source_class and target_class and source_class != target_class:
                    relationships.append({
                        "source": source_class,
                        "target": target_class,
                        "tipo": rel_type,
                        "cardinalidade": cardinality
                    })
        
        return relationships
    
    def _extract_implicit_relationships(self, doc, class_names: List[str]) -> List[Dict[str, str]]:
        """Extrai relacionamentos implícitos baseados no contexto de domínio"""
        relationships = []
        
        # Regras de domínio para relacionamentos implícitos
        domain_rules = [
            # Pessoas tendem a usar/controlar sistemas ou objetos
            (['utilizador', 'cliente', 'funcionário', 'admin'], 
             ['sistema', 'produto', 'serviço', 'pedido'], 
             'control', '1..*'),
            
            # Entidades de transação relacionam-se com pessoas
            (['pedido', 'encomenda', 'reserva', 'consulta'], 
             ['utilizador', 'cliente'], 
             'association', '*.1'),
            
            # Entidades educacionais
            (['aluno', 'professor'], 
             ['disciplina', 'curso', 'aula'], 
             'association', '*..*'),
            
            # Produtos/serviços e categorias
            (['produto', 'serviço'], 
             ['categoria', 'tipo'], 
             'association', '*.1')
        ]
        
        class_names_lower = [name.lower() for name in class_names]
        
        for source_types, target_types, rel_type, cardinality in domain_rules:
            # Encontrar classes que correspondem aos tipos
            source_classes = [name for name in class_names 
                            if any(stype in name.lower() for stype in source_types)]
            target_classes = [name for name in class_names 
                            if any(ttype in name.lower() for ttype in target_types)]
            
            # Criar relacionamentos entre os grupos
            for source in source_classes:
                for target in target_classes:
                    if source != target:
                        relationships.append({
                            "source": source,
                            "target": target,
                            "tipo": rel_type,
                            "cardinalidade": cardinality
                        })
                        break  # Apenas um relacionamento por classe source
        
        return relationships
    
    def _find_classes_in_sentence(self, sentence, class_names: List[str]) -> List[str]:
        """Encontra classes mencionadas em uma sentença"""
        classes_found = []
        sentence_text = sentence.text.lower()
        
        for class_name in class_names:
            if class_name.lower() in sentence_text:
                classes_found.append(class_name)
        
        return classes_found
    
    def _find_subject_class(self, verb_token, classes_in_sentence: List[str]):
        """Encontra a classe que atua como sujeito de um verbo"""
        for child in verb_token.children:
            if child.dep_ == "nsubj":
                for class_name in classes_in_sentence:
                    if class_name.lower() in child.text.lower():
                        return class_name
        return None
    
    def _find_object_class(self, verb_token, classes_in_sentence: List[str]):
        """Encontra a classe que atua como objeto de um verbo"""
        for child in verb_token.children:
            if child.dep_ in ["dobj", "pobj", "iobj"]:
                for class_name in classes_in_sentence:
                    if class_name.lower() in child.text.lower():
                        return class_name
        return None
    
    def _find_matching_class(self, word: str, class_names: List[str]) -> str:
        """Encontra a classe que melhor corresponde a uma palavra"""
        word_lower = word.lower().strip()
        if not word_lower:
            return None
        
        # Normalizar texto para remoção de plurais
        if word_lower.endswith('s') and len(word_lower) > 3:
            word_singular = word_lower[:-1]
        else:
            word_singular = word_lower
        
        # 1. Correspondência exata (prioridade máxima)
        for class_name in class_names:
            if class_name.lower() == word_lower or class_name.lower() == word_singular:
                return class_name
        
        # 2. Correspondência por palavra completa (evita correspondências parciais)
        for class_name in class_names:
            class_lower = class_name.lower()
            if class_lower in word_lower.split() or word_lower in class_lower.split():
                return class_name
        
        # 3. Correspondência por raiz da palavra (apenas se for uma palavra única)
        if " " not in word_lower and len(word_lower) > 3:
            for class_name in class_names:
                # Verificar se é uma raiz comum (pelo menos 4 caracteres em comum)
                if len(word_lower) >= 4 and word_lower[:4] == class_name.lower()[:4]:
                    return class_name
        
        return None
    
    def _deduplicate_relationships(self, relationships: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Remove relacionamentos duplicados"""
        seen = set()
        unique_relationships = []
        
        for rel in relationships:
            # Criar uma chave única para o relacionamento
            key = (rel["source"], rel["target"], rel["tipo"])
            reverse_key = (rel["target"], rel["source"], rel["tipo"])
            
            # Evitar relacionamentos duplicados ou reversos
            if key not in seen and reverse_key not in seen:
                seen.add(key)
                unique_relationships.append(rel)
        
        return unique_relationships
    
    def _infer_cardinality(self, token, doc) -> str:
        """Simplificado: retorna 1..* para verbos como 'tem', 'possui', etc."""
        plural_verbs = {'tem', 'possui', 'contem', 'inclui', 'gerencia'}
        
        if token.lemma_.lower() in plural_verbs:
            return "1..*"
        
        # Padrão simplificado
        return "1.1"
    
    def _extract_attributes_for_entity(self, entity: str, doc) -> List[Dict[str, str]]:
        """Extrai atributos melhorados para uma entidade específica"""
        attributes = []
        entity_lower = entity.lower()
        
        # 1. Atributos básicos obrigatórios
        basic_attributes = [
            {"nome": "id", "tipo": "Integer"},
            {"nome": "nome", "tipo": "String"},
            {"nome": "descricao", "tipo": "String"}
        ]
        
        # 2. Atributos extraídos do contexto do documento
        contextual_attributes = self._extract_contextual_attributes(entity, doc)
        
        # 3. Atributos baseados no tipo de entidade
        type_based_attributes = self._get_type_based_attributes(entity_lower)
        
        # 4. Atributos extraídos por padrões linguísticos
        pattern_attributes = self._extract_attributes_by_patterns(entity, doc)
        
        # Combinar todos os atributos
        all_attributes = basic_attributes + contextual_attributes + type_based_attributes + pattern_attributes
        
        # Remover duplicatas mantendo a ordem
        seen = set()
        unique_attributes = []
        for attr in all_attributes:
            attr_key = (attr["nome"], attr["tipo"])
            if attr_key not in seen:
                seen.add(attr_key)
                unique_attributes.append(attr)
        
        return unique_attributes[:8]  # Máximo 8 atributos para manter simplicidade

    def _extract_contextual_attributes(self, entity: str, doc) -> List[Dict[str, str]]:
        """Extrai atributos baseados no contexto do documento"""
        attributes = []
        entity_lower = entity.lower()
        text_lower = doc.text.lower()
        
        # Padrões contextuais para identificar atributos
        attribute_patterns = [
            # "X tem/possui/contém Y"
            (rf'\b{entity_lower}\s+(?:tem|possui|contém|inclui|apresenta)\s+(\w+)', 'String'),
            # "Y do/da X" 
            (rf'\b(\w+)\s+(?:do|da|de)\s+{entity_lower}\b', 'String'),
            # "X com Y"
            (rf'\b{entity_lower}\s+com\s+(\w+)', 'String'),
            # "cadastrar/registar X com Y"
            (rf'\b(?:cadastrar|registar|criar)\s+{entity_lower}\s+com\s+(\w+)', 'String')
        ]
        
        for pattern, default_type in attribute_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match) > 2 and match not in ['dados', 'informação', 'detalhes']:
                    # Inferir tipo baseado no nome do atributo
                    attr_type = self._infer_attribute_type(match)
                    attributes.append({
                        "nome": match,
                        "tipo": attr_type
                    })
        
        return attributes

    def _infer_attribute_type(self, attr_name: str) -> str:
        """Infere o tipo de um atributo baseado no seu nome"""
        attr_lower = attr_name.lower()
        
        # Tipos específicos baseados em padrões
        if any(word in attr_lower for word in ['data', 'nascimento', 'criacao', 'modificacao', 'registo', 'vencimento']):
            return "Date"
        elif any(word in attr_lower for word in ['preco', 'valor', 'custo', 'salario', 'total', 'montante']):
            return "Double"
        elif any(word in attr_lower for word in ['quantidade', 'numero', 'idade', 'ano', 'creditos', 'id']):
            return "Integer"
        elif any(word in attr_lower for word in ['ativo', 'disponivel', 'valido', 'aprovado', 'publico']):
            return "Boolean"
        elif any(word in attr_lower for word in ['email', 'telefone', 'codigo', 'password', 'isbn']):
            return "String"
        else:
            return "String"  # Default

    def _get_type_based_attributes(self, entity_lower: str) -> List[Dict[str, str]]:
        """Retorna atributos baseados no tipo de entidade"""
        type_attributes = {
            # Pessoas
            'utilizador': [
                {"nome": "email", "tipo": "String"},
                {"nome": "password", "tipo": "String"},
                {"nome": "ativo", "tipo": "Boolean"},
                {"nome": "dataRegisto", "tipo": "Date"}
            ],
            'cliente': [
                {"nome": "email", "tipo": "String"},
                {"nome": "telefone", "tipo": "String"},
                {"nome": "morada", "tipo": "String"},
                {"nome": "ativo", "tipo": "Boolean"}
            ],
            'leitor': [
                {"nome": "numeroSocio", "tipo": "String"},
                {"nome": "contacto", "tipo": "String"},
                {"nome": "ativo", "tipo": "Boolean"},
                {"nome": "dataRegisto", "tipo": "Date"}
            ],
            
            # Produtos e Serviços
            'livro': [
                {"nome": "titulo", "tipo": "String"},
                {"nome": "autor", "tipo": "String"},
                {"nome": "isbn", "tipo": "String"},
                {"nome": "categoria", "tipo": "String"},
                {"nome": "disponivel", "tipo": "Boolean"}
            ],
            'produto': [
                {"nome": "codigo", "tipo": "String"},
                {"nome": "preco", "tipo": "Double"},
                {"nome": "categoria", "tipo": "String"},
                {"nome": "disponivel", "tipo": "Boolean"}
            ],
            
            # Transações
            'empréstimo': [
                {"nome": "dataEmprestimo", "tipo": "Date"},
                {"nome": "dataDevolucao", "tipo": "Date"},
                {"nome": "estado", "tipo": "String"},
                {"nome": "renovacoes", "tipo": "Integer"}
            ],
            'pedido': [
                {"nome": "data", "tipo": "Date"},
                {"nome": "estado", "tipo": "String"},
                {"nome": "total", "tipo": "Double"},
                {"nome": "observacoes", "tipo": "String"}
            ]
        }
        
        # Procurar correspondência exata ou parcial
        for key, attrs in type_attributes.items():
            if entity_lower == key or key in entity_lower or entity_lower in key:
                return attrs
        
        return []

    def _extract_attributes_by_patterns(self, entity: str, doc) -> List[Dict[str, str]]:
        """Extrai atributos usando padrões linguísticos avançados"""
        attributes = []
        entity_lower = entity.lower()
        
        # Procurar por adjetivos e complementos associados à entidade
        for token in doc:
            if token.text.lower() == entity_lower:
                # Procurar adjetivos próximos
                for child in token.children:
                    if child.pos_ == "ADJ" and len(child.text) > 3:
                        attr_name = child.text.lower()
                        if attr_name not in ['novo', 'antigo', 'bom', 'mau']:
                            attributes.append({
                                "nome": attr_name,
                                "tipo": "Boolean"
                            })
                
                # Procurar complementos nominais
                for child in token.children:
                    if child.dep_ in ["amod", "compound"] and child.pos_ == "NOUN":
                        attr_name = child.text.lower()
                        if len(attr_name) > 3:
                            attributes.append({
                                "nome": attr_name,
                                "tipo": self._infer_attribute_type(attr_name)
                            })
        
        return attributes

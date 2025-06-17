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
            self.nlp = spacy.load("en_core_web_lg")
            logger.info("Modelo spaCy em inglês carregado como fallback")

    def extract_domain_entities(self, requirements_text: str) -> Dict[str, Any]:
        """
        Extrai entidades de domínio usando spaCy e textacy
        
        Args:
            requirements_text (str): Texto com os requisitos
            
        Returns:
            dict: Estrutura de dados com as entidades e seus relacionamentos
        """
        logger.info(f"Iniciando processamento spaCy+textacy de {len(requirements_text)} caracteres")
        
        try:
            # Pré-processar requisitos RF
            processed_text = self._preprocess_requirements(requirements_text)
            doc = self.nlp(processed_text)
            
            # Dicionário de classes
            classes = {}
            
            # 1. Extrair entidades principais (substantivos importantes)
            main_entities = self._extract_main_entities(doc)
            
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
            
            # 3. Extrair relacionamentos usando análise sintática
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
        """Extrai entidades principais do texto"""
        entities = set()
        
        # Palavras-chave comuns em sistemas de negócio
        domain_keywords = {
            'cliente', 'usuario', 'pessoa', 'funcionario', 'admin', 'sistema', 
            'servico', 'produto', 'item', 'pedido', 'venda', 'compra',
            'agenda', 'marcacao', 'evento', 'tarefa', 'atividade', 'processo',
            'documento', 'relatorio', 'registro', 'categoria', 'tipo',
            'endereco', 'contato', 'telefone', 'email', 'dados',
            'pagamento', 'valor', 'preco', 'custo', 'quantidade',
            'data', 'hora', 'periodo', 'prazo', 'status', 'estado'
        }
        
        # Extrair substantivos relevantes
        for token in doc:
            if (token.pos_ in ["NOUN", "PROPN"] and 
                len(token.text) > 2 and 
                not token.is_stop and 
                not token.is_punct):
                
                lemma = token.lemma_.lower()
                # Priorizar palavras do domínio ou substantivos frequentes
                if lemma in domain_keywords or token.pos_ == "PROPN":
                    entities.add(lemma)
        
        # Extrair entidades nomeadas
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "PRODUCT"]:
                entities.add(ent.text.lower())
        
        return list(entities)
    
    def _extract_attributes_for_entity(self, entity: str, doc) -> List[Dict[str, str]]:
        """Extrai atributos para uma entidade específica de forma genérica"""
        attributes = []
        entity_lower = entity.lower()
        
        # Atributos básicos universais para qualquer entidade
        basic_attributes = [
            {"nome": "id", "tipo": "Integer"},
            {"nome": "nome", "tipo": "String"}
        ]
        
        # Atributos específicos baseados em padrões de nomenclatura
        if any(word in entity_lower for word in ['pessoa', 'cliente', 'usuario', 'utilizador', 'admin', 'secretaria', 'funcionario', 'veterinario']):
            # Entidades que representam pessoas
            attributes = [
                {"nome": "id", "tipo": "Integer"},
                {"nome": "nome", "tipo": "String"},
                {"nome": "email", "tipo": "String"},
                {"nome": "telefone", "tipo": "String"},
                {"nome": "endereco", "tipo": "String"}
            ]
        elif any(word in entity_lower for word in ['consulta', 'marcacao', 'agendamento', 'appointment']):
            # Entidades de agendamento/consulta
            attributes = [
                {"nome": "id", "tipo": "Integer"},
                {"nome": "dataHora", "tipo": "DateTime"},
                {"nome": "observacoes", "tipo": "String"},
                {"nome": "estado", "tipo": "String"}
            ]
        elif any(word in entity_lower for word in ['servico', 'service', 'produto', 'item']):
            # Entidades de serviço/produto
            attributes = [
                {"nome": "id", "tipo": "Integer"},
                {"nome": "nome", "tipo": "String"},
                {"nome": "descricao", "tipo": "String"},
                {"nome": "preco", "tipo": "Double"},
                {"nome": "tipo", "tipo": "String"}
            ]
        elif any(word in entity_lower for word in ['agenda', 'horario', 'schedule']):
            # Entidades de agenda/horário
            attributes = [
                {"nome": "id", "tipo": "Integer"},
                {"nome": "dataInicio", "tipo": "DateTime"},
                {"nome": "dataFim", "tipo": "DateTime"},
                {"nome": "disponivel", "tipo": "Boolean"}
            ]
        elif any(word in entity_lower for word in ['tipo', 'categoria', 'class']):
            # Entidades de classificação
            attributes = [
                {"nome": "id", "tipo": "Integer"},
                {"nome": "nome", "tipo": "String"},
                {"nome": "descricao", "tipo": "String"},
                {"nome": "ativo", "tipo": "Boolean"}
            ]
        else:
            # Entidades genéricas - tentar inferir do contexto
            context_attributes = self._infer_attributes_from_context(entity, doc)
            if context_attributes:
                attributes = basic_attributes + context_attributes
            else:
                attributes = basic_attributes + [{"nome": "descricao", "tipo": "String"}]
        
        return attributes
    
    def _infer_attributes_from_context(self, entity: str, doc) -> List[Dict[str, str]]:
        """Infere atributos baseado no contexto do texto"""
        attributes = []
        
        # Procurar por palavras-chave no contexto que indiquem atributos
        context_keywords = {
            'nome': 'String',
            'email': 'String', 
            'telefone': 'String',
            'endereco': 'String',
            'data': 'Date',
            'hora': 'Time',
            'preco': 'Double',
            'valor': 'Double',
            'quantidade': 'Integer',
            'numero': 'Integer',
            'codigo': 'String',
            'tipo': 'String',
            'categoria': 'String',
            'estado': 'String',
            'status': 'String',
            'descricao': 'String',
            'observacoes': 'String',
            'comentarios': 'String'
        }
        
        # Analisar o texto em busca de padrões
        for token in doc:
            if token.text.lower() in context_keywords:
                attr_name = token.text.lower()
                attr_type = context_keywords[attr_name]
                if {"nome": attr_name, "tipo": attr_type} not in attributes:
                    attributes.append({"nome": attr_name, "tipo": attr_type})
        
        return attributes
    
    def _extract_relationships(self, doc, entity_names) -> List[Dict[str, str]]:
        """Extrai relacionamentos entre entidades de forma genérica"""
        relationships = []
        entity_names_list = list(entity_names)
        
        # Analisar dependências sintáticas para encontrar relacionamentos
        for sent in doc.sents:
            for token in sent:
                # Procurar por padrões que indiquem relacionamentos
                if token.dep_ in ["nsubj", "dobj", "pobj"] and token.head.pos_ == "VERB":
                    # Encontrar entidades relacionadas através de verbos
                    subject_entities = []
                    object_entities = []
                    
                    # Procurar entidades na frase
                    for ent_name in entity_names_list:
                        if ent_name.lower() in sent.text.lower():
                            if token.dep_ == "nsubj":
                                subject_entities.append(ent_name.capitalize())
                            elif token.dep_ in ["dobj", "pobj"]:
                                object_entities.append(ent_name.capitalize())
                    
                    # Criar relacionamentos baseados nos padrões encontrados
                    for subj in subject_entities:
                        for obj in object_entities:
                            if subj != obj:
                                rel_type = self._determine_relationship_type(token.head.lemma_, subj, obj)
                                cardinalidade = self._determine_cardinality(sent.text, subj, obj)
                                
                                relationships.append({
                                    "source": subj,
                                    "target": obj,
                                    "tipo": rel_type,
                                    "cardinalidade": cardinalidade
                                })
        
        # Adicionar relacionamentos padrão baseados em nomes de entidades
        for i, entity1 in enumerate(entity_names_list):
            for entity2 in entity_names_list[i+1:]:
                if self._entities_likely_related(entity1, entity2):
                    rel_type, cardinalidade = self._get_default_relationship(entity1, entity2)
                    relationships.append({
                        "source": entity1.capitalize(),
                        "target": entity2.capitalize(),
                        "tipo": rel_type,
                        "cardinalidade": cardinalidade
                    })
        
        return relationships
    
    def _determine_relationship_type(self, verb: str, source: str, target: str) -> str:
        """Determina o tipo de relacionamento baseado no verbo"""
        verb_lower = verb.lower()
        
        if verb_lower in ['ter', 'possuir', 'conter', 'incluir', 'have', 'contain', 'include']:
            return "composicao"
        elif verb_lower in ['usar', 'utilizar', 'referenciar', 'associar', 'use', 'reference', 'associate']:
            return "associacao"
        elif verb_lower in ['herdar', 'estender', 'implementar', 'inherit', 'extend', 'implement']:
            return "heranca"
        else:
            return "associacao"  # padrão
    
    def _determine_cardinality(self, sentence: str, source: str, target: str) -> str:
        """Determina a cardinalidade baseada no contexto da frase"""
        sentence_lower = sentence.lower()
        
        if any(word in sentence_lower for word in ['varios', 'muitos', 'multiplos', 'many', 'multiple', 'several']):
            return "1..n"
        elif any(word in sentence_lower for word in ['um', 'uma', 'one', 'single']):
            return "1..1"
        elif any(word in sentence_lower for word in ['opcional', 'pode', 'optional', 'may', 'might']):
            return "0..1"
        else:
            return "1..n"  # padrão para flexibilidade
    
    def _entities_likely_related(self, entity1: str, entity2: str) -> bool:
        """Verifica se duas entidades provavelmente têm relacionamento"""
        # Entidades de pessoas geralmente se relacionam com outras entidades
        person_entities = ['admin', 'secretaria', 'cliente', 'usuario', 'funcionario', 'veterinario']
        
        entity1_lower = entity1.lower()
        entity2_lower = entity2.lower()
        
        # Se uma é pessoa e outra não, provavelmente há relacionamento
        entity1_is_person = any(word in entity1_lower for word in person_entities)
        entity2_is_person = any(word in entity2_lower for word in person_entities)
        
        return entity1_is_person != entity2_is_person
    
    def _get_default_relationship(self, entity1: str, entity2: str) -> tuple:
        """Retorna tipo de relacionamento e cardinalidade padrão"""
        person_entities = ['admin', 'secretaria', 'cliente', 'usuario', 'funcionario', 'veterinario']
        
        entity1_lower = entity1.lower()
        entity2_lower = entity2.lower()
        
        entity1_is_person = any(word in entity1_lower for word in person_entities)
        entity2_is_person = any(word in entity2_lower for word in person_entities)
        
        if entity1_is_person and not entity2_is_person:
            return "associacao", "1..n"
        elif not entity1_is_person and entity2_is_person:
            return "associacao", "1..n"
        else:
            return "associacao", "0..n"

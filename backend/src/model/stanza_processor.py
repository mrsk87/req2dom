"""
Processador NLP avançado usando Stanza para extração de entidades, atributos e relacionamentos
com foco em português de Portugal
"""
import logging
import stanza
import re
import json
import os
from typing import Dict, Any, List, Set

logger = logging.getLogger("stanza_processor")

class StanzaProcessor:
    def __init__(self, lang="pt"):
        """
        Inicializa o processador Stanza para português de Portugal
        Args:
            lang (str): Código do idioma ('pt' para Português)
        """
        try:
            # Verificar se o modelo já foi baixado
            if not os.path.exists(os.path.expanduser('~/stanza_resources/pt')):
                logger.info("Baixando modelo em português para Stanza...")
                stanza.download('pt', verbose=False)
                
            # Inicializar o pipeline para português sem NER (não disponível para PT)
            self.nlp = stanza.Pipeline(
                lang='pt',
                processors='tokenize,mwt,pos,lemma,depparse',
                use_gpu=False,  # Definir como True se tiver GPU disponível
                verbose=False
            )
            logger.info("Modelo Stanza para português carregado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo Stanza: {str(e)}")
            # Tentar usar inglês como fallback
            try:
                logger.info("Tentando carregar modelo em inglês como fallback...")
                stanza.download('en', verbose=False)
                self.nlp = stanza.Pipeline('en', processors='tokenize,pos,lemma,depparse')
                logger.warning("Modelo Stanza em inglês carregado como fallback")
            except Exception as e:
                logger.error(f"Não foi possível carregar nenhum modelo Stanza: {str(e)}")
                raise

    def extract_domain_entities(self, requirements_text: str) -> Dict[str, Any]:
        """
        Extrai entidades de domínio usando Stanza de forma precisa e focada
        
        Args:
            requirements_text (str): Texto com os requisitos
            
        Returns:
            dict: Estrutura de dados com as entidades e seus relacionamentos
        """
        logger.info(f"Iniciando processamento NLP com Stanza: {len(requirements_text)} caracteres")
        
        try:
            # Pré-processar requisitos RF
            processed_text = self._preprocess_requirements(requirements_text)
            doc = self.nlp(processed_text)
            
            # Dicionário de classes
            classes = {}
            
            # 1. Extrair entidades principais (substantivos importantes)
            main_entities = self._extract_main_entities(doc)
            logger.info(f"Entidades extraídas pelo Stanza: {main_entities}")
            
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
            logger.info(f"Processamento com Stanza concluído: {len(classes)} classes extraídas")
            return {"content": json.dumps(result, ensure_ascii=False, indent=2)}
            
        except Exception as e:
            error_msg = f"Erro no processamento Stanza: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def _preprocess_requirements(self, text: str) -> str:
        """Pré-processa requisitos que começam com RF[número]"""
        # Remover quebras de linha desnecessárias
        text = re.sub(r'\n+', '\n', text).strip()
        
        # Transformar requisitos no formato RF[número] em frases normais
        return re.sub(r'RF\d+[\s\-.:]+', '', text)

    def _extract_main_entities(self, doc) -> List[str]:
        """Extrai entidades principais que representam conceitos de domínio relevantes de forma mais abrangente"""
        entities = set()
        
        # Vocabulário expandido de entidades de domínio
        domain_entities = {
            # Atores/pessoas
            'utilizador', 'cliente', 'funcionario', 'admin', 'administrador', 'gestor', 
            'medico', 'paciente', 'professor', 'aluno', 'estudante', 'usuario', 'pessoa', 
            'empregado', 'operador', 'tecnico', 'diretor', 'gerente', 'enfermeiro', 'secretario',
            'analista', 'programador', 'desenvolvedor', 'tester', 'arquiteto',
            
            # Entidades de negócio
            'produto', 'servico', 'pedido', 'encomenda', 'conta', 'factura', 'venda',
            'consulta', 'aula', 'disciplina', 'curso', 'projeto', 'tarefa', 'atividade',
            'relatorio', 'documento', 'ficheiro', 'arquivo', 'imagem', 'video',
            'mensagem', 'email', 'notificacao', 'alerta', 'evento', 'reuniao',
            'categoria', 'tipo', 'grupo', 'equipa', 'departamento', 'secao',
            'requisito', 'especificacao', 'caso', 'teste', 'bug', 'defeito',
            'versao', 'release', 'build', 'deploy', 'configuracao', 'parametro',
            'log', 'historico', 'auditoria', 'backup', 'restauro',
            'permissao', 'papel', 'perfil', 'privilegio', 'acesso', 'seguranca',
            'base', 'tabela', 'campo', 'coluna', 'registo', 'entrada',
            'item', 'elemento', 'objeto', 'instancia', 'entidade'
        }
        
        # Análise de frequência e importância dos substantivos
        noun_analysis = {}
        for sentence in doc.sentences:
            for word in sentence.words:
                if word.upos in ["NOUN", "PROPN"] and len(word.text) > 2:
                    text_lower = word.text.lower()
                    lemma_lower = word.lemma.lower()
                    
                    # Scoring baseado em posição sintática e frequência
                    score = 1
                    if word.deprel in ["nsubj", "nsubj:pass"]:  # Sujeito
                        score += 3
                    elif word.deprel in ["obj", "iobj"]:  # Objeto
                        score += 2
                    elif word.deprel == "root":  # Raiz da frase
                        score += 2
                    
                    # Boost para entidades do vocabulário
                    if text_lower in domain_entities or lemma_lower in domain_entities:
                        score += 5
                    
                    key = lemma_lower if lemma_lower else text_lower
                    if key not in noun_analysis:
                        noun_analysis[key] = {'score': 0, 'count': 0, 'original': word.text}
                    noun_analysis[key]['score'] += score
                    noun_analysis[key]['count'] += 1

        # Filtrar palavras muito genéricas
        exclude_words = {
            'sistema', 'dados', 'informacao', 'processo', 'forma', 'modo', 'vez', 
            'tempo', 'lugar', 'coisa', 'exemplo', 'numero', 'valor', 'nivel',
            'parte', 'meio', 'erro', 'resultado', 'condicao'
        }
        
        # Selecionar as melhores entidades
        candidates = []
        for key, data in noun_analysis.items():
            if (len(key) >= 3 and 
                key not in exclude_words and
                not key.isdigit() and
                not key.isalpha() == False):  # Evitar tokens estranhos
                
                final_score = data['score'] * data['count']
                candidates.append((key, final_score, data['original']))
        
        # Ordenar por score e pegar as melhores
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Selecionar até 5 entidades principais
        for candidate, score, original in candidates[:5]:
            # Normalizar nome da entidade
            if candidate.endswith('s') and len(candidate) > 4:
                # Tentar forma singular
                singular = candidate[:-1]
                if singular in domain_entities:
                    entities.add(singular)
                else:
                    entities.add(candidate)
            else:
                entities.add(candidate)
        
        return list(entities)

    def _extract_attributes_for_entity(self, entity: str, doc) -> List[Dict[str, str]]:
        """Extrai atributos genéricos e relevantes para qualquer entidade"""
        attributes = []
        entity_lower = entity.lower()
        
        # Atributos básicos universais (sempre presentes)
        basic_attributes = [
            {"nome": "id", "tipo": "Integer"},
            {"nome": "nome", "tipo": "String"},
            {"nome": "descricao", "tipo": "String"}
        ]
        
        # Categorias simplificadas de entidades
        if self._is_person_entity(entity_lower):
            # Pessoas: utilizador, cliente, funcionario, etc.
            attributes = basic_attributes + [
                {"nome": "email", "tipo": "String"},
                {"nome": "telefone", "tipo": "String"},
                {"nome": "ativo", "tipo": "Boolean"}
            ]
        elif self._is_product_entity(entity_lower):
            # Produtos e serviços
            attributes = basic_attributes + [
                {"nome": "preco", "tipo": "Double"},
                {"nome": "disponivel", "tipo": "Boolean"},
                {"nome": "codigo", "tipo": "String"}
            ]
        elif entity_lower in ['pedido', 'encomenda', 'reserva', 'consulta', 'marcacao']:
            # Entidades de transação ou agendamento
            attributes = basic_attributes + [
                {"nome": "data", "tipo": "Date"},
                {"nome": "estado", "tipo": "String"},
                {"nome": "valor", "tipo": "Double"}
            ]
        elif entity_lower in ['aula', 'disciplina', 'curso', 'modulo', 'formacao']:
            # Entidades educacionais
            attributes = basic_attributes + [
                {"nome": "codigo", "tipo": "String"},
                {"nome": "creditos", "tipo": "Integer"},
                {"nome": "ativo", "tipo": "Boolean"}
            ]
        elif entity_lower in ['documento', 'relatorio', 'ficheiro', 'arquivo', 'imagem']:
            # Documentos e arquivos
            attributes = basic_attributes + [
                {"nome": "formato", "tipo": "String"},
                {"nome": "tamanho", "tipo": "Integer"},
                {"nome": "dataUpload", "tipo": "Date"}
            ]
        else:
            # Para todas as outras entidades, usar atributos genéricos
            attributes = basic_attributes + [
                {"nome": "estado", "tipo": "String"},
                {"nome": "dataCriacao", "tipo": "Date"}
            ]
            
            # Adicionar atributos específicos do contexto
            context_attributes = self._infer_attributes_from_context_simple(entity, doc)
            
            # Adicionar até 2 atributos contextuais sem duplicar
            for attr in context_attributes[:2]:
                if not any(a["nome"] == attr["nome"] for a in attributes):
                    attributes.append(attr)
        
        return attributes

    def _infer_attributes_from_context_simple(self, entity: str, doc) -> List[Dict[str, str]]:
        """Inferência simplificada de atributos baseada em palavras-chave próximas"""
        attributes = []
        
        # Palavras-chave contextuais diretas
        context_keywords = {
            'data': 'Date', 'hora': 'Time', 'dataHora': 'DateTime',
            'preco': 'Double', 'valor': 'Double', 'custo': 'Double',
            'quantidade': 'Integer', 'numero': 'Integer', 'total': 'Integer',
            'descricao': 'String', 'observacao': 'String', 'comentario': 'String',
            'estado': 'String', 'status': 'String', 'tipo': 'String',
            'ativo': 'Boolean', 'disponivel': 'Boolean', 'visivel': 'Boolean',
            'email': 'String', 'telefone': 'String', 'endereco': 'String',
            'codigo': 'String', 'referencia': 'String'
        }
        
        entity_lower = entity.lower()
        
        # Procurar por palavras-chave próximas à entidade
        for sentence in doc.sentences:
            if entity_lower in sentence.text.lower():
                for word in sentence.words:
                    text_lower = word.text.lower()
                    lemma_lower = word.lemma.lower()
                    
                    if text_lower in context_keywords:
                        attr_type = context_keywords[text_lower]
                        attr = {"nome": text_lower, "tipo": attr_type}
                        if attr not in attributes:
                            attributes.append(attr)
                    elif lemma_lower in context_keywords:
                        attr_type = context_keywords[lemma_lower]
                        attr = {"nome": lemma_lower, "tipo": attr_type}
                        if attr not in attributes:
                            attributes.append(attr)
        
        return attributes

    def _is_person_entity(self, entity: str) -> bool:
        """Identifica se uma entidade representa uma pessoa"""
        person_keywords = [
            'utilizador', 'usuario', 'cliente', 'funcionario', 'admin', 'administrador', 
            'gestor', 'medico', 'enfermeiro', 'professor', 'estudante', 'aluno', 'paciente'
        ]
        return any(keyword in entity for keyword in person_keywords)
    
    def _is_product_entity(self, entity: str) -> bool:
        """Identifica se uma entidade é produto/serviço"""
        product_keywords = [
            'produto', 'item', 'artigo', 'servico', 'mercadoria', 'bem'
        ]
        return any(keyword in entity for keyword in product_keywords)

    def _extract_relationships(self, doc, class_names) -> List[Dict[str, str]]:
        """Extrai relacionamentos mais abrangentes entre entidades"""
        relationships = []
        class_names_lower = [name.lower() for name in class_names]
        
        # Padrões de relacionamento expandidos
        relationship_patterns = {
            # Verbos de associação
            'tem': ('association', '1', '*'),
            'possui': ('association', '1', '*'),
            'contem': ('composition', '1', '*'),
            'inclui': ('composition', '1', '*'),
            
            # Verbos de uso/dependência
            'usa': ('dependency', '1', '1'),
            'utiliza': ('dependency', '1', '1'),
            'acede': ('dependency', '1', '1'),
            'consulta': ('dependency', '1', '1'),
            
            # Verbos de controle/gestão
            'gere': ('aggregation', '1', '*'),
            'controla': ('aggregation', '1', '*'),
            'administra': ('aggregation', '1', '*'),
            'supervisiona': ('aggregation', '1', '*'),
            
            # Verbos de criação
            'cria': ('dependency', '1', '*'),
            'gera': ('dependency', '1', '*'),
            'produz': ('dependency', '1', '*'),
            
            # Verbos de participação
            'participa': ('association', '*', '*'),
            'pertence': ('association', '*', '1'),
            'associa': ('association', '1', '*'),
            'relaciona': ('association', '1', '*')
        }
        
        # 1. Buscar relacionamentos diretos através de verbos
        for sentence in doc.sentences:
            sentence_text = sentence.text.lower()
            
            # Identificar classes mencionadas na sentença
            classes_in_sentence = []
            for class_name in class_names:
                if class_name.lower() in sentence_text:
                    classes_in_sentence.append(class_name)
            
            # Se há pelo menos 2 classes, procurar relacionamentos
            if len(classes_in_sentence) >= 2:
                for word in sentence.words:
                    if word.upos == "VERB":
                        verb_lemma = word.lemma.lower()
                        
                        if verb_lemma in relationship_patterns:
                            rel_type, card_source, card_target = relationship_patterns[verb_lemma]
                            
                            # Tentar identificar sujeito e objeto
                            subject_classes = []
                            object_classes = []
                            
                            # Buscar sujeito do verbo
                            for child in sentence.words:
                                if child.head == word.id and child.deprel in ["nsubj", "nsubj:pass"]:
                                    for cls in classes_in_sentence:
                                        if cls.lower() in child.text.lower():
                                            subject_classes.append(cls)
                            
                            # Buscar objeto do verbo
                            for child in sentence.words:
                                if child.head == word.id and child.deprel in ["obj", "iobj", "obl"]:
                                    for cls in classes_in_sentence:
                                        if cls.lower() in child.text.lower():
                                            object_classes.append(cls)
                            
                            # Criar relacionamentos encontrados
                            for subj_cls in subject_classes:
                                for obj_cls in object_classes:
                                    if subj_cls != obj_cls:
                                        relationships.append({
                                            "source": subj_cls,
                                            "target": obj_cls,
                                            "tipo": rel_type,
                                            "cardinalidade": f"{card_source}..{card_target}"
                                        })
        
        # 2. Buscar relacionamentos por proximidade e padrões textuais
        for i, class1 in enumerate(class_names):
            for j, class2 in enumerate(class_names):
                if i >= j:  # Evitar duplicatas
                    continue
                
                # Verificar se ambas as classes aparecem na mesma sentença
                for sentence in doc.sentences:
                    sentence_text = sentence.text.lower()
                    if class1.lower() in sentence_text and class2.lower() in sentence_text:
                        
                        # Padrões de relacionamento por proximidade
                        distance = self._calculate_word_distance(sentence_text, class1.lower(), class2.lower())
                        
                        if distance <= 5:  # Palavras próximas
                            # Inferir tipo de relacionamento baseado no contexto
                            rel_type = self._infer_relationship_type(sentence_text, class1, class2)
                            
                            relationships.append({
                                "source": class1,
                                "target": class2,
                                "tipo": rel_type,
                                "cardinalidade": "1..*"
                            })
        
        # 3. Relacionamentos implícitos baseados em padrões comuns
        implicit_relationships = self._generate_implicit_relationships(class_names)
        relationships.extend(implicit_relationships)
        
        # Remover duplicatas
        unique_relationships = []
        seen = set()
        for rel in relationships:
            key = (rel["source"], rel["target"], rel["tipo"])
            if key not in seen:
                seen.add(key)
                unique_relationships.append(rel)
        
        return unique_relationships

    def _find_matching_class(self, text: str, class_names: List[str]) -> str:
        """Encontra a classe que melhor corresponde ao texto de modo mais preciso"""
        text_lower = text.lower().strip()
        if not text_lower:
            return None
        
        # Normalizar texto para remoção de plurais
        if text_lower.endswith('s') and len(text_lower) > 3:
            text_singular = text_lower[:-1]
        else:
            text_singular = text_lower
        
        # 1. Correspondência exata (prioridade máxima)
        for class_name in class_names:
            if class_name.lower() == text_lower or class_name.lower() == text_singular:
                return class_name
        
        # 2. Correspondência por palavra completa (evita correspondências parciais)
        for class_name in class_names:
            class_lower = class_name.lower()
            if class_lower in text_lower.split() or text_lower in class_lower.split():
                return class_name
        
        # 3. Correspondência por raiz da palavra (apenas se for uma palavra única)
        if " " not in text_lower and len(text_lower) > 3:
            for class_name in class_names:
                # Verificar se é uma raiz comum (pelo menos 4 caracteres em comum)
                if len(text_lower) >= 4 and text_lower[:4] == class_name.lower()[:4]:
                    return class_name
        
        return None

    def _infer_cardinality(self, token, doc) -> str:
        """Infere a cardinalidade de um relacionamento"""
        # Por padrão, usar 1..* (um para muitos)
        return "1..*"
    
    def _calculate_word_distance(self, text: str, word1: str, word2: str) -> int:
        """Calcula a distância entre duas palavras no texto"""
        words = text.split()
        try:
            pos1 = next(i for i, w in enumerate(words) if word1 in w.lower())
            pos2 = next(i for i, w in enumerate(words) if word2 in w.lower())
            return abs(pos1 - pos2)
        except StopIteration:
            return float('inf')
    
    def _infer_relationship_type(self, sentence_text: str, class1: str, class2: str) -> str:
        """Infere o tipo de relacionamento baseado no contexto da sentença"""
        text = sentence_text.lower()
        
        # Padrões de contexto para tipos de relacionamento
        if any(word in text for word in ['tem', 'possui', 'contém', 'inclui']):
            return 'composition'
        elif any(word in text for word in ['usa', 'utiliza', 'acede', 'consulta']):
            return 'dependency'
        elif any(word in text for word in ['gere', 'controla', 'administra', 'supervisiona']):
            return 'aggregation'
        elif any(word in text for word in ['associa', 'relaciona', 'conecta', 'liga']):
            return 'association'
        else:
            return 'association'  # Padrão
    
    def _generate_implicit_relationships(self, class_names: List[str]) -> List[Dict[str, str]]:
        """Gera relacionamentos implícitos baseados em padrões comuns de domínio"""
        relationships = []
        
        # Padrões de relacionamento implícitos
        person_entities = []
        business_entities = []
        
        for class_name in class_names:
            class_lower = class_name.lower()
            if self._is_person_entity(class_lower):
                person_entities.append(class_name)
            elif self._is_business_entity(class_lower):
                business_entities.append(class_name)
        
        # Pessoas geralmente têm relacionamentos com entidades de negócio
        for person in person_entities:
            for business in business_entities:
                relationships.append({
                    "source": person,
                    "target": business,
                    "tipo": "association",
                    "cardinalidade": "1..*"
                })
        
        return relationships
    
    def _is_business_entity(self, entity: str) -> bool:
        """Verifica se uma entidade representa um conceito de negócio"""
        business_terms = {
            'produto', 'servico', 'pedido', 'encomenda', 'conta', 'factura',
            'consulta', 'aula', 'disciplina', 'curso', 'projeto', 'tarefa',
            'relatorio', 'documento', 'ficheiro', 'evento', 'reuniao',
            'categoria', 'grupo', 'departamento', 'secao', 'requisito'
        }
        return entity in business_terms

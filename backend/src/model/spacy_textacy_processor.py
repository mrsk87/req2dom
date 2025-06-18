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
        """Extrai apenas entidades principais que representam conceitos de domínio relevantes"""
        entities = set()
        
        # Vocabulário ultra-focado apenas em entidades centrais de domínio
        domain_entities = {
            # Atores principais (pessoas)
            'utilizador', 'cliente', 'funcionario', 'admin', 'administrador', 'gestor', 
            'medico', 'paciente', 'professor', 'aluno', 'estudante',
            
            # Entidades principais de negócio
            'produto', 'servico', 'pedido', 'encomenda', 'conta', 'factura',
            'consulta', 'aula', 'disciplina', 'curso', 'projeto',
            
            # Não plurais para evitar duplicações
            'usuario', 'pessoa', 'empregado', 'operador', 'tecnico',
            'director', 'gerente', 'enfermeiro', 'secretario'
        }
        
        # Análise de frequência de substantivos no texto
        noun_counts = {}
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 3 and not token.is_stop:
                text_lower = token.text.lower()
                noun_counts[text_lower] = noun_counts.get(text_lower, 0) + 1
        
        # 1. Primeiro, procurar entidades do vocabulário principal
        for token in doc:
            if (token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 3 and not token.is_stop):
                text_lower = token.text.lower()
                lemma = token.lemma_.lower()
                
                # Checar se é uma entidade do vocabulário principal
                if text_lower in domain_entities or lemma in domain_entities:
                    # Normalizar para forma singular (se possível)
                    if text_lower.endswith('s') and text_lower[:-1] in domain_entities:
                        entities.add(text_lower[:-1])
                    else:
                        entities.add(text_lower)
        
        # 2. Análise de sujeitos principais nas frases
        subject_nouns = []
        for token in doc:
            if token.dep_ == "nsubj" and token.pos_ == "NOUN" and len(token.text) > 3 and not token.is_stop:
                text_lower = token.text.lower()
                # Normalizar para forma singular (se possível)
                if text_lower.endswith('s') and len(text_lower) > 4:
                    subject_nouns.append(text_lower[:-1])
                else:
                    subject_nouns.append(text_lower)
        
        # Adicionar substantivos que são sujeitos e aparecem mais de uma vez
        for noun in subject_nouns:
            if noun_counts.get(noun, 0) > 1:
                entities.add(noun)
                
        # 3. Filtrar palavras muito genéricas e irrelevantes
        exclude_words = {
            'sistema', 'aplicacao', 'plataforma', 'dados', 'informacao', 'processo',
            'forma', 'tipo', 'caso', 'parte', 'meio', 'modo', 'vez', 'tempo', 'lugar', 
            'estado', 'coisa', 'exemplo', 'numero', 'valor', 'nivel', 'grupo',
            'versao', 'recurso', 'acesso', 'funcao', 'pagina', 'opcao', 'erro', 'codigo'
        }
        
        # Manter apenas entidades válidas e relevantes
        filtered_entities = []
        for entity in entities:
            if (len(entity) >= 3 and 
                entity not in exclude_words and
                not entity.isdigit()):
                filtered_entities.append(entity)
        
        # Se não encontrou entidades válidas, extrair os substantivos mais comuns
        if not filtered_entities:
            common_nouns = sorted(noun_counts.items(), key=lambda x: x[1], reverse=True)
            for noun, count in common_nouns[:3]:
                if (len(noun) >= 3 and 
                    noun not in exclude_words and
                    not noun.isdigit()):
                    filtered_entities.append(noun)
        
        # Limitar a 3 entidades para manter o modelo simples e relevante
        return filtered_entities[:3]
    
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
        for sent in doc.sents:
            if entity_lower in sent.text.lower():
                for token in sent:
                    text_lower = token.text.lower()
                    lemma_lower = token.lemma_.lower()
                    
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
    
    def _infer_attributes_from_context_advanced(self, entity: str, doc) -> List[Dict[str, str]]:
        """Inferência avançada de atributos baseada em análise semântica e sintática"""
        attributes = []
        
        # Expandir significativamente as palavras-chave contextuais
        context_keywords = {
            # Identificação
            'nome': 'String', 'titulo': 'String', 'designacao': 'String', 'etiqueta': 'String',
            'codigo': 'String', 'referencia': 'String', 'identificador': 'String', 'id': 'Integer',
            'numero': 'Integer', 'sequencia': 'String', 'serie': 'String', 'versao': 'String',
            
            # Comunicação
            'email': 'String', 'correio': 'String', 'telefone': 'String', 'telemovel': 'String',
            'fax': 'String', 'contacto': 'String', 'website': 'String', 'url': 'String',
            'skype': 'String', 'linkedin': 'String', 'facebook': 'String', 'twitter': 'String',
            
            # Localização
            'endereco': 'String', 'morada': 'String', 'localizacao': 'String', 'local': 'String',
            'coordenadas': 'String', 'latitude': 'Double', 'longitude': 'Double',
            'pais': 'String', 'cidade': 'String', 'distrito': 'String', 'regiao': 'String',
            'codigo_postal': 'String', 'cep': 'String', 'zona': 'String', 'bairro': 'String',
            
            # Temporal
            'data': 'Date', 'hora': 'Time', 'dataHora': 'DateTime', 'timestamp': 'DateTime',
            'dataInicio': 'Date', 'dataFim': 'Date', 'dataCreacao': 'Date', 'dataModificacao': 'Date',
            'dataRegisto': 'Date', 'dataVencimento': 'Date', 'dataValidade': 'Date',
            'duracao': 'Integer', 'prazo': 'Date', 'periodo': 'String', 'intervalo': 'Integer',
            
            # Financeiro
            'preco': 'Double', 'valor': 'Double', 'custo': 'Double', 'montante': 'Double',
            'taxa': 'Double', 'desconto': 'Double', 'iva': 'Double', 'imposto': 'Double',
            'juros': 'Double', 'comissao': 'Double', 'saldo': 'Double', 'credito': 'Double',
            'debito': 'Double', 'orcamento': 'Double', 'lucro': 'Double', 'receita': 'Double',
            
            # Quantidades
            'quantidade': 'Integer', 'stock': 'Integer', 'inventario': 'Integer',
            'capacidade': 'Integer', 'limite': 'Integer', 'minimo': 'Integer', 'maximo': 'Integer',
            'peso': 'Double', 'altura': 'Double', 'largura': 'Double', 'comprimento': 'Double',
            'area': 'Double', 'volume': 'Double', 'densidade': 'Double', 'velocidade': 'Double',
            
            # Estados e condições
            'estado': 'String', 'status': 'String', 'condicao': 'String', 'situacao': 'String',
            'fase': 'String', 'etapa': 'String', 'nivel': 'String', 'grau': 'String',
            'prioridade': 'String', 'urgencia': 'String', 'importancia': 'String',
            'qualidade': 'String', 'performance': 'Double', 'eficiencia': 'Double',
            
            # Descritivos
            'descricao': 'String', 'observacoes': 'String', 'comentarios': 'String',
            'notas': 'String', 'detalhes': 'String', 'especificacoes': 'String',
            'caracteristicas': 'String', 'propriedades': 'String', 'resumo': 'String',
            
            # Classificação
            'tipo': 'String', 'categoria': 'String', 'classe': 'String', 'grupo': 'String',
            'familia': 'String', 'marca': 'String', 'modelo': 'String', 'edicao': 'String',
            'formato': 'String', 'estilo': 'String', 'genero': 'String',
            
            # Controlo e configuração
            'ativo': 'Boolean', 'disponivel': 'Boolean', 'visivel': 'Boolean', 'publico': 'Boolean',
            'privado': 'Boolean', 'aprovado': 'Boolean', 'validado': 'Boolean', 'confirmado': 'Boolean',
            'configuracao': 'String', 'parametros': 'String', 'opcoes': 'String',
            'definicoes': 'String', 'preferencias': 'String',
            
            # Tecnológicos
            'porta': 'Integer', 'protocolo': 'String', 'encoding': 'String', 'formato': 'String',
            'extensao': 'String', 'mime_type': 'String', 'hash': 'String', 'checksum': 'String',
            'backup': 'String', 'restore': 'String', 'sincronizacao': 'DateTime',
            
            # Segurança
            'password': 'String', 'senha': 'String', 'token': 'String', 'chave': 'String',
            'permissao': 'String', 'papel': 'String', 'role': 'String', 'acesso': 'String',
            'autorizacao': 'String', 'certificado': 'String', 'licenca': 'String'
        }
        
        # Análise do contexto do texto onde a entidade aparece
        entity_lower = entity.lower()
        
        # Procurar por padrões no texto próximo à entidade
        for sent in doc.sents:
            if entity_lower in sent.text.lower():
                # Analisar tokens na frase que contém a entidade
                for token in sent:
                    text_lower = token.text.lower()
                    lemma_lower = token.lemma_.lower()
                    
                    # Verificar palavras-chave do contexto
                    if text_lower in context_keywords or lemma_lower in context_keywords:
                        attr_name = text_lower if text_lower in context_keywords else lemma_lower
                        attr_type = context_keywords[attr_name]
                        
                        # Evitar duplicatas
                        if {"nome": attr_name, "tipo": attr_type} not in attributes:
                            attributes.append({"nome": attr_name, "tipo": attr_type})
                    
                    # Procurar por padrões sintáticos (ex: "X tem Y", "Y de X")
                    if token.dep_ in ["nmod", "amod", "compound"] and token.head.text.lower() == entity_lower:
                        possible_attr = token.text.lower()
                        if possible_attr in context_keywords:
                            attr_type = context_keywords[possible_attr]
                            if {"nome": possible_attr, "tipo": attr_type} not in attributes:
                                attributes.append({"nome": possible_attr, "tipo": attr_type})
        
        # Usar textacy para extração de n-gramas e frases nominais
        if hasattr(self, 'textacy_available') and self.textacy_available:
            try:
                import textacy
                # Extrair frases nominais que podem indicar atributos
                noun_chunks = list(doc.noun_chunks)
                for chunk in noun_chunks:
                    if entity_lower in chunk.text.lower():
                        for token in chunk:
                            if token.text.lower() in context_keywords:
                                attr_name = token.text.lower()
                                attr_type = context_keywords[attr_name]
                                if {"nome": attr_name, "tipo": attr_type} not in attributes:
                                    attributes.append({"nome": attr_name, "tipo": attr_type})
            except Exception:
                pass  # Continuar sem textacy se houver erro
        
        # Inferência baseada em padrões linguísticos portugueses
        import re
        for sent in doc.sents:
            sent_text = sent.text.lower()
            if entity_lower in sent_text:
                # Padrões: "entidade tem X", "X da entidade", "entidade com X"
                patterns = [
                    rf'{re.escape(entity_lower)}\s+tem\s+(\w+)',
                    rf'{re.escape(entity_lower)}\s+possui\s+(\w+)',
                    rf'{re.escape(entity_lower)}\s+com\s+(\w+)',
                    rf'(\w+)\s+d[ao]\s+{re.escape(entity_lower)}',
                    rf'{re.escape(entity_lower)}\s+(\w+ed[ao]|[ao])\s+(\w+)',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, sent_text)
                    for match in matches:
                        if isinstance(match, tuple):
                            for m in match:
                                if m in context_keywords:
                                    attr_name = m
                                    attr_type = context_keywords[m]
                                    if {"nome": attr_name, "tipo": attr_type} not in attributes:
                                        attributes.append({"nome": attr_name, "tipo": attr_type})
                        else:
                            if match in context_keywords:
                                attr_name = match
                                attr_type = context_keywords[match]
                                if {"nome": attr_name, "tipo": attr_type} not in attributes:
                                    attributes.append({"nome": attr_name, "tipo": attr_type})
        
        return attributes

    def _extract_relationships(self, doc, class_names) -> List[Dict[str, str]]:
        """Extrai apenas relacionamentos claros e diretos entre entidades"""
        relationships = []
        class_names_lower = [name.lower() for name in class_names]
        
        # Verbos que expressam relacionamentos claros
        core_relationship_verbs = {
            # Associação direta
            'tem': 'association',
            'possui': 'association',
            # Dependência
            'usa': 'dependency',
            'utiliza': 'dependency',
            # Controle
            'gere': 'control',
            'controla': 'control',
            'administra': 'control'
        }
        
        # 1. Analisar cada sentença separadamente
        for sent in doc.sents:
            # Encontrar classes mencionadas nesta sentença
            classes_in_sent = {}  # {nome-classe-lower: Nome-Classe-Original}
            for class_name in class_names:
                if class_name.lower() in sent.text.lower():
                    classes_in_sent[class_name.lower()] = class_name
            
            # Se há pelo menos duas classes na sentença
            if len(classes_in_sent) >= 2:
                # Procurar verbos conectores
                for token in sent:
                    if token.pos_ == "VERB" and token.lemma_ in core_relationship_verbs:
                        verb = token.lemma_
                        rel_type = core_relationship_verbs[verb]
                        
                        # Encontrar sujeito e objeto direcionados pelo verbo
                        subject_class = None
                        object_class = None
                        
                        # Analisar sujeito
                        for child in token.children:
                            if child.dep_ == "nsubj":
                                # Verificar se o sujeito é uma classe
                                for cls_lower, cls_original in classes_in_sent.items():
                                    if cls_lower in child.text.lower():
                                        subject_class = cls_original
                        
                        # Analisar objeto
                        for child in token.children:
                            if child.dep_ in ["dobj", "pobj"]:
                                # Verificar se o objeto é uma classe
                                for cls_lower, cls_original in classes_in_sent.items():
                                    if cls_lower in child.text.lower():
                                        object_class = cls_original
                        
                        # Se encontrou as duas partes, criar relacionamento
                        if subject_class and object_class and subject_class != object_class:
                            # Determinar cardinalidade básica
                            cardinality = "1.1"  # Padrão
                            if verb in ['tem', 'possui', 'contém']:
                                cardinality = "1..*"
                            
                            # Adicionar relacionamento único
                            exists = any(
                                r["source"] == subject_class and r["target"] == object_class 
                                for r in relationships
                            )
                            
                            if not exists:
                                relationships.append({
                                    "source": subject_class,
                                    "target": object_class,
                                    "tipo": rel_type,
                                    "cardinalidade": cardinality
                                })
        
        # 2. Se não encontrou relacionamentos sintáticos, verificar padrões comuns
        if not relationships and len(class_names) >= 2:
            # Relacionamentos semanticamente lógicos baseados em tipos
            for class1 in class_names:
                for class2 in class_names:
                    if class1 != class2:
                        c1_lower = class1.lower()
                        c2_lower = class2.lower()
                        
                        # Padrões comuns de relacionamento (pessoa-objeto)
                        if self._is_person_entity(c1_lower) and not self._is_person_entity(c2_lower):
                            # Pessoas normalmente usam ou gerenciam coisas
                            relationships.append({
                                "source": class1,
                                "target": class2,
                                "tipo": "control" if c2_lower in ["sistema", "pedido", "encomenda"] else "association",
                                "cardinalidade": "1..*"
                            })
                            break  # Apenas um relacionamento
        
        # Máximo 1 relacionamento por entidade para evitar diagramas muito complexos
        unique_rels = []
        seen_sources = set()
        
        for rel in relationships:
            if rel["source"] not in seen_sources:
                seen_sources.add(rel["source"])
                unique_rels.append(rel)
        
        return unique_rels
    
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
        """Simplificado: retorna 1..* para verbos como 'tem', 'possui', etc."""
        plural_verbs = {'tem', 'possui', 'contem', 'inclui', 'gerencia'}
        
        if token.lemma_.lower() in plural_verbs:
            return "1..*"
        
        # Padrão simplificado
        return "1.1"

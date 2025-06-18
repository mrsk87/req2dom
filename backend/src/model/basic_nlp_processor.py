"""
Processador NLP básico sem dependências externas pesadas
"""
import logging
import json
import re
from typing import Dict, Any, List, Set

logger = logging.getLogger("basic_nlp_processor")

class BasicNLPProcessor:
    """
    Processador NLP básico que extrai entidades de domínio usando técnicas simples
    sem dependências externas pesadas como spaCy
    """
    
    def __init__(self):
        """Inicializa o processador NLP básico"""
        logger.info("BasicNLPProcessor inicializado")
        
        # Palavras-chave comuns em sistemas de negócio
        self.domain_keywords = {
            'utilizador', 'usuario', 'cliente', 'pessoa', 'funcionario', 'admin', 'administrador',
            'gestor', 'operador', 'sistema', 'servico', 'produto', 'item', 'pedido', 'venda', 
            'compra', 'agenda', 'marcacao', 'agendamento', 'evento', 'tarefa', 'atividade', 
            'processo', 'documento', 'relatorio', 'registro', 'registo', 'categoria', 'tipo',
            'endereco', 'contato', 'contacto', 'telefone', 'email', 'dados', 'pagamento', 
            'valor', 'preco', 'custo', 'quantidade', 'data', 'hora', 'periodo', 'prazo', 
            'status', 'estado', 'empresa', 'organizacao', 'departamento', 'conta', 'sessao',
            'reserva', 'booking', 'appointment', 'meeting', 'project', 'projeto', 'arquivo',
            'ficheiro', 'file', 'folder', 'pasta', 'configuracao', 'definicao', 'setting'
        }
        
        # Palavras que indicam atributos
        self.attribute_keywords = {
            'nome': 'String',
            'email': 'String',
            'telefone': 'String',
            'endereco': 'String',
            'morada': 'String',
            'data': 'Date',
            'hora': 'Time',
            'datahora': 'DateTime',
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
            'comentarios': 'String',
            'nif': 'String',
            'cc': 'String',
            'id': 'Integer',
            'identificador': 'Integer',
            'password': 'String',
            'senha': 'String',
            'ativo': 'Boolean',
            'disponivel': 'Boolean',
            'aprovado': 'Boolean',
            'verificado': 'Boolean'
        }
    
    def extract_domain_entities(self, requirements_text: str) -> Dict[str, Any]:
        """
        Extrai entidades de domínio usando técnicas básicas de NLP
        
        Args:
            requirements_text (str): Texto com os requisitos
            
        Returns:
            dict: Estrutura de dados com as entidades e seus relacionamentos
        """
        logger.info(f"Iniciando processamento NLP básico de {len(requirements_text)} caracteres")
        
        try:
            # Pré-processar requisitos RF
            processed_text = self._preprocess_requirements(requirements_text)
            
            # Extrair entidades principais
            entities = self._extract_entities(processed_text)
            
            # Criar classes com atributos
            classes = {}
            for entity in entities:
                class_name = entity.capitalize()
                classes[class_name] = {
                    "nome": class_name,
                    "atributos": self._get_attributes_for_entity(entity, processed_text),
                    "relacionamentos": []
                }
            
            # Extrair relacionamentos básicos
            relationships = self._extract_basic_relationships(entities, processed_text)
            for rel in relationships:
                source_class = rel["source"]
                if source_class in classes:
                    classes[source_class]["relacionamentos"].append({
                        "tipo": rel["tipo"],
                        "alvo": rel["target"],
                        "cardinalidade": rel["cardinalidade"]
                    })
            
            result = {"classes": list(classes.values())}
            logger.info(f"Processamento concluído: {len(classes)} classes extraídas")
            return {"content": json.dumps(result, ensure_ascii=False, indent=2)}
            
        except Exception as e:
            error_msg = f"Erro no processamento NLP básico: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _preprocess_requirements(self, text: str) -> str:
        """Pré-processa requisitos que começam com RF[número]"""
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
    
    def _extract_entities(self, text: str) -> Set[str]:
        """Extrai entidades principais do texto"""
        entities = set()
        text_lower = text.lower()
        
        # Procurar por palavras-chave do domínio
        words = re.findall(r'\b\w+\b', text_lower)
        
        for word in words:
            if word in self.domain_keywords and len(word) > 2:
                entities.add(word)
        
        # Procurar por substantivos que parecem entidades (palavras capitalizadas)
        capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', text)
        for word in capitalized_words:
            if len(word) > 3 and word.lower() not in ['para', 'como', 'deve', 'pode', 'cada', 'esta', 'esse', 'isso']:
                entities.add(word.lower())
        
        # Garantir que temos pelo menos algumas entidades básicas
        if len(entities) < 2:
            entities.update(['utilizador', 'sistema'])
        
        return entities
    
    def _get_attributes_for_entity(self, entity: str, text: str) -> List[Dict[str, str]]:
        """Determina atributos para uma entidade com base no contexto"""
        attributes = []
        entity_lower = entity.lower()
        text_lower = text.lower()
        
        # Atributos básicos universais
        attributes.append({"nome": "id", "tipo": "Integer"})
        
        # Atributos específicos baseados no tipo de entidade
        if any(word in entity_lower for word in ['utilizador', 'usuario', 'cliente', 'pessoa', 'funcionario', 'admin', 'gestor']):
            # Entidades que representam pessoas
            attributes.extend([
                {"nome": "nome", "tipo": "String"},
                {"nome": "email", "tipo": "String"},
                {"nome": "telefone", "tipo": "String"},
                {"nome": "endereco", "tipo": "String"}
            ])
        elif any(word in entity_lower for word in ['evento', 'marcacao', 'agendamento', 'reserva', 'sessao']):
            # Entidades de agendamento/eventos
            attributes.extend([
                {"nome": "dataHora", "tipo": "DateTime"},
                {"nome": "observacoes", "tipo": "String"},
                {"nome": "estado", "tipo": "String"}
            ])
        elif any(word in entity_lower for word in ['servico', 'produto', 'item']):
            # Entidades de serviço/produto
            attributes.extend([
                {"nome": "nome", "tipo": "String"},
                {"nome": "descricao", "tipo": "String"},
                {"nome": "preco", "tipo": "Double"},
                {"nome": "tipo", "tipo": "String"}
            ])
        elif any(word in entity_lower for word in ['pedido', 'venda', 'compra', 'pagamento']):
            # Entidades de transação
            attributes.extend([
                {"nome": "data", "tipo": "Date"},
                {"nome": "valor", "tipo": "Double"},
                {"nome": "estado", "tipo": "String"}
            ])
        else:
            # Entidades genéricas
            attributes.extend([
                {"nome": "nome", "tipo": "String"},
                {"nome": "descricao", "tipo": "String"}
            ])
        
        # Procurar por atributos mencionados no contexto
        for attr_name, attr_type in self.attribute_keywords.items():
            if attr_name in text_lower and not any(attr["nome"] == attr_name for attr in attributes):
                attributes.append({"nome": attr_name, "tipo": attr_type})
        
        return attributes
    
    def _extract_basic_relationships(self, entities: Set[str], text: str) -> List[Dict[str, str]]:
        """Extrai relacionamentos básicos entre entidades"""
        relationships = []
        entities_list = list(entities)
        text_lower = text.lower()
        
        # Relacionamentos baseados em padrões comuns
        person_entities = []
        other_entities = []
        
        for entity in entities_list:
            if any(word in entity for word in ['utilizador', 'usuario', 'cliente', 'pessoa', 'funcionario', 'admin', 'gestor']):
                person_entities.append(entity.capitalize())
            else:
                other_entities.append(entity.capitalize())
        
        # Criar relacionamentos entre pessoas e outras entidades
        for person in person_entities:
            for other in other_entities:
                # Determinar tipo de relacionamento baseado no contexto
                if any(word in text_lower for word in ['criar', 'adicionar', 'registar', 'inserir']):
                    rel_type = "composicao"
                    cardinalidade = "1..n"
                elif any(word in text_lower for word in ['ter', 'possuir', 'associar']):
                    rel_type = "associacao"
                    cardinalidade = "1..n"
                else:
                    rel_type = "associacao"
                    cardinalidade = "0..n"
                
                relationships.append({
                    "source": person,
                    "target": other,
                    "tipo": rel_type,
                    "cardinalidade": cardinalidade
                })
        
        return relationships

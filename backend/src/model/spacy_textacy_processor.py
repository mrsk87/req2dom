import logging  # Registo de eventos e erros
import spacy    # Biblioteca principal de NLP
import textacy.extract  # Extensões para extração de padrões em texto
import re       # Expressões regulares para pré-processamento
import json     # Manipulação de JSON para estrutura de saída
from typing import Dict, Any, List  # Tipagem estática para documentação

# Configurar o logger para o processador spaCy+textacy
logger = logging.getLogger("spacy_textacy_processor")

class SpacyTextacyProcessor:
    """
    Processador NLP avançado usando spaCy + textacy para
    extração de entidades, atributos e relacionamentos de requisitos
    """
    
    def __init__(self, lang_model: str = "pt_core_news_lg"):
        """
        Inicializa o modelo spaCy.
        Tenta carregar o modelo em Português, senão faz fallback para Inglês.

        Args:
            lang_model (str): Nome do modelo spaCy a carregar (padrão: pt_core_news_lg)
        """
        try:
            # Carregar modelo específico para Português
            self.nlp = spacy.load(lang_model)
            logger.info(f"Modelo spaCy carregado: {lang_model}")
        except Exception:
            # Caso falhe, usar modelo em inglês como fallback
            self.nlp = spacy.load("en_core_web_lg")
            logger.info("Modelo spaCy em inglês carregado como fallback")

    def extract_domain_entities(self, requirements_text: str) -> Dict[str, Any]:
        """
        Extrai entidades de domínio a partir do texto de requisitos.
        Combina pré-processamento, extração de entidades principais,
        atributos e relacionamentos.

        Args:
            requirements_text (str): Texto bruto com requisitos (pode incluir RFxx)

        Returns:
            Dict[str, Any]: Dicionário com chave 'content' contendo JSON
        """
        logger.info(f"Iniciando processamento spaCy+textacy ({len(requirements_text)} caracteres)")
        try:
            # 1. Pré-processar texto para destacar requisitos RF
            processed = self._preprocess_requirements(requirements_text)
            # Converter texto em objeto spaCy
            doc = self.nlp(processed)

            # Estrutura temporária para classes descobertas
            classes: Dict[str, Any] = {}

            # 2. Extrair entidades principais (substantivos relevantes)
            main_entities = self._extract_main_entities(doc)

            # 3. Para cada entidade principal, definir classe e atributos
            for ent in main_entities:
                class_name = ent.capitalize()
                # Inicializar estrutura de classe se não existir
                if class_name not in classes:
                    classes[class_name] = {
                        "nome": class_name,
                        "atributos": [],
                        "relacionamentos": []
                    }
                # Extrair atributos específicos da entidade
                attrs = self._extract_attributes_for_entity(ent, doc)
                classes[class_name]["atributos"].extend(attrs)

            # 4. Extrair relacionamentos sintáticos entre entidades
            rels = self._extract_relationships(doc, classes.keys())
            for rel in rels:
                src = rel["source"]
                # Adicionar relacionamento à classe de origem
                if src in classes:
                    classes[src]["relacionamentos"].append({
                        "tipo": rel["tipo"],
                        "alvo": rel["target"],
                        "cardinalidade": rel["cardinalidade"]
                    })

            # 5. Eliminar duplicados em atributos e relacionamentos
            for cls in classes.values():
                # Atributos únicos
                seen = set()
                unique_attrs = []
                for a in cls["atributos"]:
                    key = (a["nome"], a["tipo"])
                    if key not in seen:
                        seen.add(key)
                        unique_attrs.append(a)
                cls["atributos"] = unique_attrs
                # Relacionamentos únicos
                seen_rel = set()
                unique_rels = []
                for r in cls["relacionamentos"]:
                    key = (r["tipo"], r["alvo"], r["cardinalidade"])
                    if key not in seen_rel:
                        seen_rel.add(key)
                        unique_rels.append(r)
                cls["relacionamentos"] = unique_rels

            # 6. Construir resultado final e converter para JSON formatado
            result = {"classes": list(classes.values())}
            logger.info(f"Processamento concluído: {len(result['classes'])} classes extraídas")
            return {"content": json.dumps(result, ensure_ascii=False, indent=2)}

        except Exception as e:
            # Em caso de erro, registar e retornar mensagem
            msg = f"Erro no processamento spaCy+textacy: {e}"
            logger.error(msg)
            return {"error": msg}

    def _preprocess_requirements(self, text: str) -> str:
        """
        Pré-processa texto de requisitos para substituir blocos RFxx
        por linhas mais legíveis para análise.

        Args:
            text (str): Texto original de requisitos

        Returns:
            str: Texto reformulado (ou original se sem padrões RF)
        """
        pattern = r"RF\d+\.\s*(.*?)(?=RF\d+\.|$)"
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            # Numerar requisitos de forma legível
            nums = re.findall(r"RF(\d+)", text)
            out = []
            for txt, num in zip(matches, nums):
                out.append(f"Requisito {num}: {txt.strip()}")
            return "\n\n".join(out)
        return text

    def _extract_main_entities(self, doc) -> List[str]:
        """
        Identifica substantivos e entidades nomeadas relevantes
        para formar classes de domínio.

        Args:
            doc: Objeto spaCy

        Returns:
            List[str]: Lista de entidades em minúsculas
        """
        entities = set()
        # Conjunto de palavras-chave do domínio
        domain_keywords = {
            'cliente', 'usuario', 'pessoa', 'funcionario', 'sistema', 'servico',
            'produto', 'pedido', 'venda', 'compra', 'agenda', 'evento', 'tarefa',
            'documento', 'relatorio', 'categoria', 'endereco', 'contato',
            'telefone', 'email', 'pagamento', 'preco', 'quantidade', 'data'
        }
        # Extrair tokens substantivos e nomes próprios
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and not token.is_punct:
                lemma = token.lemma_.lower()
                if lemma in domain_keywords or token.pos_ == "PROPN":
                    entities.add(lemma)
        # Extrair entidades nomeadas (PERSON, ORG, PRODUCT)
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "PRODUCT"]:
                entities.add(ent.text.lower())
        return list(entities)

    def _extract_attributes_for_entity(self, entity: str, doc) -> List[Dict[str, str]]:
        """
        Define atributos padrão e específicos conforme o nome da entidade.
        Se não houver padrão, tenta inferir do contexto.

        Args:
            entity (str): Nome da entidade
            doc: Objeto spaCy

        Returns:
            List[Dict[str,str]]: Lista de atributos com 'nome' e 'tipo'
        """
        ent_low = entity.lower()
        # Atributos básicos comuns
        basic = [
            {"nome": "id", "tipo": "Integer"},
            {"nome": "nome", "tipo": "String"}
        ]
        # Padrões específicos conforme tipo de entidade
        if any(w in ent_low for w in ['pessoa', 'cliente', 'usuario']):
            return [
                {"nome": "id", "tipo": "Integer"},
                {"nome": "nome", "tipo": "String"},
                {"nome": "email", "tipo": "String"},
                {"nome": "telefone", "tipo": "String"},
                {"nome": "endereco", "tipo": "String"}
            ]
        elif any(w in ent_low for w in ['consulta', 'marcacao', 'agendamento']):
            return [
                {"nome": "id", "tipo": "Integer"},
                {"nome": "dataHora", "tipo": "DateTime"},
                {"nome": "observacoes", "tipo": "String"},
                {"nome": "estado", "tipo": "String"}
            ]
        elif any(w in ent_low for w in ['servico', 'produto']):
            return [
                {"nome": "id", "tipo": "Integer"},
                {"nome": "nome", "tipo": "String"},
                {"nome": "descricao", "tipo": "String"},
                {"nome": "preco", "tipo": "Double"},
                {"nome": "tipo", "tipo": "String"}
            ]
        else:
            # Tentar inferir atributos do contexto ou usar básicos + 'descricao'
            ctx_attrs = self._infer_attributes_from_context(entity, doc)
            return basic + (ctx_attrs if ctx_attrs else [{"nome": "descricao", "tipo": "String"}])

    def _infer_attributes_from_context(self, entity: str, doc) -> List[Dict[str, str]]:
        """
        Procura palavras-chave no texto que indiquem atributos adicionais.

        Args:
            entity (str): Nome da entidade
            doc: Objeto spaCy

        Returns:
            List[Dict[str,str]]: Atributos inferidos com base no contexto
        """
        attrs = []
        keywords = {
            'nome': 'String', 'email': 'String', 'telefone': 'String',
            'data': 'Date', 'hora': 'Time', 'preco': 'Double',
            'quantidade': 'Integer', 'status': 'String', 'descricao': 'String'
        }
        for token in doc:
            low = token.text.lower()
            if low in keywords and {"nome": low, "tipo": keywords[low]} not in attrs:
                attrs.append({"nome": low, "tipo": keywords[low]})
        return attrs

    def _extract_relationships(self, doc, entity_names) -> List[Dict[str, str]]:
        """
        Identifica relacionamentos genéricos entre entidades via análise sintática
        e heurísticas padrão.
        """
        relationships: List[Dict[str,str]] = []
        names = list(entity_names)
        # Percorrer cada frase para padrões de sujeito/objeto
        for sent in doc.sents:
            for token in sent:
                if token.dep_ in ["nsubj", "dobj", "pobj"] and token.head.pos_ == "VERB":
                    subj_ents = []
                    obj_ents = []
                    # Verificar ocorrências de entidades na frase
                    for name in names:
                        if name.lower() in sent.text.lower():
                            if token.dep_ == "nsubj":
                                subj_ents.append(name.capitalize())
                            else:
                                obj_ents.append(name.capitalize())
                    # Construir relacionamentos entre cada par encontrado
                    for s in subj_ents:
                        for o in obj_ents:
                            if s != o:
                                rel_type = self._determine_relationship_type(token.head.lemma_, s, o)
                                card = self._determine_cardinality(sent.text, s, o)
                                relationships.append({
                                    "source": s,
                                    "target": o,
                                    "tipo": rel_type,
                                    "cardinalidade": card
                                })
        # Adicionar relacionamentos padrão se não detectados sintaticamente
        for i, e1 in enumerate(names):
            for e2 in names[i+1:]:
                if self._entities_likely_related(e1, e2):
                    t, c = self._get_default_relationship(e1, e2)
                    relationships.append({"source": e1.capitalize(), "target": e2.capitalize(), "tipo": t, "cardinalidade": c})
        return relationships

    def _determine_relationship_type(self, verb: str, source: str, target: str) -> str:
        """
        Determina tipo de relacionamento com base no verbo principal.
        """
        v = verb.lower()
        if v in ['ter', 'possuir', 'conter', 'incluir']:
            return "composicao"
        elif v in ['usar', 'referenciar', 'associar']:
            return "associacao"
        elif v in ['herdar', 'estender', 'implementar']:
            return "heranca"
        return "associacao"  # padrão

    def _determine_cardinality(self, sentence: str, source: str, target: str) -> str:
        """
        Define cardinalidade com base em palavras-chave no contexto da frase.
        """
        s = sentence.lower()
        if any(w in s for w in ['varios', 'muitos', 'multiplos']):
            return "1..n"
        if any(w in s for w in ['um', 'uma', 'one']):
            return "1..1"
        if any(w in s for w in ['opcional', 'pode', 'may']):
            return "0..1"
        return "1..n"

    def _entities_likely_related(self, entity1: str, entity2: str) -> bool:
        """
        Heurística simples: se uma entidade for do tipo pessoa e outra não,
        assume que se relacionam.
        """
        people = ['admin', 'cliente', 'usuario', 'funcionario']
        e1 = entity1.lower()
        e2 = entity2.lower()
        p1 = any(w in e1 for w in people)
        p2 = any(w in e2 for w in people)
        return p1 != p2

    def _get_default_relationship(self, entity1: str, entity2: str) -> Any:
        """
        Retorna relacionamento padrão (associação) e cardinalidade.
        """
        # Se um for pessoa e outro não, associação 1..n, senão 0..n
        if self._entities_likely_related(entity1, entity2):
            return "associacao", "1..n"
        return "associacao", "0..n"

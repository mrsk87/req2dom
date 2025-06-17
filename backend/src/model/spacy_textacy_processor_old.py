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
        doc = self.nlp(requirements_text)
        classes = {}
        relationships = []

        # 1. Identificar entidades nomeadas e substantivos como classes
        for ent in doc.ents:
            if ent.label_ in ["PER", "ORG", "LOC", "PRODUCT", "PERSON", "ORG", "GPE", "FAC"]:
                name = ent.text.strip().capitalize()
                if name not in classes:
                    classes[name] = {"nome": name, "atributos": [], "relacionamentos": []}
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop:
                name = token.lemma_.capitalize()
                if name not in classes:
                    classes[name] = {"nome": name, "atributos": [], "relacionamentos": []}

        # 2. Identificar atributos (adjetivos, substantivos ligados por 'de', 'do', etc)
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop:
                class_name = token.lemma_.capitalize()
                # Atributos por dependência
                for child in token.children:
                    if child.dep_ in ["amod", "nummod", "poss", "appos"] or child.pos_ == "ADJ":
                        attr = {"nome": child.lemma_, "tipo": child.pos_}
                        if attr not in classes[class_name]["atributos"]:
                            classes[class_name]["atributos"].append(attr)
                # Atributos por padrão "de"
                for prep in token.children:
                    if prep.dep_ == "prep" and prep.lemma_ == "de":
                        for pobj in prep.children:
                            if pobj.pos_ in ["NOUN", "PROPN"]:
                                attr = {"nome": pobj.lemma_, "tipo": pobj.pos_}
                                if attr not in classes[class_name]["atributos"]:
                                    classes[class_name]["atributos"].append(attr)

        # 3. Identificar relacionamentos usando textacy
        for sent in doc.sents:
            sdoc = self.nlp(sent.text)
            for subj, verb, obj in textacy.extract.subject_verb_object_triples(sdoc):
                subj_name = subj.text.capitalize()
                obj_name = obj.text.capitalize()
                if subj_name in classes and obj_name in classes:
                    # Cardinalidade heurística
                    card = "1..n" if re.search(r"muitos|vários|itens|lista|cada", sent.text, re.I) else "0..1"
                    rel = {"tipo": "associacao", "alvo": obj_name, "cardinalidade": card}
                    if rel not in classes[subj_name]["relacionamentos"]:
                        classes[subj_name]["relacionamentos"].append(rel)
                    # Relacionamento reverso
                    rel_rev = {"tipo": "associacao", "alvo": subj_name, "cardinalidade": "0..1" if card=="1..n" else "1..n"}
                    if rel_rev not in classes[obj_name]["relacionamentos"]:
                        classes[obj_name]["relacionamentos"].append(rel_rev)

        # 4. Montar lista final
        result = {"classes": list(classes.values())}
        return {"content": json.dumps(result, ensure_ascii=False, indent=2)}

"""
Gerador de classes de domínio em formato XML
"""
import json
import xml.dom.minidom as md
import xml.etree.ElementTree as ET
import logging
import re
from typing import Dict, Any, List, Union


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("domain_generator")


class DomainGenerator:
    """
    Converte estrutura de dados de classes de domínio para formato XML
    compatível com ferramentas de modelagem como StarUML
    """
    
    def __init__(self):
        """Inicializa o gerador de domínio"""
        logger.info("DomainGenerator inicializado")
    
    def _create_class_element(self, class_data: Dict[str, Any], root):
        """
        Cria elemento XML para uma classe
        
        Args:
            class_data (Dict): Dados da classe
            root: Elemento raiz XML onde adicionar a classe
        
        Returns:
            Element: Elemento XML da classe
        """
        try:
            # Criar elemento de classe
            class_element = ET.SubElement(root, "Class")
            class_element.set("name", class_data["nome"])
            
            # Adicionar atributos
            attributes = ET.SubElement(class_element, "Attributes")
            for attr in class_data.get("atributos", []):
                attr_element = ET.SubElement(attributes, "Attribute")
                attr_element.set("name", attr["nome"])
                attr_element.set("type", attr["tipo"])
            
            return class_element
        except KeyError as e:
            logger.error(f"Campo obrigatório ausente nos dados da classe: {e}")
            logger.debug(f"Dados da classe: {class_data}")
            raise
    
    def _create_relationships(self, classes_data, classes_elements, root):
        """
        Cria elementos XML para os relacionamentos entre classes
        
        Args:
            classes_data (List): Lista de dados das classes
            classes_elements (Dict): Dicionário de elementos XML das classes
            root: Elemento raiz XML onde adicionar os relacionamentos
        """
        try:
            relationships = ET.SubElement(root, "Relationships")
            
            for class_data in classes_data:
                if "relacionamentos" not in class_data:
                    continue
                    
                source_class = class_data["nome"]
                
                for rel in class_data["relacionamentos"]:
                    try:
                        rel_element = ET.SubElement(relationships, "Relationship")
                        rel_element.set("type", rel["tipo"])
                        rel_element.set("source", source_class)
                        rel_element.set("target", rel["alvo"])
                        
                        if "cardinalidade" in rel:
                            rel_element.set("cardinality", rel["cardinalidade"])
                    except KeyError as e:
                        logger.warning(f"Campo obrigatório ausente no relacionamento: {e}. Ignorando este relacionamento.")
                        logger.debug(f"Dados do relacionamento: {rel}")
        except Exception as e:
            logger.error(f"Erro ao criar relacionamentos: {e}")
            raise
    
    def _extract_json_from_text(self, text: str) -> str:
        """
        Extrai conteúdo JSON de um texto que pode conter outros elementos
        
        Args:
            text (str): Texto que pode conter JSON
            
        Returns:
            str: JSON extraído ou texto original se não conseguir extrair JSON
        """
        logger.info("Tentando extrair JSON do texto de resposta")
        
        # Padrão 1: Conteúdo entre ```json e ```
        json_pattern1 = re.search(r'```(?:json)?\s*(.*?)```', text, re.DOTALL)
        
        if json_pattern1:
            logger.info("JSON extraído usando o padrão de código markdown")
            return json_pattern1.group(1).strip()
        
        # Padrão 2: Conteúdo entre { e o último }
        json_start = text.find('{')
        json_end = text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            logger.info("JSON extraído usando o padrão de chaves")
            return text[json_start:json_end].strip()
        
        # Se não conseguir extrair, retornar o texto original
        logger.warning("Não foi possível extrair JSON do texto, retornando texto original")
        return text
    
    def _parse_json_safely(self, json_str: str) -> Union[Dict, None]:
        """
        Tenta fazer o parse de uma string JSON de forma segura
        
        Args:
            json_str (str): String JSON para parse
            
        Returns:
            Dict ou None: Objeto JSON parseado ou None se falhar
        """
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Erro de parse JSON: {e}")
            
            # Tentar limpar a string e tentar novamente
            cleaned_json = self._extract_json_from_text(json_str)
            try:
                return json.loads(cleaned_json)
            except json.JSONDecodeError as e2:
                logger.error(f"Falha ao fazer parse mesmo após limpeza: {e2}")
                return None
    
    def generate_xml(self, domain_data_str: str) -> str:
        """
        Gera XML a partir dos dados de domínio
        
        Args:
            domain_data_str (str): String JSON com dados do domínio
            
        Returns:
            str: Documento XML formatado
        """
        logger.info(f"Iniciando geração de XML a partir de string com {len(domain_data_str)} caracteres")
        
        try:
            # Garantir que temos JSON válido
            domain_data_str = self._extract_json_from_text(domain_data_str)
            
            # Parse JSON string para objeto Python
            domain_data = self._parse_json_safely(domain_data_str)
            
            if domain_data is None:
                return "<e>Não foi possível fazer parse do JSON fornecido</e>"
            
            logger.info("JSON parseado com sucesso")
            
            # Validar estrutura mínima necessária
            if "classes" not in domain_data or not isinstance(domain_data["classes"], list):
                logger.error("JSON não contém a lista de 'classes' necessária")
                return "<e>O JSON fornecido não contém uma lista de classes válida</e>"
                
            # Criar elemento raiz
            root = ET.Element("DomainModel")
            
            # Criar elementos para cada classe
            classes_elements = {}
            for class_data in domain_data.get("classes", []):
                try:
                    class_element = self._create_class_element(class_data, root)
                    classes_elements[class_data["nome"]] = class_element
                except KeyError as e:
                    logger.warning(f"Ignorando classe com dados inválidos: {e}")
            
            # Criar relacionamentos
            try:
                self._create_relationships(domain_data.get("classes", []), classes_elements, root)
            except Exception as e:
                logger.warning(f"Erro ao processar relacionamentos: {e}")
            
            # Converter para string XML
            rough_xml = ET.tostring(root, encoding='utf-8')
            
            # Formatar XML de forma bonita
            try:
                dom = md.parseString(rough_xml)
                pretty_xml = dom.toprettyxml(indent="  ")
                logger.info("XML gerado com sucesso")
                return pretty_xml
            except Exception as e:
                logger.error(f"Erro ao formatar XML: {e}")
                return rough_xml.decode('utf-8')
            
        except json.JSONDecodeError as e:
            logger.error(f"Formato JSON inválido: {e}")
            return "<e>Formato JSON inválido. Verifique se a resposta do modelo está no formato esperado.</e>"
        except Exception as e:
            logger.error(f"Erro na geração do XML: {e}")
            return f"<e>Erro na geração do XML: {str(e)}</e>"
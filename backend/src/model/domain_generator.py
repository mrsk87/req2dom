"""
Gerador de classes de domínio em formato XML
"""
import json
import xml.dom.minidom as md
import xml.etree.ElementTree as ET
import logging
import re
import uuid
from typing import Dict, Any, List, Union


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("domain_generator")


class DomainGenerator:
    """
    Converte estrutura de dados de classes de domínio para formato XML
    compatível com draw.io
    """
    
    def __init__(self):
        """Inicializa o gerador de domínio"""
        logger.info("DomainGenerator inicializado")
        self.next_y_position = 0
        self.class_positions = {}
    
    def _create_drawio_mxfile(self):
        """
        Cria a estrutura base do ficheiro mxfile para draw.io

        Retorna:
            tuple: Elemento raiz mxfile e nó root onde adicionar células
        """
        mxfile = ET.Element("mxfile")
        mxfile.set("host", "req2dom")
        mxfile.set("type", "device")
        mxfile.set("version", "14.9.6")
        mxfile.set("scale", "1")
        
        diagram = ET.SubElement(mxfile, "diagram")
        diagram.set("id", f"R{uuid.uuid4().hex[:8]}")
        diagram.set("name", "Domain Model")
        
        mxGraphModel = ET.SubElement(diagram, "mxGraphModel")
        mxGraphModel.set("dx", "1422")
        mxGraphModel.set("dy", "798")
        mxGraphModel.set("grid", "1")
        mxGraphModel.set("gridSize", "10")
        mxGraphModel.set("guides", "1")
        mxGraphModel.set("tooltips", "1")
        mxGraphModel.set("connect", "1")
        mxGraphModel.set("arrows", "1")
        mxGraphModel.set("fold", "1")
        mxGraphModel.set("page", "1")
        mxGraphModel.set("pageScale", "1")
        mxGraphModel.set("pageWidth", "850")
        mxGraphModel.set("pageHeight", "1100")
        mxGraphModel.set("math", "0")
        mxGraphModel.set("shadow", "0")
        
        root = ET.SubElement(mxGraphModel, "root")
        
        # Adicionar células padrão
        cell0 = ET.SubElement(root, "mxCell")
        cell0.set("id", "0")
        
        cell1 = ET.SubElement(root, "mxCell")
        cell1.set("id", "1")
        cell1.set("parent", "0")
        
        return mxfile, root
    
    def _create_class_element(self, class_data: Dict[str, Any], root):
        """
        Cria elemento XML para uma classe no formato draw.io
        
        Parâmetros:
            class_data (Dict): Dados da classe
            root: Elemento raiz XML onde adicionar a classe
        
        Retorna:
            tuple: ID da classe e nome da classe
        """
        try:
            class_id = f"class_{uuid.uuid4().hex[:8]}"
            class_name = class_data["nome"]
            
            # Calcular posição vertical
            x_pos = 120
            y_pos = self.next_y_position
            self.class_positions[class_name] = (x_pos, y_pos)
            
            # Atualizar próxima posição vertical (para a próxima classe)
            self.next_y_position += 160
            
            # Calcular altura com base no número de atributos (+30px por atributo)
            height = 50 + len(class_data.get("atributos", [])) * 30
            
            # Criar a célula para a classe
            class_cell = ET.SubElement(root, "mxCell")
            class_cell.set("id", class_id)
            class_cell.set("value", class_name)
            class_cell.set("style", "swimlane;fontStyle=0;childLayout=stackLayout;horizontal=1;startSize=30;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;whiteSpace=wrap;html=1;")
            class_cell.set("vertex", "1")
            class_cell.set("parent", "1")
            
            # Adicionar geometria
            geometry = ET.SubElement(class_cell, "mxGeometry")
            geometry.set("x", str(x_pos))
            geometry.set("y", str(y_pos))
            geometry.set("width", "180")
            geometry.set("height", str(height))
            geometry.set("as", "geometry")
            
            # Adicionar atributos como células filhas
            y_offset = 30  # Começa após o cabeçalho da classe
            for attr in class_data.get("atributos", []):
                attr_id = f"attr_{uuid.uuid4().hex[:8]}"
                attr_value = f"{attr['nome']}: {attr['tipo']}"
                
                attr_cell = ET.SubElement(root, "mxCell")
                attr_cell.set("id", attr_id)
                attr_cell.set("value", attr_value)
                attr_cell.set("style", "text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;spacingLeft=4;spacingRight=4;overflow=hidden;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;rotatable=0;whiteSpace=wrap;html=1;")
                attr_cell.set("vertex", "1")
                attr_cell.set("parent", class_id)
                
                # Geometria do atributo
                attr_geo = ET.SubElement(attr_cell, "mxGeometry")
                attr_geo.set("y", str(y_offset))
                attr_geo.set("width", "180")
                attr_geo.set("height", "30")
                attr_geo.set("as", "geometry")
                
                y_offset += 30
            
            return class_id, class_name
            
        except KeyError as e:
            logger.error(f"Campo obrigatório ausente nos dados da classe: {e}")
            logger.debug(f"Dados da classe: {class_data}")
            raise
    
    def _create_relationships(self, classes_data, classes_ids, root):
        """
        Cria elementos XML para os relacionamentos entre classes no formato draw.io.
        Garante que cada relacionamento está separado por entidade e com cardinalidade explícita.
        """
        try:
            for class_data in classes_data:
                if "relacionamentos" not in class_data:
                    continue
                    
                source_class = class_data["nome"]
                
                for rel in class_data["relacionamentos"]:
                    try:
                        target_class = rel["alvo"]
                        
                        # Verificar se as classes de origem e destino existem
                        source_id = None
                        target_id = None
                        
                        for class_id, name in classes_ids.items():
                            if name == source_class:
                                source_id = class_id
                            if name == target_class:
                                target_id = class_id
                        
                        if not source_id or not target_id:
                            logger.warning(f"Classe de origem ou destino não encontrada: {source_class} -> {target_class}")
                            continue
                        
                        # Criar ID único para o relacionamento
                        rel_id = f"rel_{uuid.uuid4().hex[:8]}"
                        
                        # Determinar o estilo com base no tipo de relacionamento
                        style = "endArrow=none;html=1;rounded=0;"  # Associação padrão
                        
                        rel_type = rel["tipo"].lower()
                        if "herança" in rel_type or "extends" in rel_type:
                            style = "endArrow=block;endSize=16;endFill=0;html=1;rounded=0;"  # Herança
                        elif "composição" in rel_type or "composition" in rel_type:
                            style = "endArrow=diamondThin;endFill=1;endSize=14;html=1;rounded=0;"  # Composição
                        elif "agregação" in rel_type or "aggregation" in rel_type:
                            style = "endArrow=diamondThin;endFill=0;endSize=14;html=1;rounded=0;"  # Agregação
                        
                        # Dividir cardinalidade (ex: "1..n" em "1" e "n")
                        cardinality = rel.get("cardinalidade", "0..1")
                        source_card, target_card = self._parse_cardinality(cardinality)
                        
                        # Criar célula de relacionamento (sem texto na linha principal)
                        edge = ET.SubElement(root, "mxCell")
                        edge.set("id", rel_id)
                        edge.set("value", "")  # Sem valor na linha principal
                        edge.set("style", style)
                        edge.set("edge", "1")
                        edge.set("parent", "1")
                        edge.set("source", source_id)
                        edge.set("target", target_id)
                        
                        # Geometria da linha
                        edge_geo = ET.SubElement(edge, "mxGeometry")
                        edge_geo.set("relative", "1")
                        edge_geo.set("as", "geometry")
                        
                        # Criar label para cardinalidade na origem
                        if source_card:
                            self._create_edge_label(root, source_card, rel_id, f"card_source_{rel_id}", -1)
                        
                        # Criar label para cardinalidade no destino  
                        if target_card:
                            self._create_edge_label(root, target_card, rel_id, f"card_target_{rel_id}", 1)
                        
                    except KeyError as e:
                        logger.warning(f"Campo obrigatório ausente no relacionamento: {e}. Ignorando este relacionamento.")
                        logger.debug(f"Dados do relacionamento: {rel}")
        except Exception as e:
            logger.error(f"Erro ao criar relacionamentos: {e}")
            raise
    
    def _extract_json_from_text(self, text: str) -> str:
        """
        Extrai conteúdo JSON de um texto que pode conter outros elementos
        
        Parâmetros:
            text (str): Texto que pode conter JSON
            
        Retorna:
            str: JSON extraído ou texto original se não conseguir extrair JSON
        """
        logger.info("A tentar extrair JSON do texto de resposta")
        
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
        
        Parâmetros:
            json_str (str): String JSON para parse
            
        Retorna:
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
    
    def _parse_cardinality(self, cardinality: str) -> tuple:
        """
        Divide a cardinalidade em duas partes (origem e destino)
        
        Parâmetros:
            cardinality (str): Cardinalidade no formato "1..n", "1..1", "0..n", etc.
            
        Retorna:
            tuple: (cardinalidade_origem, cardinalidade_destino)
        """
        if ".." in cardinality:
            parts = cardinality.split("..")
            return parts[0], parts[1]
        else:
            # Se não tem "..", assumir que é uma cardinalidade simples
            return cardinality, cardinality
    
    def _create_edge_label(self, root, text: str, edge_id: str, label_id: str, position: int):
        """
        Cria um label de cardinalidade ligado à linha de relacionamento
        
        Parâmetros:
            root: Elemento raiz XML onde adicionar o label
            text (str): Texto da cardinalidade
            edge_id (str): ID da linha de relacionamento pai
            label_id (str): ID único do label
            position (int): -1 para próximo da origem, 1 para próximo do destino
        """
        label = ET.SubElement(root, "mxCell")
        label.set("id", label_id)
        label.set("value", text)
        label.set("style", "edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=12;fontColor=#666666;")
        label.set("vertex", "1")
        label.set("connectable", "0")
        label.set("parent", edge_id)  # Ligado à linha de relacionamento
        
        # Geometria do label relativa à linha
        label_geo = ET.SubElement(label, "mxGeometry")
        label_geo.set("x", str(position * 0.8))  # -0.8 para origem, 0.8 para destino
        label_geo.set("relative", "1")
        label_geo.set("as", "geometry")
        
        # Offset para melhorar posicionamento
        label_offset = ET.SubElement(label_geo, "mxPoint")
        label_offset.set("x", "0")
        label_offset.set("y", "-10")  # Ligeiramente acima da linha
        label_offset.set("as", "offset")

    def generate_xml(self, domain_data_str: str) -> str:
        """
        Gera XML no formato draw.io a partir dos dados de domínio
        
        Parâmetros:
            domain_data_str (str): String JSON com dados do domínio
            
        Retorna:
            str: Documento XML formatado para draw.io
        """
        logger.info(f"Iniciando geração de XML para draw.io (entrada com {len(domain_data_str)} caracteres)")
        
        try:
            # Resetar posicionamento para cada nova geração
            self.next_y_position = 50
            self.class_positions = {}
            
            # Extrair e validar JSON
            domain_data_str = self._extract_json_from_text(domain_data_str)
            domain_data = self._parse_json_safely(domain_data_str)
            
            if domain_data is None:
                return "<mxfile><diagram><mxGraphModel><root><mxCell value=\"Erro: Não foi possível fazer parse do JSON fornecido\" vertex=\"1\"/></root></mxGraphModel></diagram></mxfile>"
            
            logger.info("JSON parseado com sucesso")
            
            # Verificar lista de classes
            if "classes" not in domain_data or not isinstance(domain_data["classes"], list):
                logger.error("JSON não contém a lista de 'classes' necessária")
                return "<mxfile><diagram><mxGraphModel><root><mxCell value=\"Erro: JSON sem lista de classes válida\" vertex=\"1\"/></root></mxGraphModel></diagram></mxfile>"
            
            # Criar estrutura base do draw.io
            mxfile, root = self._create_drawio_mxfile()
            
            # Criar elementos para cada classe
            classes_ids = {}
            for class_data in domain_data.get("classes", []):
                try:
                    class_id, class_name = self._create_class_element(class_data, root)
                    classes_ids[class_id] = class_name
                except KeyError as e:
                    logger.warning(f"Ignorando classe com dados inválidos: {e}")
            
            # Criar relacionamentos
            try:
                self._create_relationships(domain_data.get("classes", []), classes_ids, root)
            except Exception as e:
                logger.warning(f"Erro ao processar relacionamentos: {e}")
            
            # Converter para string XML
            rough_xml = ET.tostring(mxfile, encoding='utf-8')
            
            # Formatar XML de forma legível
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
            return "<mxfile><diagram><mxGraphModel><root><mxCell value=\"Erro: Formato JSON inválido\" vertex=\"1\"/></root></mxGraphModel></diagram></mxfile>"
        except Exception as e:
            logger.error(f"Erro na geração do XML: {e}")
            return f"<mxfile><diagram><mxGraphModel><root><mxCell value=\"Erro: {str(e)}\" vertex=\"1\"/></root></mxGraphModel></diagram></mxfile>"

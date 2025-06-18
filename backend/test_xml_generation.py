#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico para verificar se os relacionamentos estão sendo convertidos corretamente do JSON para XML
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from model.spacy_textacy_processor import SpacyTextacyProcessor
from model.domain_generator import DomainGenerator
import json

def test_xml_relationship_generation():
    """Testa se os relacionamentos são preservados durante a conversão JSON → XML"""
    
    print("🔍 TESTE: Conversão de Relacionamentos JSON → XML")
    print("=" * 60)
    
    # Usar o mesmo texto simples que funcionou no teste anterior
    texto_teste = """
    O cliente possui registos no sistema.
    O cliente tem consultas agendadas.
    """
    
    print(f"📝 Texto de teste:")
    print(f"'{texto_teste.strip()}'")
    print()
    
    # Passo 1: Processar com spaCy
    print("🔄 PASSO 1: Processamento spaCy+textacy")
    processor = SpacyTextacyProcessor()
    result = processor.extract_domain_entities(texto_teste)
    
    if "error" in result:
        print(f"❌ Erro no processamento: {result['error']}")
        return
    
    # Parse JSON
    content = json.loads(result['content'])
    classes = content.get('classes', [])
    
    print(f"✅ Classes extraídas: {len(classes)}")
    total_relationships = 0
    for cls in classes:
        rels = cls.get('relacionamentos', [])
        total_relationships += len(rels)
        if rels:
            print(f"  - {cls['nome']}: {len(rels)} relacionamentos")
            for rel in rels:
                print(f"    → {rel['alvo']} ({rel['tipo']}, {rel['cardinalidade']})")
    
    print(f"📊 Total de relacionamentos no JSON: {total_relationships}")
    print()
    
    # Passo 2: Converter para XML
    print("🔄 PASSO 2: Conversão JSON → XML")
    generator = DomainGenerator()
    xml_output = generator.generate_xml(result['content'])
    
    print(f"✅ XML gerado: {len(xml_output)} caracteres")
    
    # Passo 3: Analisar XML para contar relacionamentos
    print("🔄 PASSO 3: Análise do XML gerado")
    
    # Contar elementos de relacionamento no XML
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(xml_output)
        
        # Encontrar todas as células com edge="1" (relacionamentos)
        edges = root.findall(".//mxCell[@edge='1']")
        xml_relationships = len(edges)
        
        print(f"📊 Relacionamentos encontrados no XML: {xml_relationships}")
        
        if xml_relationships > 0:
            print("🔗 Detalhes dos relacionamentos no XML:")
            for i, edge in enumerate(edges, 1):
                source = edge.get('source', 'N/A')
                target = edge.get('target', 'N/A')
                style = edge.get('style', 'N/A')
                print(f"  {i}. {source} → {target}")
                print(f"     Estilo: {style}")
        
        # Verificar consistência
        print()
        if xml_relationships == total_relationships:
            print("✅ CONSISTÊNCIA: Número de relacionamentos preservado!")
        elif xml_relationships == 0 and total_relationships > 0:
            print("❌ PROBLEMA: Relacionamentos perdidos na conversão XML!")
        elif xml_relationships != total_relationships:
            print(f"⚠️  DISCREPÂNCIA: JSON ({total_relationships}) vs XML ({xml_relationships})")
        
    except ET.ParseError as e:
        print(f"❌ Erro ao analisar XML: {e}")
        print("📄 Primeiros 500 caracteres do XML:")
        print(xml_output[:500])
    
    print()
    print("=" * 60)
    print("🎯 CONCLUSÃO:")
    print(f"  - JSON: {total_relationships} relacionamentos")
    print(f"  - XML:  {xml_relationships} relacionamentos" if 'xml_relationships' in locals() else "  - XML:  erro na análise")
    
    # Se quiser ver o XML completo (descomente as linhas abaixo)
    # print("\n📄 XML COMPLETO:")
    # print(xml_output)

if __name__ == "__main__":
    test_xml_relationship_generation()

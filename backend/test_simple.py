#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples para verificar se o processador spaCy está funcionando
e gerando relacionamentos corretamente
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_simple_processing():
    """Teste simples do processador"""
    print("=== TESTE SIMPLES DO PROCESSADOR ===")
    
    try:
        from model.spacy_textacy_processor import SpacyTextacyProcessor
        print("✅ Import do processador bem-sucedido")
        
        processor = SpacyTextacyProcessor()
        print("✅ Processador inicializado")
        
        # Texto simples para teste
        texto = "O médico possui registo de pacientes. O cliente tem consultas agendadas."
        print(f"\n📝 Texto de teste: {texto}")
        
        print("\n🔄 Processando...")
        resultado = processor.extract_domain_entities(texto)
        
        print(f"\n📊 Tipo do resultado: {type(resultado)}")
        print(f"📊 Chaves do resultado: {resultado.keys() if isinstance(resultado, dict) else 'N/A'}")
        
        if "error" in resultado:
            print(f"❌ ERRO: {resultado['error']}")
            return False
        
        if "content" in resultado:
            print(f"\n📄 Conteúdo (primeiros 500 chars):")
            content = resultado["content"]
            print(content[:500] + "..." if len(content) > 500 else content)
            
            # Parse do JSON
            try:
                data = json.loads(content)
                classes = data.get('classes', [])
                
                print(f"\n📋 CLASSES ENCONTRADAS: {len(classes)}")
                for i, classe in enumerate(classes, 1):
                    print(f"  {i}. {classe['nome']}")
                    
                    # Mostrar relacionamentos
                    rels = classe.get('relacionamentos', [])
                    if rels:
                        print(f"     Relacionamentos: {len(rels)}")
                        for rel in rels:
                            print(f"       -> {rel['alvo']} ({rel['tipo']}, {rel['cardinalidade']})")
                    else:
                        print(f"     Relacionamentos: 0")
                
                # Contar total de relacionamentos
                total_rels = sum(len(classe.get('relacionamentos', [])) for classe in classes)
                print(f"\n🔗 TOTAL DE RELACIONAMENTOS: {total_rels}")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao fazer parse do JSON: {e}")
                return False
        else:
            print("❌ Resultado não contém 'content'")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_processing()
    exit(0 if success else 1)

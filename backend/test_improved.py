#!/usr/bin/env python3
"""
Script de teste para o processador SpacyTextacy otimizado
"""

import os
import sys
import json
import traceback

def test_processor():
    print("=== TESTE DO PROCESSADOR NLP OTIMIZADO ===\n")
    
    try:
        from src.model.spacy_textacy_processor import SpacyTextacyProcessor
        print("✅ Importação do processador bem-sucedida")
        
        # Inicializar o processador
        processor = SpacyTextacyProcessor()
        print("✅ Processador inicializado\n")
        
        # Texto de teste (requisitos simples e claros)
        test_text = """
        RF01. O cliente pode fazer pedidos no sistema.
        RF02. Cada pedido contém produtos e informação de pagamento.
        RF03. O administrador gerencia os utilizadores do sistema.
        """
        
        print(f"📝 Texto de teste:\n{test_text}\n")
        print("🔄 Processando...")
        
        # Processar o texto
        result = processor.extract_domain_entities(test_text)
        
        # Verificar o resultado
        if 'content' in result:
            data = json.loads(result['content'])
            classes = data['classes']
            
            print(f"\n📋 CLASSES ENCONTRADAS: {len(classes)}")
            
            for i, cls in enumerate(classes, 1):
                print(f"\n{i}. {cls['nome']}")
                
                print("   Atributos:")
                for attr in cls['atributos']:
                    print(f"   - {attr['nome']}: {attr['tipo']}")
                
                print("\n   Relacionamentos:")
                if cls['relacionamentos']:
                    for rel in cls['relacionamentos']:
                        print(f"   - {rel['tipo']} → {rel['alvo']} ({rel['cardinalidade']})")
                else:
                    print("   - Nenhum relacionamento")
            
            # Estatísticas
            total_attrs = sum(len(cls['atributos']) for cls in classes)
            total_rels = sum(len(cls['relacionamentos']) for cls in classes)
            
            print(f"\n📊 ESTATÍSTICAS:")
            print(f"  - Classes: {len(classes)}")
            print(f"  - Total de atributos: {total_attrs}")
            print(f"  - Total de relacionamentos: {total_rels}")
            print(f"  - Média de atributos por classe: {total_attrs/len(classes) if classes else 0:.1f}")
            
            return True
        else:
            error = result.get('error', 'Erro desconhecido')
            print(f"\n❌ ERRO: {error}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_processor()
    sys.exit(0 if success else 1)

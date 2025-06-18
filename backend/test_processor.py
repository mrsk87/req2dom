#!/usr/bin/env python3
"""
Script de teste para o processador spaCy+textacy
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from model.spacy_textacy_processor import SpacyTextacyProcessor

def test_portuguese_processing():
    """Testa o processamento de texto em português"""
    print("=== Teste do Processador spaCy+textacy ===")
    
    try:
        # Inicializar o processador
        processor = SpacyTextacyProcessor()
        print("✓ Processador inicializado com sucesso")
        
        # Texto de teste em português
        test_text = """
        O sistema deve permitir que o utilizador faça marcações de consultas.
        O cliente pode visualizar o histórico de consultas e cancelar marcações.
        O funcionário pode gerir os agendamentos e confirmar as consultas.
        O veterinário deve ter acesso aos registos médicos dos animais.
        O sistema deve gerar relatórios de facturação mensais.
        """
        
        print(f"\n📝 Texto de teste:")
        print(test_text.strip())
        
        # Processar o texto
        print("\n🔄 Processando...")
        result = processor.extract_domain_entities(test_text)
        
        if "error" in result:
            print(f"❌ Erro: {result['error']}")
            return False
        
        print("\n✅ Resultado do processamento:")
        print(f"📋 Conteúdo: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_portuguese_processing()
    exit(0 if success else 1)

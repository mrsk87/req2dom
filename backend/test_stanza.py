"""
Teste do processador Stanza para português
"""
import sys
import os
import json

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model.stanza_processor import StanzaProcessor

def test_stanza():
    """
    Testa o processador Stanza com alguns exemplos em português de Portugal
    """
    processor = StanzaProcessor()
    
    # Exemplo 1: Sistema de Gestão de Biblioteca
    print("\n=== TESTE 1: Sistema de Biblioteca ===")
    text1 = """
    O sistema de biblioteca deve permitir que os utilizadores requisitem livros. 
    Cada livro tem um título, autor e código ISBN. 
    Os utilizadores devem ser registados no sistema com nome, email e endereço. 
    Um utilizador pode ter várias requisições ativas.
    """
    
    result1 = processor.extract_domain_entities(text1)
    print_result(result1)
    
    # Exemplo 2: Sistema de Gestão de Encomendas
    print("\n=== TESTE 2: Sistema de Encomendas ===")
    text2 = """
    RF01: O cliente deve poder registar-se no sistema fornecendo nome, email e telefone.
    RF02: O cliente pode adicionar produtos ao carrinho de compras.
    RF03: Os produtos têm nome, descrição, preço e quantidade em stock.
    RF04: O sistema deve permitir que o cliente finalize a compra gerando uma encomenda.
    RF05: Cada encomenda tem um código único, data, estado e valor total.
    """
    
    result2 = processor.extract_domain_entities(text2)
    print_result(result2)
    
    # Exemplo 3: Sistema de Gestão Hospitalar
    print("\n=== TESTE 3: Sistema Hospitalar ===")
    text3 = """
    O sistema hospitalar deve gerir pacientes e médicos.
    Os pacientes são registados com nome, número utente e data de nascimento.
    Os médicos possuem especialidade e número de cédula profissional.
    As consultas são agendadas com data, hora e têm um médico e um paciente associados.
    """
    
    result3 = processor.extract_domain_entities(text3)
    print_result(result3)
    
    print("\nTestes do processador Stanza concluídos.")

def print_result(result):
    """Imprime o resultado de forma formatada"""
    if "error" in result:
        print(f"ERRO: {result['error']}")
    else:
        try:
            content = json.loads(result["content"])
            print(f"Entidades encontradas: {len(content.get('classes', []))}")
            
            for cls in content.get("classes", []):
                print(f"\nCLASSE: {cls['nome']}")
                
                print("  ATRIBUTOS:")
                for attr in cls.get("atributos", []):
                    print(f"    - {attr['nome']}: {attr['tipo']}")
                    
                print("  RELACIONAMENTOS:")
                for rel in cls.get("relacionamentos", []):
                    print(f"    - {rel['tipo']} -> {rel['alvo']} ({rel['cardinalidade']})")
                    
        except Exception as e:
            print(f"Erro ao processar resultado: {e}")
            print(f"Conteúdo bruto: {result}")

if __name__ == "__main__":
    test_stanza()

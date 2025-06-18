"""
Teste comparativo entre processadores spaCy e Stanza para português
"""
import sys
import os
import json
import time

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model.stanza_processor import StanzaProcessor
from src.model.spacy_textacy_processor import SpacyTextacyProcessor

def test_benchmark():
    """
    Compara o desempenho e resultados entre Stanza e spaCy
    """
    spacy_processor = SpacyTextacyProcessor()
    stanza_processor = StanzaProcessor()
    
    test_cases = [
        {
            "name": "Biblioteca",
            "text": """
            O sistema de biblioteca deve permitir que os utilizadores requisitem livros. 
            Cada livro tem um título, autor e código ISBN. 
            Os utilizadores devem ser registados no sistema com nome, email e endereço. 
            Um utilizador pode ter várias requisições ativas.
            """
        },
        {
            "name": "Encomendas",
            "text": """
            RF01: O cliente deve poder registar-se no sistema fornecendo nome, email e telefone.
            RF02: O cliente pode adicionar produtos ao carrinho de compras.
            RF03: Os produtos têm nome, descrição, preço e quantidade em stock.
            RF04: O sistema deve permitir que o cliente finalize a compra gerando uma encomenda.
            RF05: Cada encomenda tem um código único, data, estado e valor total.
            """
        },
        {
            "name": "Hospital",
            "text": """
            O sistema hospitalar deve gerir pacientes e médicos.
            Os pacientes são registados com nome, número utente e data de nascimento.
            Os médicos possuem especialidade e número de cédula profissional.
            As consultas são agendadas com data, hora e têm um médico e um paciente associados.
            """
        }
    ]
    
    print("\n=== COMPARATIVO STANZA vs SPACY ===")
    for test_case in test_cases:
        print(f"\n--- TESTE: {test_case['name']} ---")
        text = test_case['text']
        
        # Teste com spaCy+textacy
        start_spacy = time.time()
        spacy_result = spacy_processor.extract_domain_entities(text)
        spacy_time = time.time() - start_spacy
        
        # Teste com Stanza
        start_stanza = time.time()
        stanza_result = stanza_processor.extract_domain_entities(text)
        stanza_time = time.time() - start_stanza
        
        # Comparar resultados
        print(f"spaCy: {spacy_time:.2f}s, Stanza: {stanza_time:.2f}s")
        
        spacy_classes = json.loads(spacy_result["content"]).get("classes", []) if "content" in spacy_result else []
        stanza_classes = json.loads(stanza_result["content"]).get("classes", []) if "content" in stanza_result else []
        
        print(f"Classes encontradas - spaCy: {len(spacy_classes)}, Stanza: {len(stanza_classes)}")
        
        # Comparar classes encontradas
        print("\nClasses spaCy:", ", ".join([cls["nome"] for cls in spacy_classes]))
        print("Classes Stanza:", ", ".join([cls["nome"] for cls in stanza_classes]))
        
        # Comparar atributos da primeira classe (se existir)
        if spacy_classes and stanza_classes:
            spacy_attrs = spacy_classes[0].get("atributos", [])
            stanza_attrs = stanza_classes[0].get("atributos", [])
            
            print(f"\nAtributos para {spacy_classes[0]['nome']} (spaCy):", 
                  ", ".join([f"{attr['nome']}: {attr['tipo']}" for attr in spacy_attrs]))
            print(f"Atributos para {stanza_classes[0]['nome']} (Stanza):", 
                  ", ".join([f"{attr['nome']}: {attr['tipo']}" for attr in stanza_attrs]))

if __name__ == "__main__":
    test_benchmark()

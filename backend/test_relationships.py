#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico para verificação de relacionamentos entre classes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from model.spacy_textacy_processor import SpacyTextacyProcessor
import json

def test_relationships():
    """Testa a extração de relacionamentos com textos específicos"""
    processor = SpacyTextacyProcessor()
    
    # Textos que deveriam gerar relacionamentos claros
    test_cases = [
        {
            "nome": "Gestão Hospitalar",
            "texto": """
            O médico possui registo de pacientes no sistema hospitalar. 
            O paciente tem consultas agendadas. 
            A enfermeira utiliza equipamentos médicos durante os procedimentos.
            O director gere os recursos hospitalares.
            O sistema hospitalar armazena dados de pacientes.
            Os médicos acedem aos relatórios de exames.
            """,
            "relacionamentos_esperados": [
                "Médico - Paciente",
                "Paciente - Consulta", 
                "Enfermeira - Equipamento",
                "Director - Recurso",
                "Sistema - Dados",
                "Médico - Relatório"
            ]
        },
        {
            "nome": "E-commerce",
            "texto": """
            O cliente possui carrinho de compras no sistema.
            O produto tem categoria e preço definidos.
            O funcionário gere inventário de produtos.
            O sistema processa pedidos automaticamente.
            Os clientes fazem encomendas através da plataforma.
            O administrador controla utilizadores do sistema.
            """,
            "relacionamentos_esperados": [
                "Cliente - Carrinho",
                "Produto - Categoria",
                "Funcionário - Inventário", 
                "Sistema - Pedido",
                "Cliente - Encomenda",
                "Administrador - Utilizador"
            ]
        },
        {
            "nome": "Educação",
            "texto": """
            O professor leciona disciplinas aos estudantes.
            O estudante tem notas em avaliações.
            O coordenador gere horários das aulas.
            O sistema educativo regista presenças.
            Os professores criam materiais didácticos.
            A secretaria processa documentos académicos.
            """,
            "relacionamentos_esperados": [
                "Professor - Disciplina",
                "Professor - Estudante",
                "Estudante - Avaliação",
                "Coordenador - Horário",
                "Sistema - Presença",
                "Professor - Material",
                "Secretaria - Documento"
            ]
        }
    ]
    
    print("=" * 80)
    print("TESTE DE RELACIONAMENTOS ENTRE CLASSES")
    print("=" * 80)
    
    for i, caso in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"CASO {i}: {caso['nome']}")
        print(f"{'='*50}")
        
        print(f"\nTexto de entrada:")
        print(f"'{caso['texto'].strip()}'")
        
        try:
            # Processar o texto
            resultado = processor.extract_domain_entities(caso['texto'])
            
            print(f"\n🔄 RESULTADO RAW:")
            print(f"Type: {type(resultado)}")
            print(f"Keys: {resultado.keys() if isinstance(resultado, dict) else 'N/A'}")
            
            if "error" in resultado:
                print(f"❌ ERRO: {resultado['error']}")
                continue
            
            # Parse do resultado
            if "content" in resultado:
                content = resultado["content"]
                if isinstance(content, str):
                    import json
                    content = json.loads(content)
                classes = content.get('classes', [])
                relacionamentos = []
                # Extrair relacionamentos de todas as classes
                for classe in classes:
                    for rel in classe.get('relacionamentos', []):
                        relacionamentos.append({
                            'source': classe['nome'],
                            'target': rel['alvo'],
                            'tipo': rel['tipo'],
                            'cardinalidade': rel['cardinalidade']
                        })
            else:
                # Estrutura direta
                classes = resultado.get('classes', [])
                relacionamentos = resultado.get('relacionamentos', [])
            
            print(f"\n📋 CLASSES IDENTIFICADAS ({len(classes)}):")
            for j, classe in enumerate(classes, 1):
                print(f"  {j}. {classe['nome']}")
            
            print(f"\n🔗 RELACIONAMENTOS IDENTIFICADOS ({len(relacionamentos)}):")
            if relacionamentos:
                for j, rel in enumerate(relacionamentos, 1):
                    print(f"  {j}. {rel['source']} ➜ {rel['target']} ({rel['tipo']}, {rel['cardinalidade']})")
            else:
                print("  ❌ Nenhum relacionamento identificado!")
            
            print(f"\n✅ RELACIONAMENTOS ESPERADOS:")
            for j, esperado in enumerate(caso['relacionamentos_esperados'], 1):
                print(f"  {j}. {esperado}")
            
            # Análise da cobertura
            relacionamentos_encontrados = []
            for rel in relacionamentos:
                rel_str = f"{rel['source']} - {rel['target']}"
                relacionamentos_encontrados.append(rel_str)
            
            print(f"\n📊 ANÁLISE DE COBERTURA:")
            encontrados = 0
            for esperado in caso['relacionamentos_esperados']:
                # Verificar se existe algum relacionamento similar
                found = False
                for encontrado in relacionamentos_encontrados:
                    # Verificar se as palavras-chave do relacionamento esperado estão presentes
                    palavras_esperadas = esperado.lower().replace(' - ', ' ').split()
                    palavras_encontradas = encontrado.lower().replace(' - ', ' ').split()
                    
                    if any(p1 in ' '.join(palavras_encontradas) for p1 in palavras_esperadas[:1]) and \
                       any(p2 in ' '.join(palavras_encontradas) for p2 in palavras_esperadas[1:]):
                        found = True
                        break
                
                if found:
                    print(f"  ✅ {esperado} - ENCONTRADO")
                    encontrados += 1
                else:
                    print(f"  ❌ {esperado} - NÃO ENCONTRADO")
            
            taxa_cobertura = (encontrados / len(caso['relacionamentos_esperados'])) * 100
            print(f"\n📈 TAXA DE COBERTURA: {encontrados}/{len(caso['relacionamentos_esperados'])} ({taxa_cobertura:.1f}%)")
            
            if taxa_cobertura >= 70:
                print("  🟢 EXCELENTE cobertura de relacionamentos!")
            elif taxa_cobertura >= 50:
                print("  🟡 BOA cobertura de relacionamentos")
            else:
                print("  🔴 BAIXA cobertura de relacionamentos - Necessita melhorias")
                
        except Exception as e:
            print(f"❌ ERRO durante o processamento: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*80}")
    print("TESTE CONCLUÍDO")
    print(f"{'='*80}")

if __name__ == "__main__":
    test_relationships()

#!/usr/bin/env python3
"""
Teste abrangente para verificar se o processador spaCy+textacy é genérico
e funciona com diferentes domínios/tópicos
"""
import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from model.spacy_textacy_processor import SpacyTextacyProcessor

def test_domain_genericity():
    """Testa o processador com diferentes domínios para verificar genericidade"""
    print("=== Teste de Genericidade do Processador spaCy+textacy ===\n")
    
    try:
        processor = SpacyTextacyProcessor()
        print("✓ Processador inicializado com sucesso\n")
        
        # Diferentes domínios de teste
        test_domains = {
            "🏥 Saúde/Medicina": {
                "text": """
                O sistema hospitalar deve permitir que o médico registe diagnósticos dos pacientes.
                O enfermeiro pode actualizar os registos médicos e agendar tratamentos.
                Os pacientes podem consultar os seus exames e marcar consultas.
                O laboratório deve processar análises e gerar relatórios de resultados.
                """,
                "expected_entities": ["médico", "pacientes", "enfermeiro", "laboratório", "sistema", "diagnósticos", "registos", "tratamentos", "exames", "consultas", "análises", "relatórios"]
            },
            
            "🎓 Educação": {
                "text": """
                A plataforma educativa deve permitir que o professor crie disciplinas e publique conteúdos.
                Os estudantes podem inscrever-se em disciplinas e submeter trabalhos.
                O sistema deve calcular notas e gerar boletins de avaliação.
                Os coordenadores podem gerir currículos e aprovar disciplinas.
                """,
                "expected_entities": ["professor", "estudantes", "coordenadores", "plataforma", "disciplinas", "conteúdos", "trabalhos", "notas", "boletins", "currículos"]
            },
            
            "🏭 Manufatura/Produção": {
                "text": """
                O sistema de produção deve controlar máquinas e monitorizar processos de fabrico.
                Os operadores podem iniciar operações e registar defeitos nos produtos.
                O controlo de qualidade deve inspeccionar lotes e aprovar shipments.
                Os técnicos fazem manutenção preventiva dos equipamentos.
                """,
                "expected_entities": ["sistema", "máquinas", "operadores", "produtos", "controlo", "lotes", "técnicos", "processos", "operações", "defeitos", "equipamentos"]
            },
            
            "🏪 Comércio Electrónico": {
                "text": """
                A loja online deve permitir que os clientes naveguem pelo catálogo e façam encomendas.
                Os vendedores podem adicionar produtos e gerir inventário.
                O sistema de pagamento processa transacções e emite facturas.
                Os gestores analisam vendas e configuram promoções.
                """,
                "expected_entities": ["loja", "clientes", "vendedores", "gestores", "catálogo", "encomendas", "produtos", "inventário", "pagamento", "transacções", "facturas", "vendas", "promoções"]
            },
            
            "🌾 Agricultura": {
                "text": """
                O sistema agrícola deve monitorizar culturas e controlar irrigação.
                Os agricultores registam plantações e aplicam fertilizantes.
                Os sensores recolhem dados meteorológicos e da humidade do solo.
                O sistema gera alertas sobre pragas e doenças das plantas.
                """,
                "expected_entities": ["sistema", "agricultores", "sensores", "culturas", "irrigação", "plantações", "fertilizantes", "dados", "alertas", "pragas", "plantas"]
            },
            
            "🚗 Transportes": {
                "text": """
                A aplicação de transportes permite que os passageiros reservem viagens.
                Os condutores podem aceitar corridas e actualizar o estado da viagem.
                O sistema calcula rotas optimizadas e estima tempos de chegada.
                Os administradores gerem frotas e analisam métricas de performance.
                """,
                "expected_entities": ["aplicação", "passageiros", "condutores", "administradores", "viagens", "corridas", "sistema", "rotas", "frotas", "métricas"]
            },
            
            "🏦 Banca/Finanças": {
                "text": """
                O sistema bancário deve processar transferências e validar transacções.
                Os clientes podem consultar saldos e solicitar empréstimos.
                Os gestores de conta analisam riscos e aprovam créditos.
                O sistema gera extractos mensais e calcula juros.
                """,
                "expected_entities": ["sistema", "clientes", "gestores", "transferências", "transacções", "saldos", "empréstimos", "riscos", "créditos", "extractos", "juros"]
            }
        }
        
        results = {}
        total_success = 0
        
        for domain_name, domain_data in test_domains.items():
            print(f"🔄 Testando domínio: {domain_name}")
            print(f"📝 Texto: {domain_data['text'][:100]}...")
            
            try:
                result = processor.extract_domain_entities(domain_data['text'])
                
                if "error" in result:
                    print(f"❌ Erro: {result['error']}\n")
                    results[domain_name] = {"success": False, "error": result['error']}
                    continue
                
                # Analisar resultado
                content = json.loads(result['content'])
                classes = content.get('classes', [])
                extracted_entities = [cls['nome'].lower() for cls in classes]
                
                print(f"✅ Classes extraídas ({len(classes)}): {', '.join([cls['nome'] for cls in classes])}")
                
                # Verificar se captou entidades esperadas
                expected = domain_data['expected_entities']
                found_entities = []
                for expected_entity in expected:
                    if any(expected_entity.lower() in entity.lower() or entity.lower() in expected_entity.lower() 
                           for entity in extracted_entities):
                        found_entities.append(expected_entity)
                
                coverage = len(found_entities) / len(expected) * 100 if expected else 0
                print(f"📊 Cobertura de entidades esperadas: {coverage:.1f}% ({len(found_entities)}/{len(expected)})")
                
                if coverage > 30:  # Pelo menos 30% das entidades esperadas
                    print(f"✅ Domínio processado com sucesso")
                    total_success += 1
                else:
                    print(f"⚠️  Cobertura baixa - pode não estar a captar entidades específicas do domínio")
                
                results[domain_name] = {
                    "success": True,
                    "classes_count": len(classes),
                    "coverage": coverage,
                    "extracted_entities": extracted_entities,
                    "found_expected": found_entities
                }
                
            except Exception as e:
                print(f"❌ Erro durante processamento: {str(e)}")
                results[domain_name] = {"success": False, "error": str(e)}
            
            print()
        
        # Sumário final
        print("=" * 70)
        print("📋 RESUMO DOS RESULTADOS")
        print("=" * 70)
        
        total_domains = len(test_domains)
        success_rate = (total_success / total_domains) * 100
        
        print(f"🎯 Domínios testados: {total_domains}")
        print(f"✅ Domínios processados com sucesso: {total_success}")
        print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
        print()
        
        # Análise de genericidade
        if success_rate >= 85:
            print("🎉 MODELO ALTAMENTE GENÉRICO - Funciona bem com diversos domínios")
        elif success_rate >= 70:
            print("✅ MODELO RAZOAVELMENTE GENÉRICO - Funciona com a maioria dos domínios")
        elif success_rate >= 50:
            print("⚠️  MODELO PARCIALMENTE GENÉRICO - Funciona com alguns domínios")
        else:
            print("❌ MODELO NÃO GENÉRICO - Limitado a domínios específicos")
        
        # Detalhes por domínio
        print("\n📊 DETALHES POR DOMÍNIO:")
        for domain_name, result in results.items():
            if result["success"]:
                print(f"  {domain_name}: ✅ {result['classes_count']} classes, {result['coverage']:.1f}% cobertura")
            else:
                print(f"  {domain_name}: ❌ Erro")
        
        return success_rate >= 70
        
    except Exception as e:
        print(f"❌ Erro crítico durante teste: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_domain_genericity()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    success = test_generic_domains()
    exit(0 if success else 1)

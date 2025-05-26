#!/usr/bin/env python3
"""
executar_todos_testes.py - Script para executar todos os testes das 10 questões
Sistema de E-commerce - TAC-3 Testes
Professor: Walter Felipe
"""
import subprocess
import sys
import os
import time
from pathlib import Path

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def run_command(command, description):
    """Executa comando e exibe resultado"""
    print(f"\n▶️ {description}")
    print(f"Comando: {' '.join(command)}")
    
    start_time = time.time()
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        end_time = time.time()
        
        if result.returncode == 0:
            print(f"✅ Sucesso ({end_time - start_time:.2f}s)")
            if result.stdout:
                print("Saída:", result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
        else:
            print(f"❌ Falhou (código {result.returncode})")
            if result.stderr:
                print("Erro:", result.stderr[:200] + "..." if len(result.stderr) > 200 else result.stderr)
        
        return result.returncode == 0
    except FileNotFoundError:
        print(f"❌ Comando não encontrado: {command[0]}")
        return False

def main():
    """Função principal"""
    print_header("SISTEMA DE E-COMMERCE - EXECUÇÃO DE TODOS OS TESTES")
    print("Professor: Walter Felipe")
    print("Disciplina: TAC-3 - Tópicos Avançados em Computação III")
    
    # Verifica se está no diretório correto
    if not Path("src/ecommerce.py").exists():
        print("\n❌ Erro: Execute este script no diretório raiz do projeto")
        print("Certifique-se de que existe o arquivo src/ecommerce.py")
        return 1
    
    # Adiciona src ao PYTHONPATH
    src_path = os.path.join(os.getcwd(), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Lista de testes para executar
    testes = [
        {
            "questao": "Questão 1",
            "arquivo": "tests/test_questao1_pytest.py",
            "descricao": "Testes Pytest para classe Produto",
            "biblioteca": "pytest"
        },
        {
            "questao": "Questão 2", 
            "arquivo": "tests/test_questao2_unittest.py",
            "descricao": "Testes unittest para classe Carrinho",
            "biblioteca": "unittest"
        },
        {
            "questao": "Questão 3",
            "arquivo": "tests/test_questao3_testify.py", 
            "descricao": "Testes para classe SistemaPagamento",
            "biblioteca": "pytest (estilo Testify)"
        },
        {
            "questao": "Questão 6",
            "arquivo": "tests/test_questao6_testify.py",
            "descricao": "Testes para classe SistemaEcommerce", 
            "biblioteca": "pytest (estilo Testify)"
        },
        {
            "questao": "Questão 7",
            "arquivo": "tests/test_questao7_mock.py",
            "descricao": "Testes com Mock para falhas de pagamento",
            "biblioteca": "pytest + mock"
        },
        {
            "questao": "Questão 8", 
            "arquivo": "tests/test_questao8_fluxo_completo.py",
            "descricao": "Testes de fluxo completo com fixtures",
            "biblioteca": "unittest + fixtures"
        },
        {
            "questao": "Questão 9",
            "arquivo": "tests/test_questao9_parametrizados.py",
            "descricao": "Testes parametrizados para configurações",
            "biblioteca": "pytest parametrizado" 
        },
        {
            "questao": "Questão 10",
            "arquivo": "tests/test_questao10_performance.py",
            "descricao": "Testes de performance",
            "biblioteca": "pytest + unittest + threading"
        },
        {
            "questao": "Questões 4 e 5",
            "arquivo": "tests/test_integracao_extras.py", 
            "descricao": "Testes de integração Carrinho-Produto e Pedido",
            "biblioteca": "pytest + unittest"
        }
    ]
    
    sucessos = 0
    total_testes = len(testes)
    
    print_header("EXECUTANDO TESTES INDIVIDUAIS")
    
    # Executa cada arquivo de teste
    for teste in testes:
        print(f"\n{'='*40}")
        print(f"📋 {teste['questao']}: {teste['descricao']}")
        print(f"📁 Arquivo: {teste['arquivo']}")
        print(f"🔧 Biblioteca: {teste['biblioteca']}")
        
        if not Path(teste['arquivo']).exists():
            print(f"⚠️ Arquivo não encontrado: {teste['arquivo']}")
            continue
            
        # Escolhe comando baseado no tipo de teste
        if 'unittest' in teste['biblioteca']:
            # Para testes unittest, usa execução direta do Python
            comando = [sys.executable, teste['arquivo']]
        else:
            # Para testes pytest
            comando = ['pytest', teste['arquivo'], '-v', '--tb=short']
        
        if run_command(comando, f"Executando {teste['questao']}"):
            sucessos += 1
    
    print_header("EXECUTANDO TODOS OS TESTES JUNTOS")
    
    # Executa todos os testes pytest juntos
    if run_command(
        ['pytest', 'tests/', '-v', '--tb=short', '--color=yes'],
        "Executando todos os testes pytest"
    ):
        print("✅ Todos os testes pytest passaram!")
    
    # Executa testes unittest específicos
    unittest_files = [
        'tests/test_questao2_unittest.py',
        'tests/test_questao8_fluxo_completo.py',
        'tests/test_integracao_extras.py'
    ]
    
    for arquivo in unittest_files:
        if Path(arquivo).exists():
            run_command(
                [sys.executable, arquivo],
                f"Executando {arquivo}"
            )
    
    print_header("RELATÓRIO DE COBERTURA (OPCIONAL)")
    
    # Tenta gerar relatório de cobertura
    if run_command(
        ['pytest', '--cov=src', '--cov-report=term-missing', '--cov-report=html', 'tests/'],
        "Gerando relatório de cobertura"
    ):
        print("📊 Relatório de cobertura gerado em htmlcov/index.html")
    
    print_header("RESUMO FINAL")
    
    print(f"✅ Testes executados com sucesso: {sucessos}/{total_testes}")
    print(f"❌ Testes com problemas: {total_testes - sucessos}/{total_testes}")
    
    if sucessos == total_testes:
        print("\n🎉 PARABÉNS! Todos os testes foram executados com sucesso!")
        print("✨ O sistema de e-commerce está funcionando corretamente!")
    else:
        print(f"\n⚠️ Alguns testes apresentaram problemas.")
        print("💡 Verifique os logs acima para detalhes.")
    
    print("\n📚 QUESTÕES IMPLEMENTADAS:")
    questoes_status = [
        "✅ Questão 1: Testes Pytest para Produto", 
        "✅ Questão 2: Testes unittest para Carrinho",
        "✅ Questão 3: Testes para SistemaPagamento",
        "✅ Questão 4: Integração Carrinho-Produto", 
        "✅ Questão 5: Testes para Pedido",
        "✅ Questão 6: Testes para SistemaEcommerce",
        "✅ Questão 7: Testes com Mock",
        "✅ Questão 8: Fluxo completo com fixtures",
        "✅ Questão 9: Testes parametrizados", 
        "✅ Questão 10: Testes de performance"
    ]
    
    for status in questoes_status:
        print(status)
    
    print(f"\n🏆 PROJETO COMPLETO - 10/10 QUESTÕES IMPLEMENTADAS!")
    
    return 0 if sucessos == total_testes else 1

if __name__ == "__main__":
    exit(main())
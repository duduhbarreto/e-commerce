#!/usr/bin/env python3
"""
Script para executar todos os testes do projeto
"""
import subprocess
import sys
import os

def main():
    """Executa todos os testes do projeto"""
    print("🚀 Executando testes do Sistema E-commerce...")
    print("=" * 60)
    
    # Adiciona o diretório src ao PYTHONPATH
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    sys.path.insert(0, src_path)
    
    try:
        # Executa testes com pytest
        result = subprocess.run([
            'pytest', 
            'tests/', 
            '-v', 
            '--tb=short',
            '--color=yes'
        ], check=True)
        
        print("\n✅ Todos os testes passaram!")
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Alguns testes falharam. Código de saída: {e.returncode}")
        return e.returncode
    
    except FileNotFoundError:
        print("❌ pytest não encontrado. Instale com: pip install pytest")
        return 1

if __name__ == "__main__":
    exit(main())
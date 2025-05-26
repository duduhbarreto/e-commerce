# setup_e_execucao.py - Instruções para configurar e executar o projeto

"""
========================================================================
SISTEMA DE E-COMMERCE - ATIVIDADE TAC-3 TESTES
Professor: Walter Felipe
========================================================================

ESTRUTURA DO PROJETO:
├── ecommerce.py                 # Classes principais do sistema
├── test_questao1_pytest.py     # Questão 1: Testes Pytest para Produto  
├── test_questao2_unittest.py   # Questão 2: Testes unittest para Carrinho
├── test_questao3_testify.py    # Questão 3: Testes para SistemaPagamento
├── test_integracao_extras.py   # Questões 4, 5, 7, 10: Testes extras
└── requirements.txt            # Dependências do projeto

INSTALAÇÃO E CONFIGURAÇÃO:
========================================================================

1. Criar ambiente virtual:
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows

2. Instalar dependências:
   pip install pytest

3. Criar arquivo requirements.txt:
   pytest>=7.0.0

EXECUÇÃO DOS TESTES:
========================================================================

# Executar todos os testes com pytest:
pytest -v

# Executar questão específica:
pytest test_questao1_pytest.py -v
pytest test_questao2_unittest.py -v  
pytest test_questao3_testify.py -v

# Executar testes unittest diretamente:
python test_questao2_unittest.py
python test_integracao_extras.py

# Executar com relatório de cobertura:
pip install pytest-cov
pytest --cov=ecommerce --cov-report=html

QUESTÕES IMPLEMENTADAS:
========================================================================

✅ Questão 1: Testes Pytest para Produto
   - Verificação da criação de produto
   - Verificação da disponibilidade de estoque  
   - Verificação da redução de estoque

✅ Questão 2: Testes unittest para Carrinho
   - Adição de itens no carrinho
   - Remoção de itens do carrinho
   - Cálculo do valor total do carrinho
   - Comportamento com produto sem estoque

✅ Questão 3: Testes para SistemaPagamento  
   - Cálculo cartão de crédito à vista
   - Cálculo cartão de crédito parcelado
   - Cálculo pagamento PIX com desconto
   - Cálculo do valor das parcelas

✅ Questão 4: Testes integração Carrinho-Produto
   - Atualização valor total ao adicionar produtos
   - Impedimento adição produtos sem estoque
   - Remoção parcial de produtos

✅ Questão 5: Testes para Pedido
   - Transição entre estados do pedido
   - Processamento pagamento diferentes métodos
   - Restrições de transição de estado

✅ Questão 7: Exemplo testes com Mock
   - Simulação falha autorização cartão
   - Verificação estado correto após falhas

✅ Questão 10: Exemplo testes performance
   - Tempo adição múltiplos produtos

PRINCÍPIOS APLICADOS:
========================================================================

🔹 Clean Code:
   - Nomes descritivos para classes e métodos
   - Métodos pequenos e com responsabilidade única
   - Comentários explicativos quando necessário

🔹 SOLID:
   - Single Responsibility: Cada classe tem uma responsabilidade
   - Open/Closed: Classes abertas para extensão
   - Dependency Inversion: Uso de abstrações (Enums)

🔹 Tratamento de Exceções:
   - Exceções customizadas (EstoqueInsuficienteError)
   - Validações de negócio implementadas

🔹 Testes Abrangentes:
   - Testes unitários para cada classe
   - Testes de integração entre componentes
   - Testes de borda e casos de erro
   - Uso de mocks para simulação de falhas

EXEMPLO DE USO DO SISTEMA:
========================================================================
"""

# Exemplo prático de uso do sistema
from ecommerce import *

def exemplo_uso_completo():
    """Demonstra o uso completo do sistema"""
    # 1. Criar sistema
    sistema = SistemaEcommerce()
    
    # 2. Adicionar produtos
    produto1 = Produto(1, "Notebook", "Dell Inspiron", 2500.00, 10, "Eletrônicos")
    produto2 = Produto(2, "Mouse", "Mouse sem fio", 50.00, 20, "Eletrônicos")
    
    sistema.adicionar_produto(produto1)
    sistema.adicionar_produto(produto2)
    
    # 3. Criar carrinho
    carrinho = Carrinho()
    carrinho.adicionar_item(produto1, 1)
    carrinho.adicionar_item(produto2, 2)
    
    print(f"Total do carrinho: R$ {carrinho.calcular_valor_total()}")
    
    # 4. Criar pedido
    id_pedido = sistema.criar_pedido(
        carrinho, 
        MetodoPagamento.PIX, 
        "Rua das Flores, 123"
    )
    
    print(f"Pedido criado: {id_pedido}")
    
    # 5. Consultar pedido
    pedido = sistema.obter_pedido(id_pedido)
    print(f"Status do pedido: {pedido.status.value}")

if __name__ == "__main__":
    exemplo_uso_completo()

"""
OBSERVAÇÕES IMPORTANTES:
========================================================================

1. O código está simplificado mas funcional, cobrindo os requisitos básicos
2. Para implementação completa, adicionar:
   - Validações mais robustas
   - Logging
   - Persistência de dados
   - API REST
   - Interface web

3. Os testes cobrem cenários principais mas podem ser expandidos
4. Implementação segue boas práticas de desenvolvimento Python

ENTREGA:
========================================================================
- Código fonte organizado
- Testes funcionais para questões principais  
- Documentação de uso
- Estrutura pronta para apresentação
"""
# test_questao1_pytest.py - Questão 1: Testes com Pytest para classe Produto
import pytest
from src.ecommerce import Produto, EstoqueInsuficienteError

def test_criar_produto():
    """Testa a criação de um produto"""
    produto = Produto(1, "Notebook", "Notebook Dell", 2500.00, 10, "Eletrônicos")
    
    assert produto.id == 1
    assert produto.nome == "Notebook"
    assert produto.descricao == "Notebook Dell"
    assert produto.preco == 2500.00
    assert produto.quantidade_estoque == 10
    assert produto.categoria == "Eletrônicos"

def test_verificar_disponibilidade_estoque():
    """Testa a verificação de disponibilidade de estoque"""
    produto = Produto(1, "Mouse", "Mouse sem fio", 50.00, 5, "Eletrônicos")
    
    # Testa disponibilidade com estoque suficiente
    assert produto.verificar_disponibilidade(3) == True
    assert produto.verificar_disponibilidade(5) == True
    
    # Testa disponibilidade com estoque insuficiente
    assert produto.verificar_disponibilidade(6) == False
    assert produto.verificar_disponibilidade(10) == False

def test_reducao_estoque():
    """Testa a redução de estoque"""
    produto = Produto(2, "Teclado", "Teclado mecânico", 150.00, 8, "Eletrônicos")
    
    # Testa redução válida
    produto.atualizar_estoque(3)
    assert produto.quantidade_estoque == 5
    
    # Testa redução com quantidade exata
    produto.atualizar_estoque(5)
    assert produto.quantidade_estoque == 0
    
    # Testa redução com estoque insuficiente
    produto_novo = Produto(3, "Monitor", "Monitor 24'", 800.00, 2, "Eletrônicos")
    with pytest.raises(EstoqueInsuficienteError):
        produto_novo.atualizar_estoque(5)

def test_obter_informacoes_produto():
    """Testa se retorna informações corretas do produto"""
    produto = Produto(4, "SSD", "SSD 500GB", 200.00, 15, "Armazenamento")
    
    info = produto.obter_informacoes()
    expected = {
        "id": 4,
        "nome": "SSD",
        "descricao": "SSD 500GB",
        "preco": 200.00,
        "estoque": 15,
        "categoria": "Armazenamento"
    }
    
    assert info == expected
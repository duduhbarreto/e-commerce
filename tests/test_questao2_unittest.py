# test_questao2_unittest.py - Questão 2: Testes com unittest para classe Carrinho
import unittest
from src.ecommerce import Produto, Carrinho, EstoqueInsuficienteError

class TestCarrinho(unittest.TestCase):
    
    def setUp(self):
        """Configura os objetos para os testes"""
        self.carrinho = Carrinho()
        self.produto1 = Produto(1, "Notebook", "Notebook Dell", 2500.00, 10, "Eletrônicos")
        self.produto2 = Produto(2, "Mouse", "Mouse sem fio", 50.00, 5, "Eletrônicos")
        self.produto3 = Produto(3, "Teclado", "Teclado mecânico", 150.00, 0, "Eletrônicos")  # Sem estoque
    
    def test_adicionar_itens_carrinho(self):
        """Testa a adição de itens no carrinho"""
        # Adiciona primeiro produto
        self.carrinho.adicionar_item(self.produto1, 2)
        self.assertIn(1, self.carrinho.itens)
        self.assertEqual(self.carrinho.itens[1]["quantidade"], 2)
        
        # Adiciona segundo produto
        self.carrinho.adicionar_item(self.produto2, 1)
        self.assertIn(2, self.carrinho.itens)
        self.assertEqual(self.carrinho.itens[2]["quantidade"], 1)
        
        # Adiciona mais do mesmo produto
        self.carrinho.adicionar_item(self.produto1, 1)
        self.assertEqual(self.carrinho.itens[1]["quantidade"], 3)
    
    def test_remover_itens_carrinho(self):
        """Testa a remoção de itens do carrinho"""
        # Adiciona itens primeiro
        self.carrinho.adicionar_item(self.produto1, 3)
        self.carrinho.adicionar_item(self.produto2, 2)
        
        # Remove parcialmente
        self.carrinho.remover_item(1, 1)
        self.assertEqual(self.carrinho.itens[1]["quantidade"], 2)
        
        # Remove completamente
        self.carrinho.remover_item(2)
        self.assertNotIn(2, self.carrinho.itens)
        
        # Remove quantidade maior que disponível
        self.carrinho.remover_item(1, 5)
        self.assertNotIn(1, self.carrinho.itens)
    
    def test_calcular_valor_total_carrinho(self):
        """Testa o cálculo do valor total do carrinho"""
        # Carrinho vazio
        self.assertEqual(self.carrinho.calcular_valor_total(), 0)
        
        # Adiciona produtos e verifica total
        self.carrinho.adicionar_item(self.produto1, 2)  # 2500 * 2 = 5000
        self.carrinho.adicionar_item(self.produto2, 3)  # 50 * 3 = 150
        
        total_esperado = 5150.00
        self.assertEqual(self.carrinho.calcular_valor_total(), total_esperado)
    
    def test_adicionar_produto_sem_estoque(self):
        """Testa comportamento ao tentar adicionar produto sem estoque suficiente"""
        # Tenta adicionar produto sem estoque
        with self.assertRaises(EstoqueInsuficienteError):
            self.carrinho.adicionar_item(self.produto3, 1)
        
        # Tenta adicionar mais que o estoque disponível
        with self.assertRaises(EstoqueInsuficienteError):
            self.carrinho.adicionar_item(self.produto2, 10)  # Produto2 tem apenas 5 em estoque
        
        # Verifica que nada foi adicionado
        self.assertEqual(len(self.carrinho.itens), 0)
    
    def test_limpar_carrinho(self):
        """Testa a limpeza do carrinho"""
        # Adiciona itens
        self.carrinho.adicionar_item(self.produto1, 1)
        self.carrinho.adicionar_item(self.produto2, 2)
        
        # Limpa carrinho
        self.carrinho.limpar_carrinho()
        
        # Verifica se está vazio
        self.assertEqual(len(self.carrinho.itens), 0)
        self.assertEqual(self.carrinho.calcular_valor_total(), 0)

if __name__ == '__main__':
    unittest.main()
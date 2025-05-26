# test_integracao_extras.py - Questões 4 e 5: Testes de Integração e Pedido
import pytest
import unittest
from unittest.mock import Mock, patch
from src.ecommerce import (
    Produto, Carrinho, Pedido, SistemaEcommerce, 
    StatusPedido, MetodoPagamento, TransicaoInvalidaError, EstoqueInsuficienteError
)

# ============= QUESTÃO 4: Testes de Integração Carrinho e Produto (Pytest) =============

class TestIntegracaoCarrinhoProduto:
    """Questão 4: Testes de integração entre Carrinho e Produto"""
    
    def setup_method(self):
        """Configura objetos para cada teste"""
        self.carrinho = Carrinho()
        self.produto1 = Produto(1, "Notebook", "Notebook Dell", 1000.00, 5, "Eletrônicos")
        self.produto2 = Produto(2, "Mouse", "Mouse sem fio", 50.00, 10, "Eletrônicos")
        self.produto_sem_estoque = Produto(3, "Teclado", "Teclado mecânico", 150.00, 0, "Eletrônicos")
    
    def test_carrinho_atualiza_valor_total_ao_adicionar_produtos(self):
        """Verifica se o carrinho atualiza corretamente o valor total ao adicionar produtos"""
        # Valor inicial deve ser 0
        assert self.carrinho.calcular_valor_total() == 0
        
        # Adiciona primeiro produto
        self.carrinho.adicionar_item(self.produto1, 2)
        assert self.carrinho.calcular_valor_total() == 2000.00
        
        # Adiciona segundo produto
        self.carrinho.adicionar_item(self.produto2, 3)
        assert self.carrinho.calcular_valor_total() == 2150.00  # 2000 + 150
        
        # Adiciona mais do primeiro produto
        self.carrinho.adicionar_item(self.produto1, 1)
        assert self.carrinho.calcular_valor_total() == 3150.00  # 2150 + 1000
    
    def test_carrinho_impede_adicao_produto_sem_estoque(self):
        """Verifica se o carrinho impede a adição de produtos sem estoque"""
        # Tenta adicionar produto sem estoque
        with pytest.raises(EstoqueInsuficienteError):
            self.carrinho.adicionar_item(self.produto_sem_estoque, 1)
        
        # Tenta adicionar mais que o estoque disponível
        with pytest.raises(EstoqueInsuficienteError):
            self.carrinho.adicionar_item(self.produto1, 10)  # Produto1 tem apenas 5
        
        # Verifica que carrinho permanece vazio
        assert len(self.carrinho.itens) == 0
        assert self.carrinho.calcular_valor_total() == 0
    
    def test_carrinho_permite_remover_produtos_parcialmente(self):
        """Verifica se o carrinho permite remover produtos parcialmente"""
        # Adiciona produtos
        self.carrinho.adicionar_item(self.produto1, 3)
        self.carrinho.adicionar_item(self.produto2, 5)
        
        valor_inicial = self.carrinho.calcular_valor_total()  # 3000 + 250 = 3250
        
        # Remove parcialmente produto1
        self.carrinho.remover_item(1, 1)
        assert self.carrinho.itens[1]["quantidade"] == 2
        assert self.carrinho.calcular_valor_total() == valor_inicial - 1000.00
        
        # Remove parcialmente produto2
        self.carrinho.remover_item(2, 2)
        assert self.carrinho.itens[2]["quantidade"] == 3
        assert self.carrinho.calcular_valor_total() == 2150.00  # 2000 + 150

# ============= QUESTÃO 5: Testes para Pedido (unittest) =============

class TestPedido(unittest.TestCase):
    """Questão 5: Testes para classe Pedido"""
    
    def setUp(self):
        """Configura objetos para os testes"""
        self.itens_teste = {
            1: {"produto": Produto(1, "Notebook", "Dell", 1000.00, 5, "Eletrônicos"), "quantidade": 2}
        }
        self.pedido = Pedido(
            "123", self.itens_teste, MetodoPagamento.PIX, 
            1800.00, "Rua A, 123"
        )
    
    def test_transicao_correta_estados_pedido(self):
        """Testa a transição correta entre os diferentes estados do pedido"""
        # Estado inicial deve ser PENDENTE
        self.assertEqual(self.pedido.status, StatusPedido.PENDENTE)
        
        # PENDENTE -> PAGO
        self.pedido.atualizar_status(StatusPedido.PAGO)
        self.assertEqual(self.pedido.status, StatusPedido.PAGO)
        self.assertIsNotNone(self.pedido.data_pagamento)
        
        # PAGO -> ENVIADO
        self.pedido.atualizar_status(StatusPedido.ENVIADO)
        self.assertEqual(self.pedido.status, StatusPedido.ENVIADO)
        self.assertIsNotNone(self.pedido.data_envio)
        
        # ENVIADO -> ENTREGUE
        self.pedido.atualizar_status(StatusPedido.ENTREGUE)
        self.assertEqual(self.pedido.status, StatusPedido.ENTREGUE)
    
    def test_processamento_pagamento_diferentes_metodos(self):
        """Testa o processamento de pagamento com diferentes métodos"""
        # Pedido com PIX
        pedido_pix = Pedido("456", self.itens_teste, MetodoPagamento.PIX, 900.00, "Rua B, 456")
        self.assertEqual(pedido_pix.metodo_pagamento, MetodoPagamento.PIX)
        
        # Pedido com cartão à vista
        pedido_vista = Pedido("789", self.itens_teste, MetodoPagamento.CARTAO_VISTA, 1000.00, "Rua C, 789")
        self.assertEqual(pedido_vista.metodo_pagamento, MetodoPagamento.CARTAO_VISTA)
        
        # Pedido com cartão parcelado
        pedido_parcelado = Pedido("101", self.itens_teste, MetodoPagamento.CARTAO_PARCELADO, 1100.00, "Rua D, 101")
        self.assertEqual(pedido_parcelado.metodo_pagamento, MetodoPagamento.CARTAO_PARCELADO)
    
    def test_restricoes_transicao_estado(self):
        """Testa as restrições de transição de estado"""
        # Não pode ir de PENDENTE para ENTREGUE
        with self.assertRaises(TransicaoInvalidaError):
            self.pedido.atualizar_status(StatusPedido.ENTREGUE)
        
        # Vai para PAGO primeiro
        self.pedido.atualizar_status(StatusPedido.PAGO)
        
        # Não pode ir de PAGO para ENTREGUE (deve passar por ENVIADO)
        with self.assertRaises(TransicaoInvalidaError):
            self.pedido.atualizar_status(StatusPedido.ENTREGUE)
        
        # Cancela o pedido
        self.pedido.atualizar_status(StatusPedido.CANCELADO)
        
        # Não pode sair do estado CANCELADO
        with self.assertRaises(TransicaoInvalidaError):
            self.pedido.atualizar_status(StatusPedido.PAGO)

# ============= QUESTÃO 7: Exemplo de Mock para Falhas de Pagamento =============

class TestFalhasPagamento:
    """Questão 7: Exemplo de testes com mock para simular falhas de pagamento"""
    
    def setup_method(self):
        """Configura sistema para testes"""
        self.sistema = SistemaEcommerce()
        self.produto = Produto(1, "Teste", "Produto teste", 100.00, 10, "Teste")
        self.sistema.adicionar_produto(self.produto)
        
        self.carrinho = Carrinho()
        self.carrinho.adicionar_item(self.produto, 1)
    
    @patch('src.ecommerce.SistemaPagamento.processar_pagamento')
    def test_falha_autorizacao_cartao(self, mock_pagamento):
        """Simula falha na autorização do cartão de crédito"""
        # Configura mock para retornar falha
        mock_pagamento.return_value = {"aprovado": False, "erro": "Cartão recusado"}
        
        # Tenta criar pedido
        with pytest.raises(Exception, match="Falha no processamento do pagamento"):
            self.sistema.criar_pedido(
                self.carrinho, MetodoPagamento.CARTAO_VISTA, "Endereço teste"
            )
        
        # Verifica que o produto ainda tem estoque (não foi reduzido)
        assert self.produto.quantidade_estoque == 10
        
        # Verifica que carrinho não foi limpo
        assert len(self.carrinho.itens) == 1

# ============= Exemplo de Teste de Performance (Questão 10) =============

import time

class TestPerformance:
    """Questão 10: Exemplo de testes de performance simples"""
    
    def test_tempo_adicao_multiplos_produtos(self):
        """Testa o tempo de resposta para adição de múltiplos produtos ao carrinho"""
        carrinho = Carrinho()
        produtos = [
            Produto(i, f"Produto {i}", f"Descrição {i}", 100.0, 1000, "Categoria")
            for i in range(100)
        ]
        
        start_time = time.time()
        
        for produto in produtos:
            carrinho.adicionar_item(produto, 1)
        
        end_time = time.time()
        tempo_execucao = end_time - start_time
        
        # Verifica que operação é rápida (menos de 1 segundo)
        assert tempo_execucao < 1.0
        assert len(carrinho.itens) == 100

if __name__ == '__main__':
    # Para rodar os testes unittest
    unittest.main()
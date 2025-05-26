# test_questao7_mock.py - Questão 7: Testes com Mock para falhas de pagamento
import pytest
from unittest.mock import Mock, patch, MagicMock
import time
from src.ecommerce import (
    Produto, Carrinho, SistemaEcommerce, SistemaPagamento,
    MetodoPagamento, StatusPedido, EstoqueInsuficienteError
)

class TestFalhasPagamentoMock:
    """Questão 7: Testes com Mock para simular diferentes cenários de falha no processamento de pagamento"""
    
    def setup_method(self):
        """Configura sistema para cada teste"""
        self.sistema = SistemaEcommerce()
        self.produto = Produto(1, "Produto Teste", "Descrição teste", 500.00, 10, "Teste")
        self.sistema.adicionar_produto(self.produto)
        
        self.carrinho = Carrinho()
        self.carrinho.adicionar_item(self.produto, 2)  # R$ 1000.00 total
        
        self.endereco = "Rua Teste, 123"
    
    @patch('src.ecommerce.SistemaPagamento.processar_pagamento')
    def test_falha_autorizacao_cartao_credito(self, mock_pagamento):
        """Simula falha na autorização do cartão de crédito"""
        # Configura mock para retornar falha na autorização
        mock_pagamento.return_value = {
            "aprovado": False, 
            "erro": "Cartão recusado pela operadora",
            "codigo_erro": "AUTH_DENIED"
        }
        
        # Guarda estado inicial do estoque
        estoque_inicial = self.produto.quantidade_estoque
        itens_carrinho_inicial = len(self.carrinho.itens)
        
        # Tenta criar pedido que deve falhar
        with pytest.raises(Exception, match="Falha no processamento do pagamento"):
            self.sistema.criar_pedido(
                self.carrinho, MetodoPagamento.CARTAO_VISTA, self.endereco
            )
        
        # Verifica que o sistema mantém estado correto após falha
        assert self.produto.quantidade_estoque == estoque_inicial  # Estoque não foi reduzido
        assert len(self.carrinho.itens) == itens_carrinho_inicial  # Carrinho não foi limpo
        assert len(self.sistema.pedidos) == 0  # Nenhum pedido foi criado
        
        # Verifica que o mock foi chamado corretamente
        mock_pagamento.assert_called_once_with(1000.00, MetodoPagamento.CARTAO_VISTA, 1)
    
    @patch('src.ecommerce.SistemaPagamento.processar_pagamento')
    def test_timeout_gateway_pagamento(self, mock_pagamento):
        """Simula timeout na comunicação com o gateway de pagamento"""
        # Configura mock para simular timeout
        def simular_timeout(*args, **kwargs):
            time.sleep(0.1)  # Simula demora
            raise TimeoutError("Timeout na comunicação com gateway de pagamento")
        
        mock_pagamento.side_effect = simular_timeout
        
        # Guarda estado inicial
        estoque_inicial = self.produto.quantidade_estoque
        itens_carrinho_inicial = len(self.carrinho.itens)
        
        # Tenta criar pedido que deve falhar por timeout
        with pytest.raises(TimeoutError, match="Timeout na comunicação com gateway"):
            self.sistema.criar_pedido(
                self.carrinho, MetodoPagamento.PIX, self.endereco
            )
        
        # Verifica estado após timeout
        assert self.produto.quantidade_estoque == estoque_inicial
        assert len(self.carrinho.itens) == itens_carrinho_inicial
        assert len(self.sistema.pedidos) == 0
    
    @patch('src.ecommerce.SistemaPagamento.processar_pagamento')
    def test_falha_intermitente_recuperacao(self, mock_pagamento):
        """Simula falha intermitente que se recupera na segunda tentativa"""
        # Configura mock para falhar na primeira chamada e suceder na segunda
        mock_pagamento.side_effect = [
            {"aprovado": False, "erro": "Erro temporário"},  # Primeira chamada falha
            {"aprovado": True, "valor_final": 900.00}        # Segunda chamada sucede
        ]
        
        # Primeira tentativa deve falhar
        with pytest.raises(Exception, match="Falha no processamento do pagamento"):
            self.sistema.criar_pedido(
                self.carrinho, MetodoPagamento.PIX, self.endereco
            )
        
        # Segunda tentativa deve funcionar
        id_pedido = self.sistema.criar_pedido(
            self.carrinho, MetodoPagamento.PIX, self.endereco
        )
        
        # Verifica que pedido foi criado na segunda tentativa
        assert id_pedido is not None
        pedido = self.sistema.obter_pedido(id_pedido)
        assert pedido.status == StatusPedido.PAGO
        
        # Verifica que mock foi chamado duas vezes
        assert mock_pagamento.call_count == 2
    
    @patch('src.ecommerce.SistemaPagamento.processar_pagamento')
    def test_falha_fraude_detectada(self, mock_pagamento):
        """Simula detecção de fraude no pagamento"""
        mock_pagamento.return_value = {
            "aprovado": False,
            "erro": "Possível fraude detectada",
            "codigo_erro": "FRAUD_DETECTED",
            "requer_verificacao": True
        }
        
        estoque_inicial = self.produto.quantidade_estoque
        
        with pytest.raises(Exception, match="Falha no processamento do pagamento"):
            self.sistema.criar_pedido(
                self.carrinho, MetodoPagamento.CARTAO_VISTA, self.endereco
            )
        
        # Sistema deve manter estado consistente
        assert self.produto.quantidade_estoque == estoque_inicial
        assert len(self.sistema.pedidos) == 0
    
    @patch('src.ecommerce.SistemaPagamento.processar_pagamento')
    def test_erro_conexao_banco(self, mock_pagamento):
        """Simula erro de conexão com banco de dados"""
        mock_pagamento.side_effect = ConnectionError("Erro de conexão com banco de dados")
        
        with pytest.raises(ConnectionError, match="Erro de conexão com banco"):
            self.sistema.criar_pedido(
                self.carrinho, MetodoPagamento.CARTAO_PARCELADO, self.endereco, 3
            )
    
    @patch('src.ecommerce.SistemaPagamento')
    def test_sistema_pagamento_indisponivel(self, mock_sistema_pagamento):
        """Simula sistema de pagamento completamente indisponível"""
        # Mock da classe inteira
        mock_instance = MagicMock()
        mock_sistema_pagamento.return_value = mock_instance
        mock_instance.processar_pagamento.side_effect = Exception("Sistema de pagamento indisponível")
        
        # Cria novo sistema com mock
        sistema_mock = SistemaEcommerce()
        sistema_mock.sistema_pagamento = mock_instance
        sistema_mock.adicionar_produto(self.produto)
        
        with pytest.raises(Exception, match="Sistema de pagamento indisponível"):
            sistema_mock.criar_pedido(
                self.carrinho, MetodoPagamento.PIX, self.endereco
            )
    
    def test_estado_pedido_apos_multiplas_falhas(self):
        """Verifica se o sistema mantém estado correto após múltiplas falhas"""
        # Simula várias tentativas de pagamento que falham
        with patch('src.ecommerce.SistemaPagamento.processar_pagamento') as mock_pag:
            mock_pag.return_value = {"aprovado": False, "erro": "Falha genérica"}
            
            # Várias tentativas de criar pedido
            for _ in range(3):
                try:
                    self.sistema.criar_pedido(
                        self.carrinho, MetodoPagamento.CARTAO_VISTA, self.endereco
                    )
                except Exception:
                    pass  # Esperado falhar
            
            # Verifica estado final do sistema
            assert len(self.sistema.pedidos) == 0
            assert self.produto.quantidade_estoque == 10  # Estoque original
            assert len(self.carrinho.itens) == 1  # Carrinho não foi limpo
    
    @patch('src.ecommerce.SistemaPagamento.processar_pagamento')
    def test_falha_parcial_processamento(self, mock_pagamento):
        """Simula falha que ocorre após pagamento ser aprovado mas antes de finalizar"""
        mock_pagamento.return_value = {"aprovado": True, "valor_final": 900.00}
        
        # Mock da função de atualizar estoque para simular falha após pagamento
        with patch.object(self.produto, 'atualizar_estoque') as mock_estoque:
            mock_estoque.side_effect = Exception("Erro ao atualizar estoque")
            
            with pytest.raises(Exception, match="Erro ao atualizar estoque"):
                self.sistema.criar_pedido(
                    self.carrinho, MetodoPagamento.PIX, self.endereco
                )
            
            # Verifica que pagamento foi processado mas pedido não foi salvo
            mock_pagamento.assert_called_once()
            assert len(self.sistema.pedidos) == 0
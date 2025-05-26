# test_questao6_testify.py - Questão 6: Testes para classe SistemaEcommerce
import pytest
from src.ecommerce import (
    Produto, Carrinho, SistemaEcommerce, MetodoPagamento, 
    StatusPedido, EstoqueInsuficienteError
)

class TestSistemaEcommerce:
    """Questão 6: Testes para classe SistemaEcommerce usando técnicas similares ao Testify"""
    
    def setup_method(self):
        """Configura sistema para cada teste"""
        self.sistema = SistemaEcommerce()
        self.produto1 = Produto(1, "Notebook", "Dell Inspiron", 2500.00, 10, "Eletrônicos")
        self.produto2 = Produto(2, "Mouse", "Mouse Logitech", 75.00, 20, "Eletrônicos")
        self.produto3 = Produto(3, "Teclado", "Teclado Mecânico", 200.00, 15, "Eletrônicos")
    
    def test_adicao_recuperacao_produtos(self):
        """Verifica adição e recuperação de produtos"""
        # Testa adição de produtos
        self.sistema.adicionar_produto(self.produto1)
        self.sistema.adicionar_produto(self.produto2)
        self.sistema.adicionar_produto(self.produto3)
        
        # Verifica se produtos foram adicionados corretamente
        assert len(self.sistema.produtos) == 3
        
        # Testa recuperação de produtos existentes
        produto_recuperado1 = self.sistema.obter_produto(1)
        assert produto_recuperado1 is not None
        assert produto_recuperado1.nome == "Notebook"
        assert produto_recuperado1.preco == 2500.00
        
        produto_recuperado2 = self.sistema.obter_produto(2)
        assert produto_recuperado2 is not None
        assert produto_recuperado2.nome == "Mouse"
        assert produto_recuperado2.categoria == "Eletrônicos"
        
        # Testa recuperação de produto inexistente
        produto_inexistente = self.sistema.obter_produto(999)
        assert produto_inexistente is None
    
    def test_criacao_pedidos(self):
        """Verifica criação de pedidos"""
        # Adiciona produtos ao sistema
        self.sistema.adicionar_produto(self.produto1)
        self.sistema.adicionar_produto(self.produto2)
        
        # Cria carrinho com produtos
        carrinho = Carrinho()
        carrinho.adicionar_item(self.produto1, 1)
        carrinho.adicionar_item(self.produto2, 2)
        
        valor_esperado = 2500.00 + (75.00 * 2)  # 2650.00
        assert carrinho.calcular_valor_total() == valor_esperado
        
        # Cria pedido com PIX
        id_pedido = self.sistema.criar_pedido(
            carrinho, MetodoPagamento.PIX, "Rua das Flores, 123"
        )
        
        # Verifica se pedido foi criado
        assert id_pedido is not None
        assert id_pedido in self.sistema.pedidos
        
        # Verifica dados do pedido
        pedido = self.sistema.obter_pedido(id_pedido)
        assert pedido is not None
        assert pedido.status == StatusPedido.PAGO
        assert pedido.metodo_pagamento == MetodoPagamento.PIX
        assert pedido.endereco_entrega == "Rua das Flores, 123"
        assert len(pedido.itens) == 2
        
        # Verifica se carrinho foi limpo após criação do pedido
        assert len(carrinho.itens) == 0
    
    def test_processamento_pagamentos(self):
        """Verifica processamento de pagamentos"""
        self.sistema.adicionar_produto(self.produto1)
        
        carrinho = Carrinho()
        carrinho.adicionar_item(self.produto1, 1)  # R$ 2500
        
        # Teste pagamento PIX (com desconto)
        id_pedido_pix = self.sistema.criar_pedido(
            carrinho, MetodoPagamento.PIX, "Endereço PIX"
        )
        pedido_pix = self.sistema.obter_pedido(id_pedido_pix)
        assert pedido_pix.metodo_pagamento == MetodoPagamento.PIX
        assert pedido_pix.status == StatusPedido.PAGO
        
        # Teste pagamento cartão à vista
        carrinho.adicionar_item(self.produto1, 1)
        id_pedido_vista = self.sistema.criar_pedido(
            carrinho, MetodoPagamento.CARTAO_VISTA, "Endereço Cartão"
        )
        pedido_vista = self.sistema.obter_pedido(id_pedido_vista)
        assert pedido_vista.metodo_pagamento == MetodoPagamento.CARTAO_VISTA
        assert pedido_vista.status == StatusPedido.PAGO
        
        # Teste pagamento cartão parcelado
        carrinho.adicionar_item(self.produto1, 1)
        id_pedido_parcelado = self.sistema.criar_pedido(
            carrinho, MetodoPagamento.CARTAO_PARCELADO, "Endereço Parcelado", 3
        )
        pedido_parcelado = self.sistema.obter_pedido(id_pedido_parcelado)
        assert pedido_parcelado.metodo_pagamento == MetodoPagamento.CARTAO_PARCELADO
        assert pedido_parcelado.status == StatusPedido.PAGO
    
    def test_cancelamento_pedidos_reabastecimento_estoque(self):
        """Verifica cancelamento de pedidos e reabastecimento do estoque"""
        # Adiciona produtos
        self.sistema.adicionar_produto(self.produto1)
        self.sistema.adicionar_produto(self.produto2)
        
        # Guarda estoque inicial
        estoque_inicial_produto1 = self.produto1.quantidade_estoque
        estoque_inicial_produto2 = self.produto2.quantidade_estoque
        
        # Cria carrinho e pedido
        carrinho = Carrinho()
        carrinho.adicionar_item(self.produto1, 3)
        carrinho.adicionar_item(self.produto2, 5)
        
        id_pedido = self.sistema.criar_pedido(
            carrinho, MetodoPagamento.PIX, "Endereço teste"
        )
        
        # Verifica se estoque foi reduzido
        assert self.produto1.quantidade_estoque == estoque_inicial_produto1 - 3
        assert self.produto2.quantidade_estoque == estoque_inicial_produto2 - 5
        
        # Verifica se pedido está pago
        pedido = self.sistema.obter_pedido(id_pedido)
        assert pedido.status == StatusPedido.PAGO
        
        # Cancela o pedido
        self.sistema.cancelar_pedido(id_pedido)
        
        # Verifica se estoque foi reabastecido
        assert self.produto1.quantidade_estoque == estoque_inicial_produto1
        assert self.produto2.quantidade_estoque == estoque_inicial_produto2
        
        # Verifica se pedido foi cancelado
        pedido_cancelado = self.sistema.obter_pedido(id_pedido)
        assert pedido_cancelado.status == StatusPedido.CANCELADO
    
    def test_carrinho_vazio_erro(self):
        """Verifica erro ao tentar criar pedido com carrinho vazio"""
        carrinho_vazio = Carrinho()
        
        with pytest.raises(ValueError, match="Carrinho vazio"):
            self.sistema.criar_pedido(
                carrinho_vazio, MetodoPagamento.PIX, "Endereço teste"
            )
    
    def test_pedido_inexistente(self):
        """Verifica comportamento com pedido inexistente"""
        # Tenta obter pedido que não existe
        pedido = self.sistema.obter_pedido("id-inexistente")
        assert pedido is None
        
        # Tenta cancelar pedido que não existe
        with pytest.raises(ValueError, match="Pedido não encontrado"):
            self.sistema.cancelar_pedido("id-inexistente")
    
    def test_estoque_insuficiente_ao_criar_pedido(self):
        """Verifica comportamento quando produto fica sem estoque durante criação do pedido"""
        produto_limitado = Produto(99, "Produto Limitado", "Apenas 2 unidades", 100.00, 2, "Teste")
        self.sistema.adicionar_produto(produto_limitado)
        
        carrinho = Carrinho()
        # Tenta adicionar mais que o estoque (deve dar erro no carrinho)
        with pytest.raises(EstoqueInsuficienteError):
            carrinho.adicionar_item(produto_limitado, 5)
        
        # Adiciona quantidade válida
        carrinho.adicionar_item(produto_limitado, 2)
        
        # Cria pedido (deve funcionar)
        id_pedido = self.sistema.criar_pedido(
            carrinho, MetodoPagamento.PIX, "Endereço teste"
        )
        
        # Verifica se estoque zerou
        assert produto_limitado.quantidade_estoque == 0
        
        # Verifica se pedido foi criado
        assert id_pedido in self.sistema.pedidos
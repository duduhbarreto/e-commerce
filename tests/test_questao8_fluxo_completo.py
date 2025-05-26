# test_questao8_fluxo_completo.py - Questão 8: Testes de integração completa do fluxo de compra
import unittest
from src.ecommerce import (
    Produto, Carrinho, SistemaEcommerce, 
    MetodoPagamento, StatusPedido
)

class TestFluxoCompletoCompra(unittest.TestCase):
    """Questão 8: Testes de integração completa do fluxo de compra com fixtures"""
    
    @classmethod
    def setUpClass(cls):
        """Fixture de classe - configuração que roda uma vez para toda a classe"""
        # Produtos para testes
        cls.produtos_catalogo = [
            Produto(1, "Notebook Dell", "Notebook Dell Inspiron 15", 2500.00, 5, "Eletrônicos"),
            Produto(2, "Mouse Logitech", "Mouse sem fio Logitech MX", 150.00, 20, "Eletrônicos"),
            Produto(3, "Teclado Mecânico", "Teclado mecânico RGB", 300.00, 15, "Eletrônicos"),
            Produto(4, "Monitor 24''", "Monitor Full HD 24 polegadas", 800.00, 8, "Eletrônicos"),
            Produto(5, "SSD 500GB", "SSD NVMe 500GB", 250.00, 12, "Armazenamento")
        ]
    
    def setUp(self):
        """Fixture que roda antes de cada teste"""
        # Cria novo sistema para cada teste
        self.sistema = SistemaEcommerce()
        
        # Adiciona produtos ao catálogo
        for produto in self.produtos_catalogo:
            # Cria nova instância para evitar problemas de estado compartilhado
            produto_novo = Produto(
                produto.id, produto.nome, produto.descricao, 
                produto.preco, produto.quantidade_estoque, produto.categoria
            )
            self.sistema.adicionar_produto(produto_novo)
        
        # Cliente padrão para testes
        self.endereco_entrega = "Rua das Flores, 123 - Jardim Primavera - 12345-678"
    
    def tearDown(self):
        """Fixture que roda após cada teste"""
        # Limpeza se necessário
        pass
    
    def _criar_carrinho_padrao(self):
        """Método auxiliar para criar carrinho padrão"""
        carrinho = Carrinho()
        
        # Adiciona produtos variados
        notebook = self.sistema.obter_produto(1)
        mouse = self.sistema.obter_produto(2)
        teclado = self.sistema.obter_produto(3)
        
        carrinho.adicionar_item(notebook, 1)  # R$ 2500
        carrinho.adicionar_item(mouse, 2)     # R$ 300
        carrinho.adicionar_item(teclado, 1)   # R$ 300
        
        # Total: R$ 3100
        return carrinho
    
    def test_fluxo_completo_pix(self):
        """Testa fluxo completo com pagamento via PIX"""
        # === FASE 1: Montagem do carrinho ===
        carrinho = self._criar_carrinho_padrao()
        valor_original = carrinho.calcular_valor_total()
        self.assertEqual(valor_original, 3100.00)
        
        # Verifica itens no carrinho
        self.assertEqual(len(carrinho.itens), 3)
        
        # === FASE 2: Criação do pedido ===
        id_pedido = self.sistema.criar_pedido(
            carrinho, MetodoPagamento.PIX, self.endereco_entrega
        )
        
        # Verifica se pedido foi criado
        self.assertIsNotNone(id_pedido)
        self.assertIn(id_pedido, self.sistema.pedidos)
        
        # === FASE 3: Validação do pedido ===
        pedido = self.sistema.obter_pedido(id_pedido)
        
        # Verifica dados básicos do pedido
        self.assertEqual(pedido.status, StatusPedido.PAGO)
        self.assertEqual(pedido.metodo_pagamento, MetodoPagamento.PIX)
        self.assertEqual(pedido.endereco_entrega, self.endereco_entrega)
        self.assertEqual(pedido.valor_total, valor_original)
        
        # Verifica itens do pedido
        self.assertEqual(len(pedido.itens), 3)
        self.assertIn(1, pedido.itens)  # Notebook
        self.assertIn(2, pedido.itens)  # Mouse
        self.assertIn(3, pedido.itens)  # Teclado
        
        # === FASE 4: Verificação do estoque ===
        # Estoque deve ter sido reduzido
        notebook = self.sistema.obter_produto(1)
        mouse = self.sistema.obter_produto(2)
        teclado = self.sistema.obter_produto(3)
        
        self.assertEqual(notebook.quantidade_estoque, 4)   # Era 5, vendeu 1
        self.assertEqual(mouse.quantidade_estoque, 18)     # Era 20, vendeu 2
        self.assertEqual(teclado.quantidade_estoque, 14)   # Era 15, vendeu 1
        
        # === FASE 5: Verificação do carrinho ===
        # Carrinho deve estar vazio após compra
        self.assertEqual(len(carrinho.itens), 0)
        self.assertEqual(carrinho.calcular_valor_total(), 0.0)
        
        # === FASE 6: Verificação de datas ===
        self.assertIsNotNone(pedido.data_criacao)
        self.assertIsNotNone(pedido.data_pagamento)
        self.assertIsNone(pedido.data_envio)  # Ainda não foi enviado
    
    def test_fluxo_completo_cartao_vista(self):
        """Testa fluxo completo com pagamento via cartão de crédito à vista"""
        # === MONTAGEM ===
        carrinho = Carrinho()
        monitor = self.sistema.obter_produto(4)  # R$ 800
        ssd = self.sistema.obter_produto(5)      # R$ 250
        
        carrinho.adicionar_item(monitor, 1)
        carrinho.adicionar_item(ssd, 2)
        
        valor_total = carrinho.calcular_valor_total()  # R$ 1300
        self.assertEqual(valor_total, 1300.00)
        
        # === PROCESSAMENTO ===
        id_pedido = self.sistema.criar_pedido(
            carrinho, MetodoPagamento.CARTAO_VISTA, self.endereco_entrega
        )
        
        # === VALIDAÇÕES ===
        pedido = self.sistema.obter_pedido(id_pedido)
        
        # Validações específicas do cartão à vista
        self.assertEqual(pedido.metodo_pagamento, MetodoPagamento.CARTAO_VISTA)
        self.assertEqual(pedido.status, StatusPedido.PAGO)
        self.assertEqual(pedido.valor_total, 1300.00)  # Sem alteração no valor para cartão à vista
        
        # Verificação do estoque
        monitor_atualizado = self.sistema.obter_produto(4)
        ssd_atualizado = self.sistema.obter_produto(5)
        
        self.assertEqual(monitor_atualizado.quantidade_estoque, 7)   # Era 8, vendeu 1
        self.assertEqual(ssd_atualizado.quantidade_estoque, 10)     # Era 12, vendeu 2
        
        # === SIMULAÇÃO DE PRÓXIMOS PASSOS DO PEDIDO ===
        # Simula envio do pedido
        pedido.atualizar_status(StatusPedido.ENVIADO)
        self.assertEqual(pedido.status, StatusPedido.ENVIADO)
        self.assertIsNotNone(pedido.data_envio)
        
        # Simula entrega
        pedido.atualizar_status(StatusPedido.ENTREGUE)
        self.assertEqual(pedido.status, StatusPedido.ENTREGUE)
    
    def test_fluxo_completo_cartao_parcelado(self):
        """Testa fluxo completo com pagamento via cartão de crédito parcelado"""
        # === MONTAGEM - Compra mais cara para parcelamento ===
        carrinho = Carrinho()
        notebook = self.sistema.obter_produto(1)  # R$ 2500
        monitor = self.sistema.obter_produto(4)   # R$ 800
        
        carrinho.adicionar_item(notebook, 2)  # R$ 5000
        carrinho.adicionar_item(monitor, 1)   # R$ 800
        
        valor_original = carrinho.calcular_valor_total()  # R$ 5800
        self.assertEqual(valor_original, 5800.00)
        
        # === PROCESSAMENTO COM PARCELAMENTO ===
        parcelas = 6
        id_pedido = self.sistema.criar_pedido(
            carrinho, MetodoPagamento.CARTAO_PARCELADO, 
            self.endereco_entrega, parcelas
        )
        
        # === VALIDAÇÕES ESPECÍFICAS DO PARCELAMENTO ===
        pedido = self.sistema.obter_pedido(id_pedido)
        
        self.assertEqual(pedido.metodo_pagamento, MetodoPagamento.CARTAO_PARCELADO)
        self.assertEqual(pedido.status, StatusPedido.PAGO)
        self.assertEqual(pedido.valor_total, valor_original)  # Valor original é mantido no pedido
        
        # Verificação do estoque para compra maior
        notebook_atualizado = self.sistema.obter_produto(1)
        monitor_atualizado = self.sistema.obter_produto(4)
        
        self.assertEqual(notebook_atualizado.quantidade_estoque, 3)  # Era 5, vendeu 2
        self.assertEqual(monitor_atualizado.quantidade_estoque, 7)   # Era 8, vendeu 1
        
        # === TESTE DE CENÁRIO COMPLETO COM CANCELAMENTO ===
        # Simula cancelamento do pedido parcelado
        self.sistema.cancelar_pedido(id_pedido)
        
        # Verifica status
        self.assertEqual(pedido.status, StatusPedido.CANCELADO)
        
        # Verifica reabastecimento do estoque
        notebook_reabastecido = self.sistema.obter_produto(1)
        monitor_reabastecido = self.sistema.obter_produto(4)
        
        self.assertEqual(notebook_reabastecido.quantidade_estoque, 5)  # Voltou ao original
        self.assertEqual(monitor_reabastecido.quantidade_estoque, 8)   # Voltou ao original
    
    def test_fluxo_multiplos_pedidos_mesmo_cliente(self):
        """Testa fluxo com múltiplos pedidos do mesmo cliente"""
        pedidos_criados = []
        
        # === PRIMEIRO PEDIDO - PIX ===
        carrinho1 = Carrinho()
        carrinho1.adicionar_item(self.sistema.obter_produto(2), 1)  # Mouse R$ 150
        
        id_pedido1 = self.sistema.criar_pedido(
            carrinho1, MetodoPagamento.PIX, self.endereco_entrega
        )
        pedidos_criados.append(id_pedido1)
        
        # === SEGUNDO PEDIDO - Cartão Vista ===
        carrinho2 = Carrinho()
        carrinho2.adicionar_item(self.sistema.obter_produto(3), 1)  # Teclado R$ 300
        
        id_pedido2 = self.sistema.criar_pedido(
            carrinho2, MetodoPagamento.CARTAO_VISTA, self.endereco_entrega
        )
        pedidos_criados.append(id_pedido2)
        
        # === TERCEIRO PEDIDO - Cartão Parcelado ===
        carrinho3 = Carrinho()
        carrinho3.adicionar_item(self.sistema.obter_produto(1), 1)  # Notebook R$ 2500
        
        id_pedido3 = self.sistema.criar_pedido(
            carrinho3, MetodoPagamento.CARTAO_PARCELADO, self.endereco_entrega, 4
        )
        pedidos_criados.append(id_pedido3)
        
        # === VALIDAÇÕES ===
        # Verifica se todos os pedidos foram criados
        self.assertEqual(len(self.sistema.pedidos), 3)
        
        for id_pedido in pedidos_criados:
            pedido = self.sistema.obter_pedido(id_pedido)
            self.assertIsNotNone(pedido)
            self.assertEqual(pedido.status, StatusPedido.PAGO)
            self.assertEqual(pedido.endereco_entrega, self.endereco_entrega)
        
        # Verifica se estoques foram reduzidos corretamente
        mouse = self.sistema.obter_produto(2)
        teclado = self.sistema.obter_produto(3)
        notebook = self.sistema.obter_produto(1)
        
        self.assertEqual(mouse.quantidade_estoque, 19)     # Era 20, vendeu 1
        self.assertEqual(teclado.quantidade_estoque, 14)   # Era 15, vendeu 1
        self.assertEqual(notebook.quantidade_estoque, 4)   # Era 5, vendeu 1
    
    def test_fluxo_com_estoque_insuficiente(self):
        """Testa fluxo quando produto fica sem estoque durante o processo"""
        # Cria produto com estoque limitado
        produto_limitado = Produto(99, "Produto Limitado", "Apenas 1 unidade", 100.00, 1, "Teste")
        self.sistema.adicionar_produto(produto_limitado)
        
        # === PRIMEIRO PEDIDO - Consome todo o estoque ===
        carrinho1 = Carrinho()
        carrinho1.adicionar_item(produto_limitado, 1)
        
        id_pedido1 = self.sistema.criar_pedido(
            carrinho1, MetodoPagamento.PIX, self.endereco_entrega
        )
        
        # Verifica que pedido foi criado e estoque zerou
        self.assertIsNotNone(id_pedido1)
        self.assertEqual(produto_limitado.quantidade_estoque, 0)
        
        # === TENTATIVA DE SEGUNDO PEDIDO - Deve falhar ===
        carrinho2 = Carrinho()
        
        with self.assertRaises(Exception):  # Deve dar erro de estoque insuficiente
            carrinho2.adicionar_item(produto_limitado, 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)
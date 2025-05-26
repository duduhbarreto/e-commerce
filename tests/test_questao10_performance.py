# test_questao10_performance.py - Questão 10: Testes de performance usando as três bibliotecas
import pytest
import unittest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.ecommerce import (
    Produto, Carrinho, SistemaEcommerce, SistemaPagamento,
    MetodoPagamento, StatusPedido
)

# ============= TESTES COM PYTEST =============

class TestPerformancePytest:
    """Testes de performance usando Pytest"""
    
    def test_tempo_adicao_multiplos_produtos_carrinho(self):
        """Testa o tempo de resposta para adição de múltiplos produtos ao carrinho"""
        carrinho = Carrinho()
        
        # Cria 500 produtos diferentes
        produtos = []
        for i in range(500):
            produto = Produto(
                id=i+1, 
                nome=f"Produto {i+1}", 
                descricao=f"Descrição do produto {i+1}", 
                preco=100.0 + i, 
                quantidade_estoque=1000, 
                categoria="Teste"
            )
            produtos.append(produto)
        
        # Mede tempo de adição
        start_time = time.time()
        
        for produto in produtos:
            carrinho.adicionar_item(produto, 1)
        
        end_time = time.time()
        tempo_execucao = end_time - start_time
        
        # Validações
        assert len(carrinho.itens) == 500
        assert tempo_execucao < 1.0  # Deve ser rápido (menos de 1 segundo)
        
        # Teste adicional: tempo para calcular valor total
        start_time = time.time()
        valor_total = carrinho.calcular_valor_total()
        end_time = time.time()
        
        tempo_calculo = end_time - start_time
        assert tempo_calculo < 0.1  # Cálculo deve ser muito rápido
        assert valor_total > 0
    
    def test_performance_criacao_produtos(self):
        """Testa performance na criação de muitos produtos"""
        produtos = []
        
        start_time = time.time()
        
        # Cria 1000 produtos
        for i in range(1000):
            produto = Produto(
                id=i, 
                nome=f"Produto Performance {i}", 
                descricao=f"Produto para teste de performance {i}", 
                preco=50.0 + (i * 0.5), 
                quantidade_estoque=100, 
                categoria=f"Categoria {i % 10}"
            )
            produtos.append(produto)
        
        end_time = time.time()
        tempo_criacao = end_time - start_time
        
        # Validações
        assert len(produtos) == 1000
        assert tempo_criacao < 0.5  # Criação deve ser muito rápida
    
    @pytest.mark.parametrize("num_produtos", [10, 50, 100, 200, 500])
    def test_performance_carrinho_escalonavel(self, num_produtos):
        """Testa se performance do carrinho escala bem com diferentes quantidades"""
        carrinho = Carrinho()
        produtos = [
            Produto(i, f"Produto {i}", f"Desc {i}", 100.0, 1000, "Teste")
            for i in range(num_produtos)
        ]
        
        start_time = time.time()
        
        for produto in produtos:
            carrinho.adicionar_item(produto, 1)
        
        valor_total = carrinho.calcular_valor_total()
        
        end_time = time.time()
        tempo_total = end_time - start_time
        
        # Performance deve ser linear ou melhor
        tempo_max_esperado = num_produtos * 0.001  # 1ms por produto
        assert tempo_total <= tempo_max_esperado
        assert len(carrinho.itens) == num_produtos

# ============= TESTES COM UNITTEST =============

class TestPerformanceUnittest(unittest.TestCase):
    """Testes de performance usando unittest"""
    
    def setUp(self):
        """Configura sistema para testes"""
        self.sistema = SistemaEcommerce()
        self.sistema_pagamento = SistemaPagamento()
    
    def test_tempo_processamento_pagamento(self):
        """Testa o tempo de processamento de pagamento"""
        # Processa muitos pagamentos sequencialmente
        num_pagamentos = 1000
        valores_teste = [100.0, 250.0, 500.0, 1000.0, 1500.0]
        metodos_teste = [MetodoPagamento.PIX, MetodoPagamento.CARTAO_VISTA, MetodoPagamento.CARTAO_PARCELADO]
        
        start_time = time.time()
        
        pagamentos_processados = 0
        for i in range(num_pagamentos):
            valor = valores_teste[i % len(valores_teste)]
            metodo = metodos_teste[i % len(metodos_teste)]
            
            if metodo == MetodoPagamento.CARTAO_PARCELADO:
                resultado = self.sistema_pagamento.processar_pagamento(valor, metodo, 3)
            else:
                resultado = self.sistema_pagamento.processar_pagamento(valor, metodo)
            
            if resultado["aprovado"]:
                pagamentos_processados += 1
        
        end_time = time.time()
        tempo_total = end_time - start_time
        
        # Validações
        self.assertEqual(pagamentos_processados, num_pagamentos)
        self.assertLess(tempo_total, 2.0)  # 1000 pagamentos em menos de 2 segundos
        
        # Calcula média de tempo por pagamento
        tempo_medio = tempo_total / num_pagamentos
        self.assertLess(tempo_medio, 0.002)  # Menos de 2ms por pagamento
    
    def test_performance_sistema_completo(self):
        """Testa performance do sistema completo com múltiplas operações"""
        # Adiciona produtos ao sistema
        start_time = time.time()
        
        for i in range(100):
            produto = Produto(
                id=i+1, 
                nome=f"Produto Sistema {i+1}", 
                descricao=f"Descrição {i+1}", 
                preco=100.0 + i, 
                quantidade_estoque=50, 
                categoria="Performance"
            )
            self.sistema.adicionar_produto(produto)
        
        tempo_adicao_produtos = time.time() - start_time
        
        # Cria múltiplos pedidos
        start_time = time.time()
        
        pedidos_criados = []
        for i in range(20):
            carrinho = Carrinho()
            
            # Adiciona 3 produtos aleatórios ao carrinho
            for j in range(3):
                produto_id = (i * 3 + j) % 100 + 1
                produto = self.sistema.obter_produto(produto_id)
                if produto and produto.quantidade_estoque > 0:
                    carrinho.adicionar_item(produto, 1)
            
            if carrinho.itens:
                try:
                    id_pedido = self.sistema.criar_pedido(
                        carrinho, MetodoPagamento.PIX, f"Endereço {i}"
                    )
                    pedidos_criados.append(id_pedido)
                except Exception:
                    pass  # Ignora erros de estoque
        
        tempo_criacao_pedidos = time.time() - start_time
        
        # Validações
        self.assertLess(tempo_adicao_produtos, 0.5)
        self.assertLess(tempo_criacao_pedidos, 3.0)
        self.assertGreater(len(pedidos_criados), 10)  # Pelo menos 10 pedidos criados
    
    def test_performance_busca_produtos(self):
        """Testa performance na busca de produtos"""
        # Adiciona muitos produtos
        for i in range(1000):
            produto = Produto(i+1, f"Produto {i+1}", f"Desc {i+1}", 100.0, 10, "Teste")
            self.sistema.adicionar_produto(produto)
        
        # Testa tempo de busca
        start_time = time.time()
        
        produtos_encontrados = 0
        for i in range(500):  # Busca 500 produtos
            produto_id = (i * 2) + 1  # IDs ímpares
            produto = self.sistema.obter_produto(produto_id)
            if produto:
                produtos_encontrados += 1
        
        end_time = time.time()
        tempo_busca = end_time - start_time
        
        self.assertEqual(produtos_encontrados, 500)
        self.assertLess(tempo_busca, 0.1)  # Buscas devem ser muito rápidas

# ============= TESTES SIMULANDO TESTIFY (com Pytest) =============

class TestPerformanceTestify:
    """Testes de performance simulando estilo Testify"""
    
    def test_comportamento_grande_volume_pedidos_simultaneos(self):
        """Testa o comportamento do sistema com um grande volume de pedidos simultâneos"""
        sistema = SistemaEcommerce()
        
        # Prepara produtos com estoque alto
        produtos = []
        for i in range(50):
            produto = Produto(
                id=i+1, 
                nome=f"Produto Concurrent {i+1}", 
                descricao=f"Produto para teste de concorrência", 
                preco=100.0, 
                quantidade_estoque=1000,  # Estoque alto para evitar conflitos
                categoria="Concorrencia"
            )
            produtos.append(produto)
            sistema.adicionar_produto(produto)
        
        # Função para criar pedido
        def criar_pedido(produto_id, thread_id):
            try:
                carrinho = Carrinho()
                produto = sistema.obter_produto(produto_id)
                if produto:
                    carrinho.adicionar_item(produto, 1)
                    
                    id_pedido = sistema.criar_pedido(
                        carrinho, 
                        MetodoPagamento.PIX, 
                        f"Endereço Thread {thread_id}"
                    )
                    return id_pedido
            except Exception as e:
                return f"Erro: {str(e)}"
            return None
        
        # Executa testes de concorrência
        start_time = time.time()
        
        pedidos_criados = []
        erros = []
        
        # Usa ThreadPoolExecutor para simular concorrência
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submete 100 tarefas de criação de pedido
            futures = []
            for i in range(100):
                produto_id = (i % 50) + 1  # Distribui entre os 50 produtos
                future = executor.submit(criar_pedido, produto_id, i)
                futures.append(future)
            
            # Coleta resultados
            for future in as_completed(futures):
                resultado = future.result()
                if resultado and not str(resultado).startswith("Erro"):
                    pedidos_criados.append(resultado)
                elif resultado:
                    erros.append(resultado)
        
        end_time = time.time()
        tempo_total = end_time - start_time
        
        # Validações
        assert tempo_total < 5.0  # Deve processar 100 pedidos em menos de 5 segundos
        assert len(pedidos_criados) > 80  # Pelo menos 80% dos pedidos devem ser criados
        assert len(erros) < 20  # Máximo 20% de erros
        
        # Verifica integridade dos dados
        pedidos_unicos = set(pedidos_criados)
        assert len(pedidos_unicos) == len(pedidos_criados)  # Todos os IDs devem ser únicos
    
    def test_stress_adicao_remocao_carrinho(self):
        """Teste de stress para adição e remoção de itens no carrinho"""
        carrinho = Carrinho()
        
        # Cria produtos para teste
        produtos = [
            Produto(i, f"Produto Stress {i}", f"Desc {i}", 100.0, 10000, "Stress")
            for i in range(100)
        ]
        
        start_time = time.time()
        
        # Operações mistas: adicionar e remover
        for ciclo in range(50):  # 50 ciclos de operações
            # Adiciona 10 produtos
            for i in range(10):
                produto = produtos[i]
                carrinho.adicionar_item(produto, 2)
            
            # Remove 5 produtos parcialmente
            for i in range(5):
                carrinho.remover_item(i, 1)
            
            # Remove 2 produtos completamente
            for i in range(5, 7):
                carrinho.remover_item(i)
            
            # Calcula valor total
            valor = carrinho.calcular_valor_total()
            assert valor >= 0
        
        end_time = time.time()
        tempo_operacoes = end_time - start_time
        
        # Validações de performance
        assert tempo_operacoes < 2.0  # Todas as operações em menos de 2 segundos
        
        # Estado final do carrinho deve ser consistente
        valor_final = carrinho.calcular_valor_total()
        assert valor_final >= 0
    
    def test_memory_usage_large_dataset(self):
        """Testa uso de memória com grande quantidade de dados"""
        import sys
        
        sistema = SistemaEcommerce()
        
        # Medição inicial
        initial_objects = len(sistema.produtos)
        
        # Adiciona muitos produtos
        for i in range(5000):
            produto = Produto(
                id=i+1,
                nome=f"Produto Memory {i+1}",
                descricao=f"Produto para teste de memória com ID {i+1}",
                preco=100.0 + (i * 0.1),
                quantidade_estoque=100,
                categoria=f"Categoria {i % 20}"
            )
            sistema.adicionar_produto(produto)
        
        # Verifica se todos foram adicionados
        assert len(sistema.produtos) == 5000
        
        # Cria alguns pedidos para testar memória completa
        for i in range(10):
            carrinho = Carrinho()
            
            # Adiciona 5 produtos ao carrinho
            for j in range(5):
                produto_id = (i * 5 + j) + 1
                produto = sistema.obter_produto(produto_id)
                if produto:
                    carrinho.adicionar_item(produto, 1)
            
            if carrinho.itens:
                sistema.criar_pedido(
                    carrinho, MetodoPagamento.PIX, f"Endereço Memory {i}"
                )
        
        # Validações
        assert len(sistema.pedidos) == 10
        assert all(pedido.status == StatusPedido.PAGO for pedido in sistema.pedidos.values())

if __name__ == '__main__':
    # Para executar testes unittest
    unittest.main(verbosity=2)
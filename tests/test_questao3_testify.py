# test_questao3_testify.py - Questão 3: Testes para classe SistemaPagamento
# Nota: Como "Testify" não é uma biblioteca padrão do Python, 
# usaremos pytest com parametrização para simular o comportamento esperado

import pytest
from src.ecommerce import SistemaPagamento, MetodoPagamento

class TestSistemaPagamento:
    
    def setup_method(self):
        """Configura o sistema de pagamento para cada teste"""
        self.sistema = SistemaPagamento()
    
    def test_calculo_cartao_vista(self):
        """Testa cálculo correto do valor para pagamento com cartão de crédito à vista"""
        valor_original = 1000.00
        valor_calculado = self.sistema.calcular_valor_cartao_vista(valor_original)
        
        # Para pagamento à vista, valor deve ser o mesmo
        assert valor_calculado == valor_original
        
        # Testa com diferentes valores
        assert self.sistema.calcular_valor_cartao_vista(500.00) == 500.00
        assert self.sistema.calcular_valor_cartao_vista(2500.50) == 2500.50
    
    @pytest.mark.parametrize("valor,parcelas,valor_esperado", [
        (1000.00, 2, 1050.00),  # 1000 + 5% = 1050
        (1000.00, 3, 1100.00),  # 1000 + 10% = 1100
        (1000.00, 6, 1250.00),  # 1000 + 25% = 1250
        (500.00, 4, 575.00),    # 500 + 15% = 575
    ])
    def test_calculo_cartao_parcelado(self, valor, parcelas, valor_esperado):
        """Testa cálculo correto do valor para pagamento parcelado com diferentes números de parcelas"""
        resultado = self.sistema.calcular_valor_cartao_parcelado(valor, parcelas)
        
        assert resultado["valor_total"] == valor_esperado
        assert resultado["parcelas"] == parcelas
        assert resultado["valor_parcela"] == valor_esperado / parcelas
        
        # Verifica se valor da parcela está correto
        assert abs(resultado["valor_parcela"] * parcelas - valor_esperado) < 0.01
    
    def test_calculo_cartao_parcelado_limites(self):
        """Testa limites do parcelamento"""
        valor = 1000.00
        
        # Testa parcelas inválidas
        with pytest.raises(ValueError):
            self.sistema.calcular_valor_cartao_parcelado(valor, 1)  # Mínimo 2
        
        with pytest.raises(ValueError):
            self.sistema.calcular_valor_cartao_parcelado(valor, 13)  # Máximo 12
    
    @pytest.mark.parametrize("valor,valor_esperado", [
        (1000.00, 900.00),   # 1000 - 10% = 900
        (500.00, 450.00),    # 500 - 10% = 450
        (250.50, 225.45),    # 250.50 - 10% = 225.45
    ])
    def test_calculo_pix_desconto(self, valor, valor_esperado):
        """Testa cálculo correto do valor para pagamento com PIX (aplicação do desconto)"""
        valor_calculado = self.sistema.calcular_valor_pix(valor)
        
        assert abs(valor_calculado - valor_esperado) < 0.01
    
    def test_calculo_valor_parcelas(self):
        """Testa cálculo específico do valor das parcelas"""
        valor = 1200.00
        
        # Teste com 4 parcelas
        resultado = self.sistema.calcular_valor_cartao_parcelado(valor, 4)
        # 1200 + 15% (3 * 5%) = 1380
        # 1380 / 4 = 345
        assert resultado["valor_parcela"] == 345.00
        assert resultado["valor_total"] == 1380.00
        
        # Teste com 6 parcelas
        resultado = self.sistema.calcular_valor_cartao_parcelado(valor, 6)
        # 1200 + 25% (5 * 5%) = 1500
        # 1500 / 6 = 250
        assert resultado["valor_parcela"] == 250.00
        assert resultado["valor_total"] == 1500.00
    
    def test_processar_pagamento_integrado(self):
        """Testa o processamento integrado de pagamentos"""
        valor = 1000.00
        
        # Teste pagamento à vista
        resultado = self.sistema.processar_pagamento(valor, MetodoPagamento.CARTAO_VISTA)
        assert resultado["valor_final"] == 1000.00
        assert resultado["aprovado"] == True
        
        # Teste pagamento PIX
        resultado = self.sistema.processar_pagamento(valor, MetodoPagamento.PIX)
        assert resultado["valor_final"] == 900.00
        assert resultado["aprovado"] == True
        
        # Teste pagamento parcelado
        resultado = self.sistema.processar_pagamento(valor, MetodoPagamento.CARTAO_PARCELADO, 3)
        assert resultado["valor_total"] == 1100.00
        assert resultado["valor_parcela"] == 1100.00 / 3
        assert resultado["aprovado"] == True
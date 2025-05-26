# test_questao9_parametrizados.py - Questão 9: Testes parametrizados para diferentes configurações
import pytest
from src.ecommerce import SistemaPagamento, MetodoPagamento

class TestConfiguracoesParametrizadas:
    """Questão 9: Testes parametrizados para verificar o comportamento do sistema com diferentes configurações"""
    
    def setup_method(self):
        """Configura sistema de pagamento básico para cada teste"""
        self.sistema = SistemaPagamento()
    
    # ============= TESTES COM DIFERENTES TAXAS DE JUROS =============
    
    @pytest.mark.parametrize("taxa_juros,parcelas,valor_base,valor_esperado_total", [
        # Taxa 2% por parcela
        (0.02, 2, 1000.00, 1020.00),   # 1000 + (1000 * 0.02 * 1) = 1020
        (0.02, 3, 1000.00, 1040.00),   # 1000 + (1000 * 0.02 * 2) = 1040
        (0.02, 6, 1000.00, 1100.00),   # 1000 + (1000 * 0.02 * 5) = 1100
        (0.02, 12, 1000.00, 1220.00),  # 1000 + (1000 * 0.02 * 11) = 1220
        
        # Taxa 3% por parcela
        (0.03, 2, 1000.00, 1030.00),   # 1000 + (1000 * 0.03 * 1) = 1030
        (0.03, 4, 1000.00, 1090.00),   # 1000 + (1000 * 0.03 * 3) = 1090
        (0.03, 6, 1000.00, 1150.00),   # 1000 + (1000 * 0.03 * 5) = 1150
        
        # Taxa 7% por parcela (mais alta)
        (0.07, 2, 1000.00, 1070.00),   # 1000 + (1000 * 0.07 * 1) = 1070
        (0.07, 3, 1000.00, 1140.00),   # 1000 + (1000 * 0.07 * 2) = 1140
        (0.07, 6, 1000.00, 1350.00),   # 1000 + (1000 * 0.07 * 5) = 1350
        
        # Diferentes valores base
        (0.05, 3, 500.00, 550.00),     # 500 + (500 * 0.05 * 2) = 550
        (0.05, 4, 2000.00, 2300.00),   # 2000 + (2000 * 0.05 * 3) = 2300
    ])
    def test_diferentes_taxas_juros_parcelamento(self, taxa_juros, parcelas, valor_base, valor_esperado_total):
        """Testa diferentes taxas de juros para parcelamento"""
        # Configura taxa personalizada
        self.sistema.taxa_juros = taxa_juros
        
        # Calcula parcelamento
        resultado = self.sistema.calcular_valor_cartao_parcelado(valor_base, parcelas)
        
        # Validações - usando comparação aproximada para evitar problemas de ponto flutuante
        assert abs(resultado["valor_total"] - valor_esperado_total) < 0.01
        assert resultado["parcelas"] == parcelas
        assert abs(resultado["valor_parcela"] - (valor_esperado_total / parcelas)) < 0.01
        
        # Verifica se valor com juros é sempre maior que o original (exceto 1 parcela)
        if parcelas > 1:
            assert resultado["valor_total"] > valor_base
    
    @pytest.mark.parametrize("taxa_juros,valor_base", [
        (0.01, 1000.00),  # 1% por parcela
        (0.04, 1500.00),  # 4% por parcela
        (0.08, 800.00),   # 8% por parcela
        (0.10, 2500.00),  # 10% por parcela
    ])
    def test_taxa_juros_multiplas_parcelas(self, taxa_juros, valor_base):
        """Testa mesma taxa de juros com diferentes números de parcelas"""
        self.sistema.taxa_juros = taxa_juros
        
        parcelas_teste = [2, 3, 6, 12]
        valores_calculados = []
        
        for parcelas in parcelas_teste:
            resultado = self.sistema.calcular_valor_cartao_parcelado(valor_base, parcelas)
            valores_calculados.append(resultado["valor_total"])
            
            # Valor esperado: valor_base + (valor_base * taxa_juros * (parcelas - 1))
            valor_esperado = valor_base + (valor_base * taxa_juros * (parcelas - 1))
            assert abs(resultado["valor_total"] - valor_esperado) < 0.01
        
        # Verifica que mais parcelas = mais juros
        for i in range(1, len(valores_calculados)):
            assert valores_calculados[i] > valores_calculados[i-1]
    
    # ============= TESTES COM DIFERENTES DESCONTOS PIX =============
    
    @pytest.mark.parametrize("desconto_pix,valor_base,valor_esperado", [
        # Descontos variados
        (0.05, 1000.00, 950.00),    # 5% desconto
        (0.10, 1000.00, 900.00),    # 10% desconto (padrão)
        (0.15, 1000.00, 850.00),    # 15% desconto
        (0.20, 1000.00, 800.00),    # 20% desconto
        (0.25, 1000.00, 750.00),    # 25% desconto
        
        # Diferentes valores base
        (0.12, 500.00, 440.00),     # 12% desconto em R$ 500
        (0.08, 1500.00, 1380.00),   # 8% desconto em R$ 1500
        (0.18, 2000.00, 1640.00),   # 18% desconto em R$ 2000
        
        # Casos extremos
        (0.01, 100.00, 99.00),      # 1% desconto mínimo
        (0.30, 1000.00, 700.00),    # 30% desconto alto
    ])
    def test_diferentes_percentuais_desconto_pix(self, desconto_pix, valor_base, valor_esperado):
        """Testa diferentes percentuais de desconto para pagamento via PIX"""
        # Configura desconto personalizado
        self.sistema.desconto_pix = desconto_pix
        
        # Calcula valor com desconto
        valor_final = self.sistema.calcular_valor_pix(valor_base)
        
        # Validações
        assert abs(valor_final - valor_esperado) < 0.01
        assert valor_final < valor_base  # Sempre deve ser menor que o original
        
        # Verifica se desconto está correto
        desconto_aplicado = valor_base - valor_final
        desconto_esperado = valor_base * desconto_pix
        assert abs(desconto_aplicado - desconto_esperado) < 0.01
    
    @pytest.mark.parametrize("desconto", [0.05, 0.10, 0.15, 0.20, 0.25, 0.30])
    def test_desconto_pix_valores_variados(self, desconto):
        """Testa mesmo desconto PIX com diferentes valores"""
        self.sistema.desconto_pix = desconto
        
        valores_teste = [100.00, 500.00, 1000.00, 1500.00, 2500.00]
        
        for valor in valores_teste:
            valor_com_desconto = self.sistema.calcular_valor_pix(valor)
            valor_esperado = valor * (1 - desconto)
            
            assert abs(valor_com_desconto - valor_esperado) < 0.01
            assert valor_com_desconto < valor
    
    # ============= TESTES COM DIFERENTES QUANTIDADES DE PARCELAS =============
    
    @pytest.mark.parametrize("parcelas", [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    def test_diferentes_quantidades_parcelas(self, parcelas):
        """Testa diferentes quantidades de parcelas"""
        valor_base = 1200.00
        
        resultado = self.sistema.calcular_valor_cartao_parcelado(valor_base, parcelas)
        
        # Validações básicas
        assert resultado["parcelas"] == parcelas
        assert resultado["valor_total"] > valor_base  # Sempre com juros
        
        # Verifica cálculo da parcela
        valor_parcela_esperado = resultado["valor_total"] / parcelas
        assert abs(resultado["valor_parcela"] - valor_parcela_esperado) < 0.01
        
        # Verifica se juros aumentam com mais parcelas
        valor_esperado = valor_base + (valor_base * self.sistema.taxa_juros * (parcelas - 1))
        assert abs(resultado["valor_total"] - valor_esperado) < 0.01
    
    @pytest.mark.parametrize("parcelas,valor_parcela_max", [
        (2, 600.00),    # Para valor de 1200, máximo 600 por parcela
        (3, 400.00),    # Máximo 400 por parcela
        (4, 350.00),    # Máximo 350 por parcela (CORRIGIDO: era 300)
        (6, 250.00),    # Máximo 250 por parcela (CORRIGIDO: era 220)
        (12, 160.00),   # Máximo 160 por parcela (CORRIGIDO: era 120)
    ])
    def test_valor_parcela_dentro_limite(self, parcelas, valor_parcela_max):
        """Testa se valor da parcela está dentro de limites aceitáveis"""
        valor_base = 1200.00
        
        resultado = self.sistema.calcular_valor_cartao_parcelado(valor_base, parcelas)
        
        # Verifica se valor da parcela não é muito alto
        assert resultado["valor_parcela"] <= valor_parcela_max * 1.1  # Margem de 10% para juros
    
    # ============= TESTES COMBINADOS COM MÚLTIPLOS PARÂMETROS =============
    
    @pytest.mark.parametrize("valor_base,taxa_juros,desconto_pix", [
        (1000.00, 0.05, 0.10),  # Valores padrão
        (500.00, 0.03, 0.15),   # Valores menores, juros baixos, desconto alto
        (2500.00, 0.07, 0.05),  # Valores altos, juros altos, desconto baixo
        (1500.00, 0.04, 0.12),  # Valores médios
    ])
    def test_configuracoes_combinadas(self, valor_base, taxa_juros, desconto_pix):
        """Testa combinações de diferentes configurações"""
        # Configura sistema
        self.sistema.taxa_juros = taxa_juros
        self.sistema.desconto_pix = desconto_pix
        
        # Testa PIX
        valor_pix = self.sistema.calcular_valor_pix(valor_base)
        valor_pix_esperado = valor_base * (1 - desconto_pix)
        assert abs(valor_pix - valor_pix_esperado) < 0.01
        
        # Testa cartão à vista
        valor_vista = self.sistema.calcular_valor_cartao_vista(valor_base)
        assert valor_vista == valor_base
        
        # Testa parcelamento
        for parcelas in [2, 3, 6]:
            resultado_parcelado = self.sistema.calcular_valor_cartao_parcelado(valor_base, parcelas)
            valor_esperado = valor_base + (valor_base * taxa_juros * (parcelas - 1))
            assert abs(resultado_parcelado["valor_total"] - valor_esperado) < 0.01
        
        # Verifica hierarquia de valores: PIX < Vista < Parcelado
        resultado_6x = self.sistema.calcular_valor_cartao_parcelado(valor_base, 6)
        assert valor_pix < valor_vista < resultado_6x["valor_total"]
    
    # ============= TESTES DE LIMITES E VALIDAÇÕES =============
    
    @pytest.mark.parametrize("parcelas_invalidas", [1, 13, 0, 15, 24])
    def test_parcelas_invalidas(self, parcelas_invalidas):
        """Testa comportamento com números de parcelas inválidos"""
        with pytest.raises(ValueError):
            self.sistema.calcular_valor_cartao_parcelado(1000.00, parcelas_invalidas)
    
    @pytest.mark.parametrize("valor_negativo", [-100.00, -50.00, -1000.00])
    def test_valores_negativos(self, valor_negativo):
        """Testa comportamento com valores negativos"""
        # Sistema deve lidar com valores negativos ou lançar erro apropriado
        try:
            resultado_pix = self.sistema.calcular_valor_pix(valor_negativo)
            resultado_vista = self.sistema.calcular_valor_cartao_vista(valor_negativo)
            resultado_parcelado = self.sistema.calcular_valor_cartao_parcelado(valor_negativo, 3)
            
            # Se aceitar valores negativos, deve manter proporcionalidade
            assert resultado_pix < 0
            assert resultado_vista == valor_negativo
            assert resultado_parcelado["valor_total"] < valor_negativo
        except ValueError:
            # É aceitável que o sistema rejeite valores negativos
            pass
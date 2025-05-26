# ecommerce.py - Sistema de E-commerce Simples
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime
import uuid

class StatusPedido(Enum):
    PENDENTE = "pendente"
    PAGO = "pago"
    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"

class MetodoPagamento(Enum):
    CARTAO_VISTA = "cartao_vista"
    CARTAO_PARCELADO = "cartao_parcelado"
    PIX = "pix"

class EstoqueInsuficienteError(Exception):
    """Exceção para quando não há estoque suficiente"""
    pass

class TransicaoInvalidaError(Exception):
    """Exceção para transições de estado inválidas"""
    pass

class Produto:
    """Classe que representa um item disponível para venda"""
    
    def __init__(self, id: int, nome: str, descricao: str, preco: float, quantidade_estoque: int, categoria: str):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.quantidade_estoque = quantidade_estoque
        self.categoria = categoria
    
    def verificar_disponibilidade(self, quantidade: int) -> bool:
        """Verifica se há estoque suficiente"""
        return self.quantidade_estoque >= quantidade
    
    def atualizar_estoque(self, quantidade: int):
        """Atualiza o estoque do produto"""
        if quantidade > self.quantidade_estoque:
            raise EstoqueInsuficienteError(f"Estoque insuficiente. Disponível: {self.quantidade_estoque}")
        self.quantidade_estoque -= quantidade
    
    def obter_informacoes(self) -> Dict:
        """Retorna informações detalhadas do produto"""
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "preco": self.preco,
            "estoque": self.quantidade_estoque,
            "categoria": self.categoria
        }

class Carrinho:
    """Classe que gerencia os itens selecionados pelo usuário"""
    
    def __init__(self):
        self.itens: Dict[int, Dict] = {}  # {produto_id: {"produto": Produto, "quantidade": int}}
    
    def adicionar_item(self, produto: Produto, quantidade: int):
        """Adiciona um item ao carrinho"""
        if not produto.verificar_disponibilidade(quantidade):
            raise EstoqueInsuficienteError("Produto sem estoque suficiente")
        
        if produto.id in self.itens:
            self.itens[produto.id]["quantidade"] += quantidade
        else:
            self.itens[produto.id] = {"produto": produto, "quantidade": quantidade}
    
    def remover_item(self, produto_id: int, quantidade: int = None):
        """Remove um item do carrinho"""
        if produto_id not in self.itens:
            return
        
        if quantidade is None or quantidade >= self.itens[produto_id]["quantidade"]:
            del self.itens[produto_id]
        else:
            self.itens[produto_id]["quantidade"] -= quantidade
    
    def calcular_valor_total(self) -> float:
        """Calcula o valor total do carrinho"""
        total = 0
        for item in self.itens.values():
            total += item["produto"].preco * item["quantidade"]
        return total
    
    def limpar_carrinho(self):
        """Limpa todos os itens do carrinho"""
        self.itens.clear()

class SistemaPagamento:
    """Classe responsável por processar transações financeiras"""
    
    def __init__(self):
        self.taxa_juros = 0.05  # 5% por parcela
        self.desconto_pix = 0.10  # 10% de desconto no PIX
    
    def calcular_valor_cartao_vista(self, valor: float) -> float:
        """Calcula valor para pagamento à vista"""
        return valor
    
    def calcular_valor_cartao_parcelado(self, valor: float, parcelas: int) -> Dict:
        """Calcula valor para pagamento parcelado"""
        if parcelas < 2 or parcelas > 12:
            raise ValueError("Número de parcelas deve ser entre 2 e 12")
        
        valor_com_juros = valor * (1 + (self.taxa_juros * (parcelas - 1)))
        valor_parcela = valor_com_juros / parcelas
        
        return {
            "valor_total": valor_com_juros,
            "valor_parcela": valor_parcela,
            "parcelas": parcelas
        }
    
    def calcular_valor_pix(self, valor: float) -> float:
        """Calcula valor para pagamento PIX com desconto"""
        return valor * (1 - self.desconto_pix)
    
    def processar_pagamento(self, valor: float, metodo: MetodoPagamento, parcelas: int = 1) -> Dict:
        """Processa o pagamento"""
        if metodo == MetodoPagamento.CARTAO_VISTA:
            valor_final = self.calcular_valor_cartao_vista(valor)
            return {"valor_final": valor_final, "aprovado": True}
        
        elif metodo == MetodoPagamento.CARTAO_PARCELADO:
            resultado = self.calcular_valor_cartao_parcelado(valor, parcelas)
            resultado["aprovado"] = True
            return resultado
        
        elif metodo == MetodoPagamento.PIX:
            valor_final = self.calcular_valor_pix(valor)
            return {"valor_final": valor_final, "aprovado": True}

class Pedido:
    """Classe que representa uma compra finalizada"""
    
    def __init__(self, id_pedido: str, itens: Dict, metodo_pagamento: MetodoPagamento, 
                 valor_total: float, endereco_entrega: str):
        self.id_pedido = id_pedido
        self.itens = itens
        self.metodo_pagamento = metodo_pagamento
        self.valor_total = valor_total
        self.endereco_entrega = endereco_entrega
        self.status = StatusPedido.PENDENTE
        self.data_criacao = datetime.now()
        self.data_pagamento = None
        self.data_envio = None
    
    def atualizar_status(self, novo_status: StatusPedido):
        """Atualiza o status do pedido com validações"""
        transicoes_validas = {
            StatusPedido.PENDENTE: [StatusPedido.PAGO, StatusPedido.CANCELADO],
            StatusPedido.PAGO: [StatusPedido.ENVIADO, StatusPedido.CANCELADO],
            StatusPedido.ENVIADO: [StatusPedido.ENTREGUE],
            StatusPedido.ENTREGUE: [],
            StatusPedido.CANCELADO: []
        }
        
        if novo_status not in transicoes_validas[self.status]:
            raise TransicaoInvalidaError(f"Não é possível ir de {self.status.value} para {novo_status.value}")
        
        self.status = novo_status
        
        if novo_status == StatusPedido.PAGO:
            self.data_pagamento = datetime.now()
        elif novo_status == StatusPedido.ENVIADO:
            self.data_envio = datetime.now()

class SistemaEcommerce:
    """Classe principal que integra todas as outras classes"""
    
    def __init__(self):
        self.produtos: Dict[int, Produto] = {}
        self.pedidos: Dict[str, Pedido] = {}
        self.sistema_pagamento = SistemaPagamento()
    
    def adicionar_produto(self, produto: Produto):
        """Adiciona um produto ao catálogo"""
        self.produtos[produto.id] = produto
    
    def obter_produto(self, produto_id: int) -> Optional[Produto]:
        """Recupera um produto pelo ID"""
        return self.produtos.get(produto_id)
    
    def criar_pedido(self, carrinho: Carrinho, metodo_pagamento: MetodoPagamento, 
                     endereco_entrega: str, parcelas: int = 1) -> str:
        """Cria um novo pedido"""
        if not carrinho.itens:
            raise ValueError("Carrinho vazio")
        
        valor_total = carrinho.calcular_valor_total()
        id_pedido = str(uuid.uuid4())
        
        # Cria o pedido
        pedido = Pedido(id_pedido, carrinho.itens.copy(), metodo_pagamento, 
                       valor_total, endereco_entrega)
        
        # Processa pagamento
        resultado_pagamento = self.sistema_pagamento.processar_pagamento(
            valor_total, metodo_pagamento, parcelas)
        
        if resultado_pagamento["aprovado"]:
            # Atualiza estoque dos produtos
            for item in carrinho.itens.values():
                item["produto"].atualizar_estoque(item["quantidade"])
            
            # Atualiza status do pedido
            pedido.atualizar_status(StatusPedido.PAGO)
            
            # Armazena o pedido
            self.pedidos[id_pedido] = pedido
            
            # Limpa o carrinho
            carrinho.limpar_carrinho()
            
            return id_pedido
        else:
            raise Exception("Falha no processamento do pagamento")
    
    def cancelar_pedido(self, id_pedido: str):
        """Cancela um pedido e reabastece o estoque"""
        if id_pedido not in self.pedidos:
            raise ValueError("Pedido não encontrado")
        
        pedido = self.pedidos[id_pedido]
        
        # Reabastece o estoque
        for item in pedido.itens.values():
            item["produto"].quantidade_estoque += item["quantidade"]
        
        # Atualiza status
        pedido.atualizar_status(StatusPedido.CANCELADO)
    
    def obter_pedido(self, id_pedido: str) -> Optional[Pedido]:
        """Recupera um pedido pelo ID"""
        return self.pedidos.get(id_pedido)
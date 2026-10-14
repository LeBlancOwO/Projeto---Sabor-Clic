class Carrinho:
    def __init__(self, id, cliente_id, status="Aguardando"):
        self.id = id
        self.cliente_id = cliente_id
        self.status = status

def listar_pedidos():
    pedidos = [{"id": 1, "nome": "Cupcake", "Valor": 8.00}]
    return (pedidos)

def criar_pedido():
    pass
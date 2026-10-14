class Prato:
    def __init__(self, id, nome, descricao, preco, ativo=True):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.ativo = ativo

def listar_pratos():
    pratos = [{"id": 1, "nome": "Pizza", "preco": 40.0}]
    return (pratos)

#def criar_prato():
#    dados = request.json
#    return jsonify({"status": "Prato criado", "dados": dados})
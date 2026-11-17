from flask import Blueprint, request, jsonify, session
from app.models.pedido import Pedido
from app.models.log import Log
from app.controllers.decorators import login_required

carrinho_bp = Blueprint("carrinho_api", __name__, url_prefix="/api/carrinho")

@carrinho_bp.route("/", methods=["GET"])
@login_required
def obter_carrinho():
    carrinho = session.get("carrinho", [])
    pedidos = Pedido.listar(cliente_id=session["usuario"]["id"])
    return jsonify({"sucesso": True, "carrinho": carrinho, "pedidos": pedidos})

@carrinho_bp.route("/adicionar", methods=["POST"])
@login_required
def adicionar_item():
    item = request.get_json()
    carrinho = session.get("carrinho", [])
    
    for c in carrinho:
        if c["id"] == item["id"]:
            c["quantidade"] += 1
            break
    else:
        carrinho.append({
            "id": item["id"],
            "nome_prato": item["nome_prato"],
            "valor_unitario": float(item["valor_unitario"]),
            "quantidade": 1
        })
        
    session["carrinho"] = carrinho
    session.modified = True
    return jsonify({"sucesso": True, "carrinho": carrinho})

@carrinho_bp.route("/remover/<int:item_id>", methods=["DELETE"])
@login_required
def remover_item(item_id):
    carrinho = [c for c in session.get("carrinho", []) if c["id"] != item_id]
    session["carrinho"] = carrinho
    session.modified = True
    return jsonify({"sucesso": True, "carrinho": carrinho})

@carrinho_bp.route("/finalizar", methods=["POST"])
@login_required
def finalizar_pedido():
    carrinho = session.get("carrinho", [])
    if not carrinho:
        return jsonify({"sucesso": False, "mensagem": "Carrinho vazio."}), 400

    total = sum(i["valor_unitario"] * i["quantidade"] for i in carrinho)
    usuario = session["usuario"]
    
    pedido_id = Pedido.criar(usuario["id"], usuario["nome"], carrinho, total)
    session["carrinho"] = []
    session.modified = True
    
    Log.registrar(usuario["nome"], usuario["nivel_acesso"], f"Finalizou pedido #{pedido_id} (R$ {total:.2f})")
    return jsonify({"sucesso": True, "pedido_id": pedido_id})
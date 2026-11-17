from flask import Blueprint, request, jsonify, session
from app.models.pedido import Pedido
from app.models.log import Log

pedido_bp = Blueprint("pedido_api", __name__, url_prefix="/api/pedidos")

@pedido_bp.route("/criar", methods=["POST"])
def criar():
    usuario = session.get("usuario")
    if not usuario:
        return jsonify({"sucesso": False, "mensagem": "Faça login para finalizar o seu pedido."}), 401

    dados = request.get_json()
    itens = dados.get("itens", "")
    valor_total = dados.get("valor_total", 0)
    produtos = dados.get("produtos", [])

    if not itens:
        return jsonify({"sucesso": False, "mensagem": "Seu carrinho está vazio."}), 400

    Pedido.criar(usuario["id"], itens, valor_total, produtos)
    Log.registrar(usuario["nome"], usuario["nivel_acesso"], f"Realizou pedido: {itens} (R$ {float(valor_total):.2f})")
    return jsonify({"sucesso": True, "mensagem": "Pedido enviado para a cozinha com sucesso!"}), 201

@pedido_bp.route("/meus", methods=["GET"])
def meus_pedidos():
    usuario = session.get("usuario")
    if not usuario:
        return jsonify({"pedidos": []})
    return jsonify({"pedidos": Pedido.listar_por_usuario(usuario["id"])})

@pedido_bp.route("/listar", methods=["GET"])
def listar_todos():
    usuario = session.get("usuario")
    if not usuario or usuario.get("nivel_acesso") not in ("cozinheiro", "administrador"):
        return jsonify({"sucesso": False}), 403
    return jsonify({"pedidos": Pedido.listar_todos()})

@pedido_bp.route("/status/<int:pedido_id>", methods=["PUT"])
def mudar_status(pedido_id):
    usuario = session.get("usuario")
    if not usuario or usuario.get("nivel_acesso") not in ("cozinheiro", "administrador"):
        return jsonify({"sucesso": False}), 403
    dados = request.get_json()
    Pedido.atualizar_status(pedido_id, dados.get("status"))
    return jsonify({"sucesso": True})
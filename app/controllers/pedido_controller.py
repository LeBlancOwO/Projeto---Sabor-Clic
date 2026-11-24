from flask import Blueprint, request, jsonify, session
from app.models.pedido import Pedido, ErroPedido
from app.models.log import Log
from app.controllers.decorators import nivel_requerido

pedido_bp = Blueprint("pedido_api", __name__, url_prefix="/api/pedidos")


@pedido_bp.route("/criar", methods=["POST"])
def criar():
    usuario = session.get("usuario")
    if not usuario:
        return jsonify({"sucesso": False, "mensagem": "Faça login para finalizar o seu pedido."}), 401

    dados = request.get_json(silent=True) or {}
    produtos = dados.get("produtos")
    if not isinstance(produtos, list):
        produtos = []

    try:
        pedido_id, total, itens = Pedido.criar(
            usuario["id"],
            produtos,
            dados.get("tipo_entrega", "Retirada"),
            dados.get("endereco_entrega", ""),
        )
    except ErroPedido as e:
        return jsonify({"sucesso": False, "mensagem": str(e)}), 400

    Log.registrar(usuario["nome"], usuario["nivel_acesso"],
                  f"Pedido #{pedido_id} ({dados.get('tipo_entrega', 'Retirada')}): {itens} - R$ {total:.2f}")
    return jsonify({"sucesso": True, "mensagem": "Pedido enviado para a Dark Kitchen!", "total": total}), 201


@pedido_bp.route("/meus", methods=["GET"])
def meus_pedidos():
    usuario = session.get("usuario")
    if not usuario:
        return jsonify({"pedidos": []})
    return jsonify({"pedidos": Pedido.listar_por_usuario(usuario["id"])})


@pedido_bp.route("/listar", methods=["GET"])
@nivel_requerido("cozinheiro", "administrador")
def listar_todos():
    return jsonify({"pedidos": Pedido.listar_todos()})


@pedido_bp.route("/status/<int:pedido_id>", methods=["PUT"])
@nivel_requerido("cozinheiro", "administrador")
def mudar_status(pedido_id):
    dados = request.get_json(silent=True) or {}
    if not Pedido.atualizar_status(pedido_id, dados.get("status")):
        return jsonify({"sucesso": False, "mensagem": "Status inválido."}), 400
    return jsonify({"sucesso": True})
from flask import Blueprint, request, jsonify, session
from app.models.estoque import Estoque
from app.models.buffet import Buffet
from app.models.log import Log

cozinha_bp = Blueprint("cozinha_api", __name__, url_prefix="/api/cozinha")

def is_equipe():
    u = session.get("usuario")
    return u and u.get("nivel_acesso") in ("cozinheiro", "administrador")

@cozinha_bp.route("/estoque", methods=["GET"])
def listar_estoque():
    if not is_equipe():
        return jsonify({"sucesso": False}), 403
    return jsonify({"estoque": Estoque.listar()})

@cozinha_bp.route("/estoque", methods=["POST"])
def salvar_estoque():
    if not is_equipe():
        return jsonify({"sucesso": False}), 403
    dados = request.get_json()
    Estoque.salvar(dados["insumo"], dados["quantidade"], dados["unidade"])
    u = session.get("usuario")
    Log.registrar(u["nome"], u["nivel_acesso"], f"Adicionou insumo: {dados['insumo']} ({dados['quantidade']} {dados['unidade']})")
    return jsonify({"sucesso": True, "mensagem": "Insumo salvo no estoque!"})

@cozinha_bp.route("/estoque/<int:item_id>", methods=["DELETE"])
def remover_estoque(item_id):
    if not is_equipe():
        return jsonify({"sucesso": False}), 403
    Estoque.remover(item_id)
    return jsonify({"sucesso": True, "mensagem": "Insumo removido."})

@cozinha_bp.route("/reservas", methods=["GET"])
def listar_reservas_cozinha():
    if not is_equipe():
        return jsonify({"sucesso": False}), 403
    return jsonify({"reservas": Buffet.listar_todas()})
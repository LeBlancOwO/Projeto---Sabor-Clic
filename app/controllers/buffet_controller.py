from flask import Blueprint, request, jsonify, session
from app.models.buffet import Buffet
from app.models.log import Log

buffet_bp = Blueprint("buffet_api", __name__, url_prefix="/api/buffet")

@buffet_bp.route("/datas-ocupadas", methods=["GET"])
def datas_ocupadas():
    mes = request.args.get("mes")
    ocupadas = Buffet.listar_datas_ocupadas(mes)
    return jsonify({"ocupadas": ocupadas})

@buffet_bp.route("/reservar", methods=["POST"])
def reservar():
    usuario = session.get("usuario")
    if not usuario:
        return jsonify({"sucesso": False, "mensagem": "Faça login para reservar um buffet."}), 401

    dados = request.get_json()
    resultado = Buffet.reservar(
        usuario["id"],
        dados["data_evento"],
        dados["tipo_evento"],
        dados["qtd_convidados"]
    )

    if resultado["sucesso"]:
        Log.registrar(usuario["nome"], usuario["nivel_acesso"], f"Reservou buffet para {dados['data_evento']}")
        return jsonify(resultado), 201
    return jsonify(resultado), 400
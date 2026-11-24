from flask import Blueprint, request, jsonify, session
from app.models.buffet import Buffet
from app.models.log import Log

buffet_bp = Blueprint("buffet_api", __name__, url_prefix="/api/buffet")


@buffet_bp.route("/datas-ocupadas", methods=["GET"])
def datas_ocupadas():
    ocupadas = Buffet.listar_datas_ocupadas(request.args.get("mes"))
    return jsonify({"ocupadas": ocupadas})


@buffet_bp.route("/reservar", methods=["POST"])
def reservar():
    usuario = session.get("usuario")
    if not usuario:
        return jsonify({"sucesso": False, "mensagem": "Faça login para reservar a cozinha."}), 401

    dados = request.get_json(silent=True) or {}
    data_evento = str(dados.get("data_evento", "")).strip()
    tipo_evento = str(dados.get("tipo_evento", "")).strip()

    if not data_evento or not tipo_evento:
        return jsonify({"sucesso": False, "mensagem": "Preencha todos os dados da reserva."}), 400

    # Datas, limites e conflitos são validados no model
    resultado = Buffet.reservar(usuario["id"], data_evento, tipo_evento, dados.get("qtd_convidados", 1))

    if resultado["sucesso"]:
        Log.registrar(usuario["nome"], usuario["nivel_acesso"],
                      f"Reservou cozinha para {data_evento[:10]} ({tipo_evento[:80]})")
        return jsonify(resultado), 201
    return jsonify(resultado), 400
import math
from flask import Blueprint, request, jsonify, session
from app.models.estoque import Estoque
from app.models.buffet import Buffet
from app.models.log import Log
from app.controllers.decorators import nivel_requerido

cozinha_bp = Blueprint("cozinha_api", __name__, url_prefix="/api/cozinha")

# Todas as rotas da cozinha: só cozinheiro ou administrador
cozinha_bp.before_request(nivel_requerido("cozinheiro", "administrador")(lambda: None))


def resposta(sucesso, mensagem, codigo=200):
    return jsonify({"sucesso": sucesso, "mensagem": mensagem}), codigo


def ler_quantidade(valor):
    """Converte para float válido (>= 0) ou retorna None."""
    try:
        qtd = float(valor)
    except (ValueError, TypeError):
        return None
    if not math.isfinite(qtd) or qtd < 0:
        return None
    return qtd


@cozinha_bp.route("/estoque", methods=["GET"])
def listar_estoque():
    return jsonify({"estoque": Estoque.listar()})


@cozinha_bp.route("/estoque", methods=["POST"])
def salvar_estoque():
    dados = request.get_json(silent=True) or {}
    insumo = str(dados.get("insumo", "")).strip()[:80]
    unidade = str(dados.get("unidade", "")).strip()[:20]
    qtd = ler_quantidade(dados.get("quantidade", 0))

    if qtd is None:
        return resposta(False, "Quantidade inválida.", 400)
    if not insumo or not unidade:
        return resposta(False, "Preencha insumo, quantidade e unidade.", 400)

    Estoque.salvar(insumo, qtd, unidade)
    u = session["usuario"]
    Log.registrar(u["nome"], u["nivel_acesso"], f"Adicionou insumo: {insumo} ({qtd} {unidade})")
    return resposta(True, "Insumo salvo no estoque!")


@cozinha_bp.route("/estoque/<int:item_id>", methods=["PUT"])
def atualizar_estoque(item_id):
    dados = request.get_json(silent=True) or {}
    qtd = ler_quantidade(dados.get("quantidade"))
    if qtd is None:
        return resposta(False, "Quantidade inválida.", 400)

    Estoque.atualizar_quantidade(item_id, qtd)
    u = session["usuario"]
    Log.registrar(u["nome"], u["nivel_acesso"], f"Atualizou quantidade do insumo #{item_id} para {qtd}")
    return resposta(True, "Quantidade do insumo atualizada!")


@cozinha_bp.route("/estoque/<int:item_id>", methods=["DELETE"])
def remover_estoque(item_id):
    Estoque.remover(item_id)
    u = session["usuario"]
    Log.registrar(u["nome"], u["nivel_acesso"], f"Removeu o insumo #{item_id} do estoque")
    return resposta(True, "Insumo removido.")


@cozinha_bp.route("/reservas", methods=["GET"])
def listar_reservas_cozinha():
    return jsonify({"reservas": Buffet.listar_todas()})
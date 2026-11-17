from flask import Blueprint, request, jsonify, session
from app.models.cadastro import Cadastro
from app.models.buffet import Buffet
from app.models.log import Log
from app.utils.email_service import enviar_email_cancelamento

admin_bp = Blueprint("admin_api", __name__, url_prefix="/api/admin")

def is_admin():
    u = session.get("usuario")
    return u and u.get("nivel_acesso") == "administrador"

@admin_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    if not is_admin():
        return jsonify({"sucesso": False}), 403
    return jsonify({"usuarios": Cadastro.listar_todos()})

@admin_bp.route("/usuarios/<int:usuario_id>/cargo", methods=["PUT"])
def alterar_cargo(usuario_id):
    if not is_admin():
        return jsonify({"sucesso": False}), 403
    dados = request.get_json()
    novo_nivel = dados.get("nivel_acesso")
    if Cadastro.alterar_nivel(usuario_id, novo_nivel):
        admin_logado = session.get("usuario")
        Log.registrar(admin_logado["nome"], "administrador", f"Alterou cargo do usuário #{usuario_id} para {novo_nivel}")
        return jsonify({"sucesso": True, "mensagem": f"Cargo atualizado para {novo_nivel}!"})
    return jsonify({"sucesso": False, "mensagem": "Cargo inválido."}), 400

@admin_bp.route("/reservas", methods=["GET"])
def listar_reservas():
    if not is_admin():
        return jsonify({"sucesso": False}), 403
    return jsonify({"reservas": Buffet.listar_todas()})

@admin_bp.route("/reservas/<int:reserva_id>/cancelar", methods=["DELETE"])
def cancelar_reserva(reserva_id):
    if not is_admin():
        return jsonify({"sucesso": False}), 403
    dados_reserva = Buffet.cancelar_reserva(reserva_id)
    if not dados_reserva:
        return jsonify({"sucesso": False, "mensagem": "Reserva não encontrada."}), 404

    enviado = enviar_email_cancelamento(
        dados_reserva["cliente_email"],
        dados_reserva["cliente_nome"],
        dados_reserva["data_evento"],
        dados_reserva["tipo_evento"]
    )
    admin_logado = session.get("usuario")
    Log.registrar(admin_logado["nome"], "administrador", f"Cancelou reserva de {dados_reserva['cliente_nome']} ({dados_reserva['data_evento']})")

    aviso_email = "E-mail enviado ao cliente!" if enviado else "Data liberada (e-mail registrado no log do servidor)."
    return jsonify({"sucesso": True, "mensagem": f"Reserva cancelada! {aviso_email}"})

@admin_bp.route("/bloqueios", methods=["GET"])
def listar_bloqueios():
    if not is_admin():
        return jsonify({"sucesso": False}), 403
    return jsonify({"bloqueios": Buffet.listar_bloqueios()})

@admin_bp.route("/bloqueios", methods=["POST"])
def criar_bloqueio():
    if not is_admin():
        return jsonify({"sucesso": False}), 403
    dados = request.get_json()
    if Buffet.bloquear_data(dados.get("data_bloqueada"), dados.get("motivo")):
        return jsonify({"sucesso": True, "mensagem": "Data removida da agenda dos clientes!"})
    return jsonify({"sucesso": False, "mensagem": "Essa data já está bloqueada."}), 400

@admin_bp.route("/bloqueios/<int:bloqueio_id>", methods=["DELETE"])
def remover_bloqueio(bloqueio_id):
    if not is_admin():
        return jsonify({"sucesso": False}), 403
    Buffet.desbloquear_data(bloqueio_id)
    return jsonify({"sucesso": True, "mensagem": "Data liberada novamente para os clientes!"})

@admin_bp.route("/logs", methods=["GET"])
def logs():
    if not is_admin():
        return jsonify({"sucesso": False}), 403
    return jsonify({"logs": Log.listar_recentes()})
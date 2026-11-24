import sqlite3
import threading
from flask import Blueprint, request, jsonify, session, Response
from app.models.cadastro import Cadastro
from app.models.buffet import Buffet
from app.models.log import Log
from app.utils import email_service
from app.controllers.decorators import nivel_requerido

admin_bp = Blueprint("admin_api", __name__, url_prefix="/api/admin")

# Protege TODAS as rotas deste blueprint (inclusive as que você criar depois).
# O decorator responde 401/403 sozinho; se passar, a função vazia deixa a rota seguir.
admin_bp.before_request(nivel_requerido("administrador")(lambda: None))


def resposta(sucesso, mensagem, codigo=200, **extra):
    return jsonify({"sucesso": sucesso, "mensagem": mensagem, **extra}), codigo


@admin_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    return jsonify({"usuarios": Cadastro.listar_todos()})


@admin_bp.route("/usuarios/<int:usuario_id>/cargo", methods=["PUT"])
def alterar_cargo(usuario_id):
    dados = request.get_json(silent=True) or {}
    novo_nivel = dados.get("nivel_acesso")
    admin_logado = session["usuario"]

    if usuario_id == admin_logado["id"] and novo_nivel != "administrador":
        return resposta(False, "Você não pode remover o seu próprio acesso de administrador.", 400)

    try:
        if Cadastro.alterar_nivel(usuario_id, novo_nivel):
            Log.registrar(admin_logado["nome"], "administrador",
                          f"Alterou cargo do usuário #{usuario_id} para {novo_nivel}")
            return resposta(True, f"Cargo atualizado para {novo_nivel}!")
    except sqlite3.IntegrityError as e:
        return resposta(False, str(e), 400)

    return resposta(False, "Cargo inválido.", 400)


@admin_bp.route("/reservas", methods=["GET"])
def listar_reservas():
    return jsonify({"reservas": Buffet.listar_todas()})


@admin_bp.route("/reservas/<int:reserva_id>/cancelar", methods=["DELETE"])
def cancelar_reserva(reserva_id):
    reserva = Buffet.cancelar_reserva(reserva_id)
    if not reserva:
        return resposta(False, "Reserva não encontrada.", 404)

    # Envia o e-mail em segundo plano (o SMTP pode demorar ou travar)
    threading.Thread(
        target=email_service.enviar_email_cancelamento,
        args=(reserva["cliente_email"], reserva["cliente_nome"],
              reserva["data_evento"], reserva["tipo_evento"]),
        daemon=True
    ).start()

    admin_logado = session["usuario"]
    Log.registrar(admin_logado["nome"], "administrador",
                  f"Cancelou reserva de cozinha de {reserva['cliente_nome']} ({reserva['data_evento']})")

    email_configurado = bool(email_service.EMAIL_REMETENTE and email_service.SENHA_APP_GMAIL)
    aviso = ("O cliente está sendo avisado por e-mail."
             if email_configurado else
             "Data liberada (e-mail simulado no terminal do servidor).")
    return resposta(True, f"Reserva de cozinha cancelada! {aviso}")


@admin_bp.route("/bloqueios", methods=["GET"])
def listar_bloqueios():
    return jsonify({"bloqueios": Buffet.listar_bloqueios()})


@admin_bp.route("/bloqueios", methods=["POST"])
def criar_bloqueio():
    dados = request.get_json(silent=True) or {}
    ok, mensagem = Buffet.bloquear_data(dados.get("data_bloqueada"), dados.get("motivo"))
    if not ok:
        return resposta(False, mensagem, 400)

    admin_logado = session["usuario"]
    Log.registrar(admin_logado["nome"], "administrador",
                  f"Bloqueou a data {str(dados.get('data_bloqueada'))[:10]} na agenda da cozinha")
    return resposta(True, mensagem)


@admin_bp.route("/bloqueios/<int:bloqueio_id>", methods=["DELETE"])
def remover_bloqueio(bloqueio_id):
    Buffet.desbloquear_data(bloqueio_id)
    admin_logado = session["usuario"]
    Log.registrar(admin_logado["nome"], "administrador", f"Liberou o bloqueio de data #{bloqueio_id}")
    return resposta(True, "Data liberada novamente!")


@admin_bp.route("/logs", methods=["GET"])
def logs():
    return jsonify({"logs": Log.listar_recentes()})


@admin_bp.route("/logs/download", methods=["GET"])
def baixar_logs_txt():
    conteudo = Log.gerar_conteudo_txt()
    return Response(
        conteudo,
        mimetype="text/plain; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=logs_auditoria_sabor_clic.txt"}
    )
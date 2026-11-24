import re
import time
from flask import Blueprint, request, jsonify, session, make_response
from app.models.cadastro import Cadastro
from app.models.log import Log

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# ----- Limite simples de tentativas de login (em memória) -----
LIMITE_TENTATIVAS = 5
JANELA_SEGUNDOS = 300
_falhas_login = {}


def _chave_login(identificador):
    return f"{request.remote_addr}|{identificador.lower()}"


def _login_bloqueado(chave):
    agora = time.time()
    recentes = [t for t in _falhas_login.get(chave, []) if agora - t < JANELA_SEGUNDOS]
    if recentes:
        _falhas_login[chave] = recentes
    else:
        _falhas_login.pop(chave, None)
    return len(recentes) >= LIMITE_TENTATIVAS


def _registrar_falha(chave):
    _falhas_login.setdefault(chave, []).append(time.time())


def texto_seguro(valor, max_len=120):
    if not isinstance(valor, str):
        return ""
    limpo = re.sub(r"[\x00-\x1f\x7f]", "", valor).strip()
    return limpo[:max_len]


def senha_texto(valor):
    return valor if isinstance(valor, str) else ""


@auth_bp.route("/cadastrar", methods=["POST"])
def cadastrar():
    dados = request.get_json(silent=True) or {}
    usuario_logado = session.get("usuario")

    nivel_desejado = texto_seguro(dados.get("nivel_acesso", "cliente"), 20).lower()
    if nivel_desejado in ("cozinheiro", "administrador"):
        if not usuario_logado or usuario_logado["nivel_acesso"] != "administrador":
            return jsonify({"sucesso": False, "mensagem": "Apenas administradores criam contas de equipe."}), 403

    senha = senha_texto(dados.get("senha", ""))
    if len(senha.encode("utf-8")) > 72:
        return jsonify({"sucesso": False, "mensagem": "A senha deve ter no máximo 72 caracteres."}), 400

    novo = Cadastro(
        texto_seguro(dados.get("nome", ""), 100),
        texto_seguro(dados.get("usuario", ""), 50),
        texto_seguro(dados.get("email", ""), 100),
        texto_seguro(dados.get("cpf", ""), 14),
        senha,
        nivel_desejado
    )
    resultado = novo.salvar()

    if resultado["sucesso"]:
        ator = usuario_logado["nome"] if usuario_logado else novo.nome
        Log.registrar(ator, nivel_desejado, f"Cadastrou @{novo.usuario} ({nivel_desejado})")
        return jsonify(resultado), 201
    return jsonify(resultado), 400


@auth_bp.route("/logar", methods=["POST"])
def logar():
    dados = request.get_json(silent=True) or {}
    identificador = texto_seguro(dados.get("identificador", ""), 100)
    senha = senha_texto(dados.get("senha", ""))

    chave = _chave_login(identificador)
    if _login_bloqueado(chave):
        return jsonify({
            "sucesso": False,
            "mensagem": "Muitas tentativas de login. Aguarde alguns minutos e tente novamente."
        }), 429

    usuario = None
    if identificador and senha and len(senha.encode("utf-8")) <= 72:
        usuario = Cadastro.autenticar(identificador, senha)

    if not usuario:
        _registrar_falha(chave)
        return jsonify({"sucesso": False, "mensagem": "Usuário/E-mail ou senha inválidos."}), 401

    _falhas_login.pop(chave, None)

    session.clear()  # evita reaproveitar uma sessão antiga
    session.permanent = True
    session["usuario"] = {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "usuario": usuario["usuario"],
        "email": usuario["email"],
        "nivel_acesso": usuario["nivel_acesso"]
    }

    Log.registrar(usuario["nome"], usuario["nivel_acesso"], "Realizou login no sistema")
    return jsonify({"sucesso": True, "usuario": session["usuario"]})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    usuario = session.get("usuario")
    if usuario:
        Log.registrar(usuario["nome"], usuario["nivel_acesso"], "Saiu do sistema")
    session.clear()
    resp = make_response(jsonify({"sucesso": True}))
    resp.delete_cookie("pref_usuario_nome")  # limpa o cookie antigo, que não existe mais
    return resp


@auth_bp.route("/preferencias", methods=["POST"])
def salvar_preferencias():
    dados = request.get_json(silent=True) or {}
    tema = dados.get("tema", "claro")
    if tema not in ("claro", "escuro"):
        tema = "claro"
    resp = make_response(jsonify({"sucesso": True, "tema": tema}))
    resp.set_cookie(
        "tema_preferido",
        tema,
        max_age=60 * 60 * 24 * 365,
        httponly=True,
        samesite="Lax"
    )
    return resp
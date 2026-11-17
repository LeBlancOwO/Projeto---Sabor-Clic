from flask import Blueprint, request, jsonify, session, make_response
from app.models.cadastro import Cadastro
from app.models.log import Log

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/cadastrar", methods=["POST"])
def cadastrar():
    dados = request.get_json()
    usuario_logado = session.get("usuario")
    
    nivel_desejado = dados.get("nivel_acesso", "cliente").lower()
    if nivel_desejado in ("cozinheiro", "administrador"):
        if not usuario_logado or usuario_logado["nivel_acesso"] != "administrador":
            return jsonify({"sucesso": False, "mensagem": "Apenas administradores criam contas de equipe."}), 403

    novo = Cadastro(
        dados["nome"],
        dados["usuario"],
        dados["email"],
        dados["cpf"],
        dados["senha"],
        nivel_desejado
    )
    resultado = novo.salvar()

    if resultado["sucesso"]:
        ator = usuario_logado["nome"] if usuario_logado else dados["nome"]
        Log.registrar(ator, nivel_desejado, f"Cadastrou @{dados['usuario']} ({nivel_desejado})")
        return jsonify(resultado), 201
    return jsonify(resultado), 400

@auth_bp.route("/logar", methods=["POST"])
def logar():
    dados = request.get_json()
    usuario = Cadastro.autenticar(dados["identificador"], dados["senha"])

    if not usuario:
        return jsonify({"sucesso": False, "mensagem": "Usuário/E-mail ou senha inválidos."}), 401

    session["usuario"] = {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "usuario": usuario["usuario"],
        "email": usuario["email"],
        "nivel_acesso": usuario["nivel_acesso"]
    }
    session.setdefault("carrinho", [])

    Log.registrar(usuario["nome"], usuario["nivel_acesso"], "Realizou login no sistema")
    
    resp = make_response(jsonify({"sucesso": True, "usuario": session["usuario"]}))
    resp.set_cookie("pref_usuario_nome", usuario["nome"], max_age=60*60*24*30)
    return resp

@auth_bp.route("/logout", methods=["POST"])
def logout():
    usuario = session.get("usuario")
    if usuario:
        Log.registrar(usuario["nome"], usuario["nivel_acesso"], "Saiu do sistema")
    session.clear()
    return jsonify({"sucesso": True})

@auth_bp.route("/preferencias", methods=["POST"])
def salvar_preferencias():
    dados = request.get_json()
    tema = dados.get("tema", "claro")
    resp = make_response(jsonify({"sucesso": True, "tema": tema}))
    resp.set_cookie("tema_preferido", tema, max_age=60*60*24*365)
    return resp
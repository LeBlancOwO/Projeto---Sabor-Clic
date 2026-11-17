from flask import Blueprint, request, jsonify
from app.models.cadastro import Cadastro

login_bp = Blueprint("login", __name__, url_prefix="/api/login")

@login_bp.route("/logar", methods = ["POST"])
def Login():

    dados = request.get_json()

    usuario = Cadastro.Autenticar(
        dados["email"],
        dados["cpf"],
        dados["senha"]
    )

    if not usuario:
        return jsonify({"sucesso": False, "mensagem": "Login inválido"}), 401
    return jsonify ({"sucesso": True, "usuario": {
                        "id": usuario[0],
                        "nome": usuario[1],
                        "email": usuario[2],
                        "nivel_acesso": usuario[5]
                        }
                     })
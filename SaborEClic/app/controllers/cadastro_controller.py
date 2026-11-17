from flask import Blueprint, request, jsonify
from app.models.cadastro import Cadastro

cadastro_bp = Blueprint("cadastro", __name__, url_prefix="/api/cadastro")

@cadastro_bp.route("/cadastrar", methods = ["POST"])
def Cadastrar():
    
    dados = request.get_json()

    usuario = Cadastro(
        dados["nome"],
        dados["email"],
        dados["cpf"],
        dados["senha"],
        dados["nivel_acesso"]
    )

    resultado = usuario.Salvar()

    if resultado["sucesso"]:
        return jsonify(resultado), 201
    return jsonify(resultado),400
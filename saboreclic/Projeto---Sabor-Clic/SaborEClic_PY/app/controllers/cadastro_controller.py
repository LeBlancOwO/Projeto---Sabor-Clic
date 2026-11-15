from flask import Blueprint, render_template, request, redirect
from app.models.cadastro import Cadastro

cadastro_bp = Blueprint("cadastro", __name__, url_prefix="/cadastro")

@cadastro_bp.route('/')
def renderizar_cadastro():
    return render_template ("cadastro.html")

@cadastro_bp.route('/cadastrar', methods = ["POST"])
def Cadastrar():
    nome = request.form["nome"]
    email = request.form["email"]
    cpf = request.form["cpf"]
    senha = request.form["senha"]
    nivel_acesso = request.form["nivel_acesso"]

    cadastro = Cadastro(
        nome,
        email,
        cpf,
        senha,
        nivel_acesso
    )

    cadastro.Salvar()

    return redirect("/")
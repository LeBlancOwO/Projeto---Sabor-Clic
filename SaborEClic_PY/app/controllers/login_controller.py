from flask import Blueprint, render_template, request, redirect
from app.models.cadastro import Cadastro

login_bp = Blueprint("login", __name__, url_prefix="/login")

@login_bp.route('/')
def renderizar_login():
    return render_template ("login.html")

@login_bp.route("/logar", methods = ["POST"])
def Login():
    email = request.form["email"]
    cpf = request.form["cpf"]
    senha = request.form["senha"]
    nivel_acesso = request.form["nivel_acesso"]

    cadastro = Cadastro.Autenticar(
        email,
        cpf,
        senha,
        nivel_acesso
    )

    if cadastro:
        return render_template(
            "layout.html",
            cadastro = cadastro
        )

    return "Login inválido"
from flask import Blueprint, render_template, session, redirect, url_for

views_bp = Blueprint("views", __name__)

@views_bp.route("/")
def index():
    return render_template("layout.html")

@views_bp.route("/login")
def login():
    return render_template("login.html")

@views_bp.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@views_bp.route("/cardapio")
def cardapio():
    return render_template("cardapio.html")

@views_bp.route("/carrinho")
def carrinho():
    if "usuario" not in session:
        return redirect(url_for("views.login"))
    return render_template("carrinho.html")

@views_bp.route("/servicos")
def servicos():
    if "usuario" not in session:
        return redirect(url_for("views.login"))
    return render_template("servicos.html")

@views_bp.route("/cozinha")
def painel_cozinha():
    usuario = session.get("usuario")
    if not usuario:
        return redirect(url_for("views.login"))
    if usuario["nivel_acesso"] not in ("cozinheiro", "administrador"):
        return redirect(url_for("views.cardapio"))
    return render_template("painel_cozinha.html")

@views_bp.route("/admin")
def painel_admin():
    usuario = session.get("usuario")
    if not usuario:
        return redirect(url_for("views.login"))
    if usuario["nivel_acesso"] != "administrador":
        return redirect(url_for("views.cardapio"))
    return render_template("painel_admin.html")
from flask import Blueprint, render_template
from app.controllers.decorators import login_required, nivel_requerido

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
@login_required
def carrinho():
    return render_template("carrinho.html")


@views_bp.route("/servicos")
@login_required
def servicos():
    return render_template("servicos.html")


@views_bp.route("/cozinha")
@nivel_requerido("cozinheiro", "administrador")
def painel_cozinha():
    return render_template("painel_cozinha.html")


@views_bp.route("/admin")
@nivel_requerido("administrador")
def painel_admin():
    return render_template("painel_admin.html")


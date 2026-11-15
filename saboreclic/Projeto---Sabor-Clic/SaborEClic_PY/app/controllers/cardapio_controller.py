from flask import Blueprint, render_template, request, redirect
from app.models.cardapio import Cardapio

cardapio_bp = Blueprint("cardapio", __name__, url_prefix="/cardapio")

@cardapio_bp.route('/')
def renderizar_cardapio():
        pratos = Cardapio.Listar()
        return render_template("cardapio.html", pratos = pratos)

@cardapio_bp.route("/novo")
def novo_prato():
      return render_template("adicionar_prato.html")

@cardapio_bp.route("/adicionar", methods = ["POST"])
def adicionar_prato():
    nome_prato = request.form["nome_prato"]
    ingredientes = request.form["ingredientes"]
    valor_unitario = request.form["valor_unitario"]

    cardapio = Cardapio(
        nome_prato,
        ingredientes,
        valor_unitario
    )

    cardapio.Salvar()

    return redirect ("/cardapio/")
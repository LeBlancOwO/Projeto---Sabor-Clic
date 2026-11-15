from flask import Blueprint, render_template, request, redirect
from app.models.carrinho import Carrinho

carrinho_bp = Blueprint("carrinho", __name__, url_prefix="/carrinho")

@carrinho_bp.route('/')
def renderizar_carrinho():
    pedidos = Carrinho.Listar(1)
    total = 0
    for item in pedidos:

        valor_unitario = item[3]

        if isinstance (valor_unitario, str):
            valor_unitario = float(valor_unitario.replace(",", "."))
        else:
            valor_unitario = float(valor_unitario)

        quantidade = int(item[4])
        total += valor_unitario * quantidade
    return render_template ("carrinho.html", pedidos = pedidos, total = total)

@carrinho_bp.route("/adicionar", methods = ["POST"])
def adicionar_carrinho():
    id_prato = request.form["id_prato"]
    quantidade = int(request.form["quantidade"])

    carrinho = Carrinho(
        1, 
        id_prato,
        quantidade
    )

    carrinho.Salvar()

    return redirect("/carrinho")

@carrinho_bp.route("/excluir/<int:id>")
def excluir_item(id):

    Carrinho.Excluir(id)

    return redirect("/carrinho")
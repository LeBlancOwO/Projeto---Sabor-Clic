from flask import Blueprint, render_template

carrinho_bp = Blueprint("carrinho", __name__, url_prefix="/carrinho")

@carrinho_bp.route('/')
def renderizar_carrinho():
    return render_template ("carrinho.html")

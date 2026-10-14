from flask import Blueprint, render_template

cardapio_bp = Blueprint("cardapio", __name__, url_prefix="/cardapio")

@cardapio_bp.route('/')
def renderizar_cardapio():
    return render_template ("cardapio.html")

@cardapio_bp.route('/adicionar_prato')
def renderizar_adicionar_prato():
    return render_template ("adicionar_prato.html")
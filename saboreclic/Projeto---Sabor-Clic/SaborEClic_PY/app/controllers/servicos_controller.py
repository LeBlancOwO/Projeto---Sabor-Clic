from flask import Blueprint, render_template

servicos_bp = Blueprint("servicos", __name__, url_prefix="/servicos")

@servicos_bp.route('/')
def renderizar_servicos():
    return render_template ("servicos.html")
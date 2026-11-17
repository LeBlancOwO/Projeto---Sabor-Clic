from flask import Flask
from app.models.cadastro import Cadastro
from app.models.cardapio import Cardapio

def create_app():
    app = Flask(__name__, template_folder="views", static_folder="static") 

    from app.controllers.cadastro_controller import cadastro_bp
    app.register_blueprint(cadastro_bp)

    from app.controllers.login_controller import login_bp
    app.register_blueprint(login_bp)

    Cadastro.Criar_tabela()
    Cardapio.Criar_tabela()

    return app
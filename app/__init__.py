from flask import Flask
from app.models.cadastro import Cadastro
from app.models.cardapio import Cardapio
from app.models.pedido import Pedido
from app.models.estoque import Estoque
from app.models.buffet import Buffet
from app.models.log import Log
from app.controllers.pedido_controller import pedido_bp

def create_app():
    app = Flask(__name__, template_folder="views", static_folder="static")
    app.secret_key = "chave-secreta-sabor-e-clic-escolar"

    # Registro dos Blueprints
    from app.controllers.views_controller import views_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.cardapio_controller import cardapio_bp
    from app.controllers.carrinho_controller import carrinho_bp
    from app.controllers.cozinha_controller import cozinha_bp
    from app.controllers.buffet_controller import buffet_bp
    from app.controllers.admin_controller import admin_bp

    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cardapio_bp)
    app.register_blueprint(carrinho_bp)
    app.register_blueprint(cozinha_bp)
    app.register_blueprint(buffet_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(pedido_bp)

    # Inicialização automática do Banco de Dados SQLite
    Cadastro.criar_tabela()
    Cardapio.criar_tabela()
    Pedido.criar_tabela()
    Estoque.criar_tabela()
    Buffet.criar_tabela()
    Log.criar_tabela()
    Cadastro.criar_admin_padrao()

    return app
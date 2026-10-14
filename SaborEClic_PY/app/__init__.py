from flask import Flask

def create_app():
    app = Flask(__name__, template_folder="views", static_folder="static") 

    from app.controllers.cardapio_controller import cardapio_bp
    app.register_blueprint(cardapio_bp)

    from app.controllers.login_controller import login_bp
    app.register_blueprint(login_bp)

    from app.controllers.carrinho_controller import carrinho_bp
    app.register_blueprint(carrinho_bp)

    from app.controllers.homepage_controller import homepage_bp
    app.register_blueprint(homepage_bp)

    from app.controllers.usuario_controller import usuario_bp
    app.register_blueprint(usuario_bp)

    return app
import os
import secrets
from flask import Flask
from app.models.cadastro import Cadastro
from app.models.cardapio import Cardapio
from app.models.pedido import Pedido
from app.models.estoque import Estoque
from app.models.buffet import Buffet
from app.models.log import Log
from app.models.conexao import Conexao
from app.controllers.erro_controller import erro_bp


def criar_triggers_banco():
    with Conexao() as cursor:
        # 1. Auditoria automática ao mudar status do pedido
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS trg_log_status_pedido
            AFTER UPDATE OF status ON Pedidos
            WHEN OLD.status != NEW.status
            BEGIN
                INSERT INTO Logs (data_hora, usuario_nome, nivel_acesso, acao)
                VALUES (
                    datetime('now', 'localtime'),
                    'TRIGGER_DB',
                    'sistema',
                    'Pedido #' || NEW.id || ' alterado de [' || OLD.status || '] para [' || NEW.status || ']'
                );
            END;
        """)

        # 2. Estoque: desativa ao zerar; só reativa se estava zerado e foi reposto
        cursor.execute("DROP TRIGGER IF EXISTS trg_cardapio_esgotado")
        cursor.execute("""
            CREATE TRIGGER trg_cardapio_esgotado
            AFTER UPDATE OF quantidade ON Cardapio
            BEGIN
                UPDATE Cardapio
                SET ativo = CASE
                    WHEN NEW.quantidade <= 0 THEN 0
                    WHEN OLD.quantidade <= 0 THEN 1
                    ELSE NEW.ativo
                END
                WHERE id = NEW.id;
            END;
        """)

        # 3. Proteção do Admin Master contra rebaixamento
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS trg_proteger_admin_master
            BEFORE UPDATE OF nivel_acesso ON Cadastro
            WHEN OLD.usuario = 'admin' AND NEW.nivel_acesso != 'administrador'
            BEGIN
                SELECT RAISE(ABORT, 'Operacao bloqueada: o administrador master nao pode ter o cargo alterado.');
            END;
        """)


def create_app():
    app = Flask(__name__, template_folder="views", static_folder="static")

    # Sem valor fixo no código: use a variável SECRET_KEY. Sem ela, gera uma
    # chave aleatória (as sessões caem quando o servidor reinicia).
    app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

    app.config.update(
        SESSION_COOKIE_NAME="sabor_clic_session",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE") == "1",  # use 1 em produção com HTTPS
        PERMANENT_SESSION_LIFETIME=3600 * 4,
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,  # uploads de até 5 MB
    )

    @app.after_request
    def cabecalhos_seguranca(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        return resp

    from app.controllers.views_controller import views_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.cardapio_controller import cardapio_bp
    from app.controllers.cozinha_controller import cozinha_bp
    from app.controllers.buffet_controller import buffet_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.pedido_controller import pedido_bp

    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cardapio_bp)
    app.register_blueprint(cozinha_bp)
    app.register_blueprint(buffet_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(erro_bp)

    Cadastro.criar_tabela()
    Cardapio.criar_tabela()
    Pedido.criar_tabela()
    Estoque.criar_tabela()
    Buffet.criar_tabela()
    Log.criar_tabela()
    criar_triggers_banco()
    Cadastro.criar_admin_padrao()

    return app
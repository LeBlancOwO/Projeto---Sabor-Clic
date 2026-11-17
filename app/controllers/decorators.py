from functools import wraps
from flask import session, redirect, url_for, jsonify, request

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"sucesso": False, "mensagem": "Não autenticado"}), 401
            return redirect(url_for("views.login"))
        return f(*args, **kwargs)
    return decorated

def nivel_requerido(*niveis):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            usuario = session.get("usuario")
            if not usuario:
                if request.path.startswith("/api/"):
                    return jsonify({"sucesso": False, "mensagem": "Não autenticado"}), 401
                return redirect(url_for("views.login"))
            if usuario["nivel_acesso"] not in niveis:
                if request.path.startswith("/api/"):
                    return jsonify({"sucesso": False, "mensagem": "Acesso negado"}), 403
                return redirect(url_for("views.cardapio"))
            return f(*args, **kwargs)
        return decorated
    return decorator
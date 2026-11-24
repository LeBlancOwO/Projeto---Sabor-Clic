from flask import Blueprint, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

erro_bp = Blueprint("erros", __name__)

# código: (ícone, título, mensagem)
ERROS = {
    400: ("🤔", "Requisição inválida", "Não foi possível entender o pedido enviado."),
    401: ("🔒", "Login necessário", "Faça login para continuar."),
    403: ("🚫", "Acesso negado", "Você não tem permissão para acessar esta página."),
    404: ("🔍", "Página não encontrada", "O endereço que você tentou acessar não existe ou foi removido."),
    405: ("⛔", "Ação não permitida", "Esse método não é permitido para este endereço."),
    413: ("📦", "Arquivo muito grande", "O arquivo enviado é maior que o limite de 5 MB."),
    429: ("⏳", "Muitas tentativas", "Aguarde alguns instantes e tente novamente."),
    500: ("🛠️", "Erro interno", "Algo deu errado do nosso lado. Tente novamente em instantes."),
}
ERRO_PADRAO = ("⚠️", "Algo deu errado", "Não foi possível concluir a ação. Tente novamente.")


@erro_bp.app_errorhandler(HTTPException)
def tratar_erro_http(e):
    """
    Trata todos os erros HTTP (404, 403, 405, 413...). Exceções não tratadas
    no código viram 500 e também passam por aqui.
    """
    codigo = e.code or 500
    icone, titulo, mensagem = ERROS.get(codigo, ERRO_PADRAO)

    # Arquivo estático inexistente: resposta curta, sem renderizar a página
    if request.path.startswith("/static/"):
        return "", codigo

    # API: devolve JSON no mesmo padrão do resto do sistema
    if request.path.startswith("/api/"):
        resposta = jsonify({"sucesso": False, "mensagem": mensagem})
        resposta.status_code = codigo
        return resposta

    # Páginas: template de erro (com fallback simples se até ele falhar)
    try:
        return render_template(
            "erro.html", codigo=codigo, icone=icone, titulo=titulo, mensagem=mensagem
        ), codigo
    except Exception:
        return (
            f"<h1>{codigo} - {titulo}</h1><p>{mensagem}</p>"
            "<p><a href='/'>Voltar ao início</a></p>"
        ), codigo
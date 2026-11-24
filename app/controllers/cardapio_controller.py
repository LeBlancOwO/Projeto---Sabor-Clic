import os
import uuid
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
from app.models.cardapio import Cardapio
from app.models.log import Log

cardapio_bp = Blueprint("cardapio_api", __name__, url_prefix="/api/cardapio")

EXTENSOES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".webp"}
CATEGORIAS = {"Doces", "Bolos", "Sobremesas", "Salgadinhos", "Cozinha"}


def pasta_uploads():
    return os.path.join(current_app.root_path, "static", "imagens", "produtos")


def pode_gerenciar_produtos(usuario):
    return usuario and usuario.get("nivel_acesso") in ("cozinheiro", "administrador")


def erro(mensagem, codigo=400):
    return jsonify({"sucesso": False, "mensagem": mensagem}), codigo


@cardapio_bp.route("/listar", methods=["GET"])
def listar():
    usuario = session.get("usuario")
    apenas_ativos = not pode_gerenciar_produtos(usuario)
    return jsonify({"pratos": Cardapio.listar(apenas_ativos=apenas_ativos)})


@cardapio_bp.route("/adicionar", methods=["POST"])
def adicionar():
    usuario = session.get("usuario")
    if not pode_gerenciar_produtos(usuario):
        return erro("Acesso negado.", 403)

    # Aceita JSON ou FormData (multipart)
    if request.is_json:
        dados = request.get_json(silent=True) or {}
        arquivo = None
    else:
        dados = request.form
        arquivo = request.files.get("foto_arquivo")

    nome = str(dados.get("nome", "")).strip()[:120]
    ingredientes = str(dados.get("ingredientes", "")).strip()[:300]
    categoria = str(dados.get("categoria", "Doces")).strip()
    foto_url = str(dados.get("foto_url", "")).strip()[:500]

    if categoria not in CATEGORIAS:
        categoria = "Doces"

    if not nome or not ingredientes:
        return erro("Preencha o nome e os ingredientes do produto.")

    try:
        valor = float(str(dados.get("valor", 0)).replace(",", "."))
        quantidade = int(dados.get("quantidade", 0))
    except (ValueError, TypeError):
        return erro("Valor ou quantidade inválidos.")

    if valor <= 0 or quantidade < 0:
        return erro("O valor deve ser maior que zero e a quantidade não pode ser negativa.")

    if foto_url and not foto_url.startswith(("http://", "https://", "/static/")):
        return erro("O link da foto deve começar com http:// ou https://.")

    foto_final = foto_url

    if arquivo and arquivo.filename and arquivo.filename.strip():
        ext = os.path.splitext(secure_filename(arquivo.filename))[1].lower()
        if ext not in EXTENSOES_PERMITIDAS:
            return erro("Formato de imagem não permitido. Use JPG, PNG ou WEBP.")
        pasta = pasta_uploads()
        os.makedirs(pasta, exist_ok=True)
        nome_arquivo = f"{uuid.uuid4().hex}{ext}"
        arquivo.save(os.path.join(pasta, nome_arquivo))
        foto_final = f"/static/imagens/produtos/{nome_arquivo}"

    Cardapio.adicionar(nome, ingredientes, categoria, valor, foto_final, quantidade)
    Log.registrar(usuario["nome"], usuario["nivel_acesso"],
                  f"Cadastrou produto: {nome} (R$ {valor:.2f} | Qtd: {quantidade})")
    return jsonify({"sucesso": True, "mensagem": "Produto cadastrado com sucesso!"}), 201


@cardapio_bp.route("/quantidade/<int:prato_id>", methods=["PUT"])
def atualizar_quantidade(prato_id):
    usuario = session.get("usuario")
    if not pode_gerenciar_produtos(usuario):
        return erro("Acesso negado.", 403)

    dados = request.get_json(silent=True) or {}
    try:
        quantidade = int(dados.get("quantidade", 0))
    except (ValueError, TypeError):
        return erro("Quantidade inválida.")

    Cardapio.atualizar_quantidade(prato_id, quantidade)
    return jsonify({"sucesso": True, "mensagem": "Estoque atualizado!"})


@cardapio_bp.route("/status/<int:prato_id>", methods=["PUT"])
def status(prato_id):
    usuario = session.get("usuario")
    if not pode_gerenciar_produtos(usuario):
        return erro("Acesso negado.", 403)

    dados = request.get_json(silent=True) or {}
    Cardapio.alternar_ativo(prato_id, dados.get("ativo"))
    return jsonify({"sucesso": True})


@cardapio_bp.route("/remover/<int:prato_id>", methods=["DELETE"])
def remover(prato_id):
    usuario = session.get("usuario")
    if not pode_gerenciar_produtos(usuario):
        return erro("Acesso negado.", 403)

    Cardapio.remover(prato_id)
    Log.registrar(usuario["nome"], usuario["nivel_acesso"], f"Excluiu produto ID #{prato_id}")
    return jsonify({"sucesso": True, "mensagem": "Produto excluído!"})
import os
import uuid
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from app.models.cardapio import Cardapio
from app.models.log import Log

cardapio_bp = Blueprint("cardapio_api", __name__, url_prefix="/api/cardapio")

PASTA_UPLOADS = os.path.join("app", "static", "imagens", "produtos")

def pode_gerenciar_produtos(usuario):
    return usuario and usuario.get("nivel_acesso") in ("cozinheiro", "administrador")

@cardapio_bp.route("/listar", methods=["GET"])
def listar():
    usuario = session.get("usuario")
    apenas_ativos = not pode_gerenciar_produtos(usuario)
    return jsonify({"pratos": Cardapio.listar(apenas_ativos=apenas_ativos)})

@cardapio_bp.route("/adicionar", methods=["POST"])
def adicionar():
    usuario = session.get("usuario")
    if not pode_gerenciar_produtos(usuario):
        return jsonify({"sucesso": False, "mensagem": "Acesso negado."}), 403

    # Lê os dados tanto se vierem por JSON quanto por FormData (multipart)
    if request.is_json:
        dados = request.get_json() or {}
        nome = str(dados.get("nome", "")).strip()
        ingredientes = str(dados.get("ingredientes", "")).strip()
        categoria = str(dados.get("categoria", "Doces")).strip()
        valor = dados.get("valor", 0)
        quantidade = dados.get("quantidade", 0)
        foto_url = str(dados.get("foto_url", "")).strip()
        arquivo = None
    else:
        nome = request.form.get("nome", "").strip()
        ingredientes = request.form.get("ingredientes", "").strip()
        categoria = request.form.get("categoria", "Doces").strip()
        valor = request.form.get("valor", 0)
        quantidade = request.form.get("quantidade", 0)
        foto_url = request.form.get("foto_url", "").strip()
        arquivo = request.files.get("foto_arquivo")

    if not nome or not ingredientes:
        return jsonify({"sucesso": False, "mensagem": "Preencha o nome e os ingredientes do produto."}), 400

    try:
        valor_float = float(str(valor).replace(",", "."))
        quantidade_int = int(quantidade)
    except (ValueError, TypeError):
        return jsonify({"sucesso": False, "mensagem": "Valor ou quantidade inválidos."}), 400

    foto_final = foto_url

    # Só salva arquivo na pasta se um arquivo válido realmente foi enviado
    if arquivo and arquivo.filename and arquivo.filename.strip() != "":
        os.makedirs(PASTA_UPLOADS, exist_ok=True)
        ext = os.path.splitext(secure_filename(arquivo.filename))[1] or ".jpg"
        nome_arquivo = f"{uuid.uuid4().hex}{ext}"
        caminho_salvar = os.path.join(PASTA_UPLOADS, nome_arquivo)
        arquivo.save(caminho_salvar)
        foto_final = f"/static/imagens/produtos/{nome_arquivo}"

    Cardapio.adicionar(nome, ingredientes, categoria, valor_float, foto_final, quantidade_int)
    Log.registrar(usuario["nome"], usuario["nivel_acesso"], f"Cadastrou produto: {nome} (R$ {valor_float:.2f} | Qtd: {quantidade_int})")
    return jsonify({"sucesso": True, "mensagem": "Produto cadastrado com sucesso!"}), 201

@cardapio_bp.route("/quantidade/<int:prato_id>", methods=["PUT"])
def atualizar_quantidade(prato_id):
    usuario = session.get("usuario")
    if not pode_gerenciar_produtos(usuario):
        return jsonify({"sucesso": False}), 403
    dados = request.get_json()
    Cardapio.atualizar_quantidade(prato_id, dados.get("quantidade", 0))
    return jsonify({"sucesso": True, "mensagem": "Estoque atualizado!"})

@cardapio_bp.route("/status/<int:prato_id>", methods=["PUT"])
def status(prato_id):
    usuario = session.get("usuario")
    if not pode_gerenciar_produtos(usuario):
        return jsonify({"sucesso": False}), 403
    dados = request.get_json()
    Cardapio.alternar_ativo(prato_id, dados.get("ativo"))
    return jsonify({"sucesso": True})

@cardapio_bp.route("/remover/<int:prato_id>", methods=["DELETE"])
def remover(prato_id):
    usuario = session.get("usuario")
    if not pode_gerenciar_produtos(usuario):
        return jsonify({"sucesso": False}), 403
    Cardapio.remover(prato_id)
    Log.registrar(usuario["nome"], usuario["nivel_acesso"], f"Excluiu produto ID #{prato_id}")
    return jsonify({"sucesso": True, "mensagem": "Produto excluído!"})
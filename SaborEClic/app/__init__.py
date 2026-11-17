from flask import Flask
from app.models.cadastro import Cadastro
from app.models.cardapio import Cardapio

def create_app():
    app = Flask(__name__, template_folder="views", static_folder="static") 

    Cadastro.Criar_tabela()
    Cardapio.Criar_tabela()

    return app
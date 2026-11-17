from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Servidor iniciado! Admin padrão: admin@docecelebracao.com | CPF: 00000000000 | Senha: admin1234")
    app.run(debug=True)
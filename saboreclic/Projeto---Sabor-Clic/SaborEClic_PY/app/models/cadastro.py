from app.models.conexao import Conexao

class Cadastro:

    def __init__(self, nome, email, cpf, senha, nivel_acesso):
        self.nome = nome
        self.email = email
        self.cpf = cpf
        self.senha = senha
        self.nivel_acesso = nivel_acesso

    @staticmethod
    def Criar_tabela():

        with Conexao() as cursor:

            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS Cadastro(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                cpf VARCHAR(11) NOT NULL UNIQUE,
                senha VARCHAR(50) NOT NULL,
                nivel_acesso TEXT NOT NULL
                )
            """)

    def Salvar(self):

        with Conexao() as cursor:

            cursor.execute("""
                INSERT INTO Cadastro
                (nome, email, cpf, senha, nivel_acesso)
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.nome,
                self.email,
                self.cpf,
                self.senha,
                self.nivel_acesso
            ))

    @staticmethod
    def Autenticar(email, cpf, senha, nivel_acesso):

        with Conexao() as cursor:

            cursor.execute("""
                SELECT *
                FROM Cadastro
                WHERE email = ?
                AND cpf = ?
                AND senha = ?
                AND nivel_acesso = ?
            """,(email, cpf, senha, nivel_acesso))

            cadastro = cursor.fetchone()

        return cadastro
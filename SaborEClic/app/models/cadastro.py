from app.models.conexao import Conexao
import bcrypt

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
                email VARCHAR(100) NOT NULL UNIQUE CHECK(email LIKE '%@%'),
                cpf TEXT NOT NULL UNIQUE CHECK(length(cpf) = 11),
                senha TEXT NOT NULL,
                nivel_acesso TEXT NOT NULL CHECK(nivel_acesso IN ('administrador', 'cozinheiro', 'cliente'))
                )
            """)

    def Salvar(self):

        if len(self.cpf) != 11:
                        return {"sucesso": False, "mensagem": "O CPF deve possuir 11 dígitos"}
        
        if len(self.senha) < 8:
            return {"sucesso": False, "mensagem": "A senha deve possuir no mínimo 8 caracteres"}
        
        senha_hash = Cadastro.GerarHash(self.senha)

        with Conexao() as cursor:

            cursor.execute("""
                INSERT INTO Cadastro
                (nome, email, cpf, senha, nivel_acesso)
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.nome,
                self.email,
                self.cpf,
                senha_hash,
                self.nivel_acesso
            ))

            return {"sucesso": True, "mensagem": "Usuário cadastrado"}

    @staticmethod
    def Autenticar(email, cpf, senha):

        usuario = Cadastro.BuscarUsuario(email, cpf)

        if not usuario: 
             return None
        
        senha_correta = bcrypt.checkpw(
             senha.encode(),
             usuario[4].encode()
        )

        if senha_correta:
             return usuario

        return None

    @staticmethod
    def BuscarUsuario(email, cpf):

        with Conexao() as cursor:

            cursor.execute("""
                SELECT *
                FROM Cadastro
                WHERE email = ?
                AND cpf = ?
            """, (email, cpf))

            return cursor.fetchone

    @staticmethod
    def GerarHash(senha):

        return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
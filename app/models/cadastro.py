from app.models.conexao import Conexao
import bcrypt
import sqlite3

class Cadastro:
    def __init__(self, nome, usuario, email, cpf, senha, nivel_acesso="cliente"):
        self.nome = nome.strip()
        self.usuario = usuario.strip().lower()
        self.email = email.strip().lower()
        self.cpf = "".join(filter(str.isdigit, cpf))
        self.senha = senha
        self.nivel_acesso = nivel_acesso.lower()

    @staticmethod
    def criar_tabela():
        with Conexao() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Cadastro (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome VARCHAR(100) NOT NULL,
                    usuario VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) NOT NULL UNIQUE CHECK(email LIKE '%@%'),
                    cpf TEXT NOT NULL UNIQUE CHECK(length(cpf) = 11),
                    senha TEXT NOT NULL,
                    nivel_acesso TEXT NOT NULL CHECK(nivel_acesso IN ('administrador', 'cozinheiro', 'cliente'))
                )
            """)

    def salvar(self):
        if len(self.usuario) < 3:
            return {"sucesso": False, "mensagem": "O nome de usuário deve ter pelo menos 3 caracteres."}
        if len(self.cpf) != 11:
            return {"sucesso": False, "mensagem": "O CPF deve possuir 11 dígitos."}
        if len(self.senha) < 8:
            return {"sucesso": False, "mensagem": "A senha deve possuir no mínimo 8 caracteres."}
        if self.nivel_acesso not in ('administrador', 'cozinheiro', 'cliente'):
            return {"sucesso": False, "mensagem": "Nível de acesso inválido."}

        senha_hash = bcrypt.hashpw(self.senha.encode(), bcrypt.gensalt()).decode()

        try:
            with Conexao() as cursor:
                cursor.execute("""
                    INSERT INTO Cadastro (nome, usuario, email, cpf, senha, nivel_acesso)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (self.nome, self.usuario, self.email, self.cpf, senha_hash, self.nivel_acesso))
            return {"sucesso": True, "mensagem": "Cadastro realizado com sucesso!"}
        except sqlite3.IntegrityError as e:
            erro = str(e).lower()
            if "cadastro.usuario" in erro:
                return {"sucesso": False, "mensagem": "Este nome de usuário já está em uso."}
            if "cadastro.email" in erro:
                return {"sucesso": False, "mensagem": "Este e-mail já está cadastrado."}
            if "cadastro.cpf" in erro:
                return {"sucesso": False, "mensagem": "Este CPF já está cadastrado."}
            return {"sucesso": False, "mensagem": "Dados já cadastrados no sistema."}

    @staticmethod
    def autenticar(identificador, senha):
        identificador = identificador.strip().lower()
        with Conexao() as cursor:
            cursor.execute("""
                SELECT * FROM Cadastro 
                WHERE email = ? OR usuario = ?
            """, (identificador, identificador))
            user = cursor.fetchone()

        if user and bcrypt.checkpw(senha.encode(), user["senha"].encode()):
            return dict(user)
        return None

    @staticmethod
    def listar_todos():
        with Conexao() as cursor:
            cursor.execute("SELECT id, nome, usuario, email, cpf, nivel_acesso FROM Cadastro")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def criar_admin_padrao():
        with Conexao() as cursor:
            cursor.execute("SELECT id FROM Cadastro WHERE nivel_acesso = 'administrador'")
            if not cursor.fetchone():
                admin = Cadastro("Admin Master", "admin", "admin@docecelebracao.com", "00000000000", "admin1234", "administrador")
                admin.salvar()
                
    @staticmethod
    def listar_todos():
        with Conexao() as cursor:
            cursor.execute("SELECT id, nome, usuario, email, cpf, nivel_acesso FROM Cadastro ORDER BY nome ASC")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def alterar_nivel(usuario_id, novo_nivel):
        if novo_nivel not in ("cliente", "cozinheiro", "administrador"):
            return False
        with Conexao() as cursor:
            cursor.execute("UPDATE Cadastro SET nivel_acesso = ? WHERE id = ?", (novo_nivel, usuario_id))
        return True
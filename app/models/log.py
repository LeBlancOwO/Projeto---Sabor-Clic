from datetime import datetime
from app.models.conexao import Conexao

class Log:
    @staticmethod
    def criar_tabela():
        with Conexao() as cursor:
            cursor.execute("PRAGMA table_info(Logs)")
            colunas = [row["name"] for row in cursor.fetchall()]
            if colunas and "usuario_nome" not in colunas:
                cursor.execute("DROP TABLE Logs")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_hora TEXT NOT NULL,
                    usuario_nome TEXT NOT NULL,
                    nivel_acesso TEXT NOT NULL,
                    acao TEXT NOT NULL
                )
            """)

    @staticmethod
    def registrar(usuario_nome, nivel_acesso, acao):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with Conexao() as cursor:
                cursor.execute("""
                    INSERT INTO Logs (data_hora, usuario_nome, nivel_acesso, acao)
                    VALUES (?, ?, ?, ?)
                """, (agora, str(usuario_nome), str(nivel_acesso), str(acao)))
        except Exception as e:
            print(f"Erro ao gravar log: {e}")

    @staticmethod
    def listar_recentes(limite=50):
        with Conexao() as cursor:
            cursor.execute("""
                SELECT id, data_hora, usuario_nome, nivel_acesso, acao
                FROM Logs
                ORDER BY id DESC
                LIMIT ?
            """, (limite,))
            return [dict(row) for row in cursor.fetchall()]
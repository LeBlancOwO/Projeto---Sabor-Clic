from app.models.conexao import Conexao

class Cardapio:
    @staticmethod
    def criar_tabela():
        with Conexao() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Cardapio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    ingredientes TEXT NOT NULL,
                    categoria TEXT NOT NULL DEFAULT 'Doces',
                    valor REAL NOT NULL,
                    foto TEXT NOT NULL DEFAULT '/static/imagens/doces.jpg',
                    quantidade INTEGER NOT NULL DEFAULT 10,
                    ativo INTEGER NOT NULL DEFAULT 1
                )
            """)

    @staticmethod
    def adicionar(nome, ingredientes, categoria, valor, foto, quantidade):
        foto_final = foto.strip() if foto and foto.strip() else "/static/imagens/doces.jpg"
        with Conexao() as cursor:
            cursor.execute("""
                INSERT INTO Cardapio (nome, ingredientes, categoria, valor, foto, quantidade, ativo)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (nome, ingredientes, categoria, float(valor), foto_final, int(quantidade)))

    @staticmethod
    def listar(apenas_ativos=False):
        with Conexao() as cursor:
            if apenas_ativos:
                cursor.execute("SELECT * FROM Cardapio WHERE ativo = 1 ORDER BY id DESC")
            else:
                cursor.execute("SELECT * FROM Cardapio ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def atualizar_quantidade(prato_id, nova_qtd):
        with Conexao() as cursor:
            cursor.execute("UPDATE Cardapio SET quantidade = ? WHERE id = ?", (max(0, int(nova_qtd)), prato_id))

    @staticmethod
    def alternar_ativo(prato_id, ativo):
        with Conexao() as cursor:
            cursor.execute("UPDATE Cardapio SET ativo = ? WHERE id = ?", (1 if ativo else 0, prato_id))

    @staticmethod
    def remover(prato_id):
        with Conexao() as cursor:
            cursor.execute("DELETE FROM Cardapio WHERE id = ?", (prato_id,))
from app.models.conexao import Conexao

class Estoque:
    @staticmethod
    def criar_tabela():
        with Conexao() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS EstoqueInsumos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insumo TEXT NOT NULL,
                    quantidade REAL NOT NULL,
                    unidade TEXT NOT NULL
                )
            """)

    @staticmethod
    def salvar(insumo, quantidade, unidade):
        with Conexao() as cursor:
            cursor.execute("SELECT id, quantidade FROM EstoqueInsumos WHERE LOWER(insumo) = LOWER(?)", (insumo.strip(),))
            existente = cursor.fetchone()
            if existente:
                nova_qtd = float(existente["quantidade"]) + float(quantidade)
                cursor.execute("UPDATE EstoqueInsumos SET quantidade = ?, unidade = ? WHERE id = ?",
                               (nova_qtd, unidade.strip(), existente["id"]))
            else:
                cursor.execute("INSERT INTO EstoqueInsumos (insumo, quantidade, unidade) VALUES (?, ?, ?)",
                               (insumo.strip(), float(quantidade), unidade.strip()))

    @staticmethod
    def atualizar_quantidade(item_id, nova_qtd):
        with Conexao() as cursor:
            cursor.execute("UPDATE EstoqueInsumos SET quantidade = ? WHERE id = ?",
                           (max(0.0, float(nova_qtd)), item_id))

    @staticmethod
    def listar():
        with Conexao() as cursor:
            cursor.execute("SELECT * FROM EstoqueInsumos ORDER BY insumo ASC")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def remover(item_id):
        with Conexao() as cursor:
            cursor.execute("DELETE FROM EstoqueInsumos WHERE id = ?", (item_id,))
from datetime import datetime
from app.models.conexao import Conexao

class Pedido:
    @staticmethod
    def criar_tabela():
        with Conexao() as cursor:
            cursor.execute("PRAGMA table_info(Pedidos)")
            colunas = [row["name"] for row in cursor.fetchall()]
            if colunas and "valor_total" not in colunas:
                cursor.execute("DROP TABLE Pedidos")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Pedidos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    itens TEXT NOT NULL,
                    valor_total REAL NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Aguardando',
                    data_hora TEXT NOT NULL
                )
            """)

    @staticmethod
    def criar(usuario_id, itens, valor_total, produtos=None):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with Conexao() as cursor:
            cursor.execute("""
                INSERT INTO Pedidos (usuario_id, itens, valor_total, status, data_hora)
                VALUES (?, ?, ?, 'Aguardando', ?)
            """, (usuario_id, itens, float(valor_total), agora))

            # Desconta automaticamente a quantidade comprada do estoque do cardápio
            if produtos:
                for p in produtos:
                    cursor.execute("""
                        UPDATE Cardapio
                        SET quantidade = MAX(0, quantidade - ?)
                        WHERE id = ?
                    """, (int(p.get("quantidade", 1)), int(p["id"])))

    @staticmethod
    def listar_por_usuario(usuario_id):
        with Conexao() as cursor:
            cursor.execute("""
                SELECT id, itens, valor_total, status, data_hora
                FROM Pedidos
                WHERE usuario_id = ?
                ORDER BY id DESC
            """, (usuario_id,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def listar_todos():
        with Conexao() as cursor:
            cursor.execute("""
                SELECT p.id, p.itens, p.valor_total, p.status, p.data_hora, c.nome AS cliente_nome
                FROM Pedidos p
                JOIN Cadastro c ON p.usuario_id = c.id
                ORDER BY p.id DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def atualizar_status(pedido_id, novo_status):
        with Conexao() as cursor:
            cursor.execute("UPDATE Pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
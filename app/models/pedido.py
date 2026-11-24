from datetime import datetime
from app.models.conexao import Conexao

STATUS_PERMITIDOS = ("Aguardando", "Em Preparo", "Saiu para Entrega", "Pronto")
TAXA_ENTREGA = 8.00

# Colunas que podem faltar em bancos antigos (adicionadas sem apagar nada)
COLUNAS_EXTRAS = {
    "itens": "TEXT NOT NULL DEFAULT ''",
    "valor_total": "REAL NOT NULL DEFAULT 0",
    "tipo_entrega": "TEXT NOT NULL DEFAULT 'Retirada'",
    "endereco_entrega": "TEXT DEFAULT 'Retirada na Dark Kitchen'",
    "status": "TEXT NOT NULL DEFAULT 'Aguardando'",
    "data_hora": "TEXT NOT NULL DEFAULT ''",
}


class ErroPedido(Exception):
    """Erro de regra de negócio ao criar um pedido (mensagem vai para o cliente)."""


class Pedido:
    @staticmethod
    def criar_tabela():
        with Conexao() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Pedidos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    itens TEXT NOT NULL,
                    valor_total REAL NOT NULL,
                    tipo_entrega TEXT NOT NULL DEFAULT 'Retirada',
                    endereco_entrega TEXT DEFAULT 'Retirada na Dark Kitchen',
                    status TEXT NOT NULL DEFAULT 'Aguardando',
                    data_hora TEXT NOT NULL
                )
            """)

            cursor.execute("PRAGMA table_info(Pedidos)")
            colunas = {row["name"] for row in cursor.fetchall()}
            for nome, definicao in COLUNAS_EXTRAS.items():
                if nome not in colunas:
                    cursor.execute(f"ALTER TABLE Pedidos ADD COLUMN {nome} {definicao}")

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pedidos_usuario ON Pedidos(usuario_id)")

    @staticmethod
    def criar(usuario_id, produtos, tipo_entrega="Retirada", endereco_entrega=""):
        """
        Recebe apenas [{id, quantidade}]. Nome, preço e total vêm do banco.
        Retorna (pedido_id, total, resumo_itens).
        """
        quantidades = {}
        for p in produtos:
            try:
                pid = int(p["id"])
                qtd = int(p["quantidade"])
            except (KeyError, ValueError, TypeError):
                raise ErroPedido("Item inválido no carrinho.")
            if qtd < 1 or qtd > 99:
                raise ErroPedido("Quantidade inválida no carrinho.")
            quantidades[pid] = quantidades.get(pid, 0) + qtd

        if not quantidades:
            raise ErroPedido("Seu carrinho está vazio.")

        tipo = "Entrega" if tipo_entrega == "Entrega" else "Retirada"
        endereco = str(endereco_entrega or "").strip()[:200]
        if tipo == "Entrega" and len(endereco) < 6:
            raise ErroPedido("Informe o endereço completo para entrega.")
        if tipo == "Retirada":
            endereco = "Retirada na Dark Kitchen"

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Se qualquer ErroPedido for lançado aqui dentro, o Conexao faz rollback
        # e o estoque descontado até o momento volta ao normal.
        with Conexao() as cursor:
            subtotal = 0.0
            resumo = []

            for pid, qtd in quantidades.items():
                cursor.execute("SELECT nome, valor FROM Cardapio WHERE id = ? AND ativo = 1", (pid,))
                produto = cursor.fetchone()
                if not produto:
                    raise ErroPedido("Um dos produtos não está mais disponível.")

                cursor.execute("""
                    UPDATE Cardapio
                    SET quantidade = quantidade - ?
                    WHERE id = ? AND quantidade >= ?
                """, (qtd, pid, qtd))
                if cursor.rowcount == 0:
                    raise ErroPedido(f"Estoque insuficiente para {produto['nome']}.")

                subtotal += float(produto["valor"]) * qtd
                resumo.append(f"{qtd}x {produto['nome']}")

            total = round(subtotal + (TAXA_ENTREGA if tipo == "Entrega" else 0), 2)
            itens_texto = ", ".join(resumo)

            cursor.execute("""
                INSERT INTO Pedidos (usuario_id, itens, valor_total, tipo_entrega, endereco_entrega, status, data_hora)
                VALUES (?, ?, ?, ?, ?, 'Aguardando', ?)
            """, (int(usuario_id), itens_texto, total, tipo, endereco, agora))

            return cursor.lastrowid, total, itens_texto

    @staticmethod
    def listar_por_usuario(usuario_id):
        with Conexao() as cursor:
            cursor.execute("""
                SELECT id, itens, valor_total, tipo_entrega, endereco_entrega, status, data_hora
                FROM Pedidos
                WHERE usuario_id = ?
                ORDER BY id DESC
            """, (int(usuario_id),))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def listar_todos(limite=200):
        with Conexao() as cursor:
            cursor.execute("""
                SELECT p.id, p.itens, p.valor_total, p.tipo_entrega, p.endereco_entrega,
                       p.status, p.data_hora, c.nome AS cliente_nome
                FROM Pedidos p
                JOIN Cadastro c ON p.usuario_id = c.id
                ORDER BY p.id DESC
                LIMIT ?
            """, (int(limite),))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def atualizar_status(pedido_id, novo_status):
        if novo_status not in STATUS_PERMITIDOS:
            return False
        with Conexao() as cursor:
            cursor.execute("UPDATE Pedidos SET status = ? WHERE id = ?", (novo_status, int(pedido_id)))
        return True
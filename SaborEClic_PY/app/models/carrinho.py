from app.models.conexao import Conexao

class Carrinho:

    def __init__(self, id_usuario, id_prato, quantidade):
        self.id_usuario = id_usuario
        self.id_prato = id_prato
        self.quantidade = quantidade

    @staticmethod
    def Criar_tabela():

        with Conexao() as cursor:

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Carrinho(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                id_prato INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,

                FOREIGN KEY(id_usuario)
                REFERENCES Cadastro(id),

                FOREIGN KEY(id_prato)
                REFERENCES Cardapio(id)
            )
        """)

    def Salvar(self):

        with Conexao() as cursor:

            cursor.execute("""
                INSERT INTO Carrinho
                (id_usuario, id_prato, quantidade)
                VALUES (?, ?, ?)
            """, (
                self.id_usuario,
                self.id_prato,
                self.quantidade
            )) 

    @staticmethod
    def Listar(id_usuario):

        with Conexao() as cursor:

            cursor.execute("""
                SELECT
                    c.id,
                    p.nome_prato,
                    p.ingredientes,
                    p.valor_unitario,
                    c.quantidade

                FROM Carrinho c

                INNER JOIN Cardapio p
                ON c.id_prato = p.id

                WHERE c.id_usuario = ?
            """, (id_usuario,))

            dados = cursor.fetchall()

        return dados

    @staticmethod
    def Excluir(id):

        with Conexao() as cursor:

            cursor.execute("""
                DELETE FROM Carrinho
                WHERE id = ?
            """, (id,))
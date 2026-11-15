from app.models.conexao import Conexao

class Cardapio:

    def __init__(self, nome_prato, ingredientes, valor_unitario):
        self.nome_prato = nome_prato
        self.ingredientes = ingredientes
        self.valor_unitario = valor_unitario

    @staticmethod
    def Criar_tabela():

        with Conexao() as cursor:

            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS Cardapio(
                id_pratos INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_prato VARCHAR(50) NOT NULL,
                ingredientes VARCHAR(200) NOT NULL,
                valor_unitario DECIMAL(10,2) NOT NULL
                )
            """)

    def Salvar(self):

        with Conexao() as cursor:

            cursor.execute("""
                INSERT INTO Cardapio
                (nome_prato, ingredientes, valor_unitario)
                VALUES (?, ?, ?)
            """, (
                self.nome_prato,
                self.ingredientes,
                self.valor_unitario
            ))

    @staticmethod
    def Listar():

        with Conexao() as cursor:

            cursor.execute("""
                SELECT *
                FROM Cardapio
            """)

            dados = cursor.fetchall()

        return dados
import os
import sqlite3


class Conexao:
    # Caminho absoluto: não depende de onde você roda o "python"
    BANCO = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "banco.db",
    )

    @classmethod
    def conectar(cls):
        conn = sqlite3.connect(cls.BANCO, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def __enter__(self):
        self.conn = self.conectar()
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()
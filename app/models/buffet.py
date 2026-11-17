from app.models.conexao import Conexao
import sqlite3

class Buffet:
    @staticmethod
    def criar_tabela():
        with Conexao() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ReservasBuffet (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    data_evento TEXT NOT NULL UNIQUE,
                    tipo_evento TEXT NOT NULL,
                    qtd_convidados INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Confirmado'
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS DatasBloqueadas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_bloqueada TEXT NOT NULL UNIQUE,
                    motivo TEXT DEFAULT 'Indisponível'
                )
            """)

    @staticmethod
    def reservar(usuario_id, data_evento, tipo_evento, qtd_convidados):
        data_limpa = str(data_evento).strip()[:10]
        with Conexao() as cursor:
            cursor.execute("SELECT 1 FROM DatasBloqueadas WHERE data_bloqueada = ?", (data_limpa,))
            if cursor.fetchone():
                return {"sucesso": False, "mensagem": "Esta data está bloqueada na agenda do buffet."}
        try:
            with Conexao() as cursor:
                cursor.execute("""
                    INSERT INTO ReservasBuffet (usuario_id, data_evento, tipo_evento, qtd_convidados)
                    VALUES (?, ?, ?, ?)
                """, (usuario_id, data_limpa, tipo_evento, int(qtd_convidados)))
            return {"sucesso": True, "mensagem": f"Buffet reservado para {data_limpa}!"}
        except sqlite3.IntegrityError:
            return {"sucesso": False, "mensagem": "Esta data já está reservada por outro cliente."}

    @staticmethod
    def listar_datas_ocupadas(mes_ano=None):
        with Conexao() as cursor:
            if mes_ano:
                filtro = f"{mes_ano.strip()}%"
                cursor.execute("SELECT data_evento FROM ReservasBuffet WHERE data_evento LIKE ?", (filtro,))
                reservadas = [str(r["data_evento"]).strip()[:10] for r in cursor.fetchall()]

                cursor.execute("SELECT data_bloqueada FROM DatasBloqueadas WHERE data_bloqueada LIKE ?", (filtro,))
                bloqueadas = [str(r["data_bloqueada"]).strip()[:10] for r in cursor.fetchall()]
            else:
                cursor.execute("SELECT data_evento FROM ReservasBuffet")
                reservadas = [str(r["data_evento"]).strip()[:10] for r in cursor.fetchall()]

                cursor.execute("SELECT data_bloqueada FROM DatasBloqueadas")
                bloqueadas = [str(r["data_bloqueada"]).strip()[:10] for r in cursor.fetchall()]

            return list(set(reservadas + bloqueadas))

    @staticmethod
    def listar_todas():
        with Conexao() as cursor:
            cursor.execute("""
                SELECT r.id, r.data_evento, r.tipo_evento, r.qtd_convidados, r.status,
                       c.nome AS cliente_nome, c.usuario AS cliente_usuario,
                       c.email AS cliente_email, c.cpf AS cliente_cpf
                FROM ReservasBuffet r
                JOIN Cadastro c ON r.usuario_id = c.id
                ORDER BY r.data_evento ASC
            """)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def cancelar_reserva(reserva_id):
        with Conexao() as cursor:
            cursor.execute("""
                SELECT r.data_evento, r.tipo_evento, c.nome AS cliente_nome, c.email AS cliente_email
                FROM ReservasBuffet r
                JOIN Cadastro c ON r.usuario_id = c.id
                WHERE r.id = ?
            """, (reserva_id,))
            dados = cursor.fetchone()
            if not dados:
                return None
            cursor.execute("DELETE FROM ReservasBuffet WHERE id = ?", (reserva_id,))
            return dict(dados)

    @staticmethod
    def bloquear_data(data_str, motivo="Indisponível"):
        data_limpa = str(data_str).strip()[:10]
        try:
            with Conexao() as cursor:
                cursor.execute(
                    "INSERT INTO DatasBloqueadas (data_bloqueada, motivo) VALUES (?, ?)",
                    (data_limpa, motivo or "Indisponível")
                )
            return True
        except sqlite3.IntegrityError:
            return False

    @staticmethod
    def desbloquear_data(bloqueio_id):
        with Conexao() as cursor:
            cursor.execute("DELETE FROM DatasBloqueadas WHERE id = ?", (bloqueio_id,))

    @staticmethod
    def listar_bloqueios():
        with Conexao() as cursor:
            cursor.execute("SELECT * FROM DatasBloqueadas ORDER BY data_bloqueada ASC")
            return [dict(row) for row in cursor.fetchall()]
import re
import sqlite3
from datetime import date, datetime, timedelta
from app.models.conexao import Conexao

MAX_PESSOAS = 15
MAX_DIAS_ANTECEDENCIA = 730  # ~2 anos
PADRAO_MES = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


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
                    motivo TEXT DEFAULT 'Manutenção / Indisponível'
                )
            """)

    @staticmethod
    def normalizar_data(valor):
        """Converte 'YYYY-MM-DD' em date. Retorna None se for inválida."""
        try:
            return datetime.strptime(str(valor).strip()[:10], "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def reservar(usuario_id, data_evento, tipo_evento, qtd_convidados):
        data = Buffet.normalizar_data(data_evento)
        if not data:
            return {"sucesso": False, "mensagem": "Data inválida."}

        hoje = date.today()
        if data < hoje:
            return {"sucesso": False, "mensagem": "Não é possível reservar uma data que já passou."}
        if data > hoje + timedelta(days=MAX_DIAS_ANTECEDENCIA):
            return {"sucesso": False, "mensagem": "Escolha uma data dentro dos próximos 2 anos."}

        try:
            qtd = int(qtd_convidados)
        except (ValueError, TypeError):
            return {"sucesso": False, "mensagem": "Quantidade de pessoas inválida."}
        if not 1 <= qtd <= MAX_PESSOAS:
            return {"sucesso": False, "mensagem": f"A equipe deve ter entre 1 e {MAX_PESSOAS} pessoas."}

        tipo = str(tipo_evento).strip()[:80]
        if not tipo:
            return {"sucesso": False, "mensagem": "Informe a finalidade da reserva."}

        data_iso = data.isoformat()
        try:
            # Verificação e inserção na mesma transação
            with Conexao() as cursor:
                cursor.execute("SELECT 1 FROM DatasBloqueadas WHERE data_bloqueada = ?", (data_iso,))
                if cursor.fetchone():
                    return {"sucesso": False, "mensagem": "Esta data está bloqueada na agenda da cozinha."}
                cursor.execute("""
                    INSERT INTO ReservasBuffet (usuario_id, data_evento, tipo_evento, qtd_convidados)
                    VALUES (?, ?, ?, ?)
                """, (int(usuario_id), data_iso, tipo, qtd))
            return {"sucesso": True, "mensagem": f"Cozinha reservada com sucesso para {data.strftime('%d/%m/%Y')}!"}
        except sqlite3.IntegrityError:
            return {"sucesso": False, "mensagem": "Esta data já está reservada por outro chef/cliente."}

    @staticmethod
    def listar_datas_ocupadas(mes_ano=None):
        mes_ano = (mes_ano or "").strip()
        if mes_ano and not PADRAO_MES.match(mes_ano):
            return []

        filtro = f"{mes_ano}-%" if mes_ano else "%"
        with Conexao() as cursor:
            cursor.execute("""
                SELECT data_evento AS data FROM ReservasBuffet WHERE data_evento LIKE ?
                UNION
                SELECT data_bloqueada FROM DatasBloqueadas WHERE data_bloqueada LIKE ?
                ORDER BY 1
            """, (filtro, filtro))
            return [row["data"] for row in cursor.fetchall()]

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
            """, (int(reserva_id),))
            dados = cursor.fetchone()
            if not dados:
                return None
            cursor.execute("DELETE FROM ReservasBuffet WHERE id = ?", (int(reserva_id),))
            return dict(dados)

    @staticmethod
    def bloquear_data(data_str, motivo=None):
        """Retorna (sucesso, mensagem)."""
        data = Buffet.normalizar_data(data_str)
        if not data:
            return False, "Data inválida."

        data_iso = data.isoformat()
        motivo_limpo = str(motivo or "").strip()[:100] or "Manutenção / Indisponível"

        try:
            with Conexao() as cursor:
                cursor.execute("SELECT 1 FROM ReservasBuffet WHERE data_evento = ?", (data_iso,))
                if cursor.fetchone():
                    return False, "Já existe uma reserva nesta data. Cancele a reserva primeiro."
                cursor.execute(
                    "INSERT INTO DatasBloqueadas (data_bloqueada, motivo) VALUES (?, ?)",
                    (data_iso, motivo_limpo)
                )
            return True, "Data bloqueada na agenda da cozinha!"
        except sqlite3.IntegrityError:
            return False, "Essa data já está bloqueada."

    @staticmethod
    def desbloquear_data(bloqueio_id):
        with Conexao() as cursor:
            cursor.execute("DELETE FROM DatasBloqueadas WHERE id = ?", (int(bloqueio_id),))

    @staticmethod
    def listar_bloqueios():
        with Conexao() as cursor:
            cursor.execute("SELECT * FROM DatasBloqueadas ORDER BY data_bloqueada ASC")
            return [dict(row) for row in cursor.fetchall()]
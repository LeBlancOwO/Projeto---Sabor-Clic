import sqlite3
import bcrypt

nova = input("Nova senha do admin (mínimo 8 caracteres): ")
if len(nova) < 8 or len(nova.encode()) > 72:
    raise SystemExit("A senha deve ter entre 8 e 72 caracteres.")

hash_novo = bcrypt.hashpw(nova.encode(), bcrypt.gensalt()).decode()

con = sqlite3.connect("banco.db")
con.execute("UPDATE Cadastro SET senha = ? WHERE usuario = 'admin'", (hash_novo,))
con.commit()
con.close()
print("Senha do admin atualizada.")
import mysql.connector
import os
from mysql.connector import Error

FILE_DIR = './models/mysql_database.sql'

def build():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("MYSQLPASSWD")
        )

        if conn.is_connected():
            print("✅ Conectado com sucesso ao MySQL!")
            return conn, conn.cursor()

    except Error as e:
        print("❌ Erro ao conectar ao MySQL:", e)
        return None, None
    
if __name__ == '__main__':
    conn,cursor = build()

    with open(FILE_DIR,'r') as f:
        sql_file = f.read()

    for cmd in sql_file.split(';'):
        if cmd:
            try:
                cursor.execute(cmd + ';')
                print(f"✔ Executado: {cmd[:50]}...")
            except Exception as e:
                print(f"❌ Erro ao executar: {cmd}\n{e}")

    conn.commit()
    cursor.close()
    conn.close()


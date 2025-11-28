import mysql.connector
import os

def connect_to_mysql():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.environ['MYSQLPASSWD']
    )
    
    cursor = conn.cursor()
    cursor.execute('USE iot_monitoring')
    if cursor is not None:
        print("✅ Conectado com sucesso ao Mysql em: localhost")
    return cursor
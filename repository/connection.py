import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv 

load_dotenv()

class DatabaseManager:
    @staticmethod
    def get_connection():
        """Retorna uma nova conexão com o banco de dados."""
        try:
            conn = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT")),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                database=os.getenv("DB_NAME"),
                client_flags=[mysql.connector.ClientFlag.SSL],
                ssl_ca="ca.pem" 
            )
            return conn
        except Error as e:
            print(f"❌ Erro de conexão: {e}")
            return None

    @staticmethod
    def execute_query(query, params=None):
        """Método utilitário para executar comandos sem repetir código."""
        conn = DatabaseManager.get_connection()
        if not conn: return None
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.rowcount
            return result
        finally:
            cursor.close()
            conn.close()

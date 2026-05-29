import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="TIENDALOSBOYACOS"
        )
        if conn.is_connected():
            print("✅ Conexión exitosa a TIENDALOSBOYACOS")
            return conn
    except Error as e:
        print(f"❌ Error de conexión: {e}")
        return None

def close_connection(conn):
    if conn and conn.is_connected():
        conn.close()
        print("🔒 Conexión cerrada")

# sirve para verificar rápidamente que la conexión funciona cada vez que lo necesite.
if __name__ == "__main__":
    conn = get_connection()
    close_connection(conn)
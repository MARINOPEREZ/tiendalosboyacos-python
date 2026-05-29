import sys
sys.path.append("../../")
from config.db import get_connection, close_connection

class Categoria:

    @staticmethod
    def listar():
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM categoria ORDER BY Nom_Categoria")
            cats = cursor.fetchall()
            close_connection(conn)
            return cats

    @staticmethod
    def buscar(id_categoria):
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM categoria WHERE Id_Categoria = %s",
                (id_categoria,))
            cat = cursor.fetchone()
            close_connection(conn)
            return cat

    @staticmethod
    def categorias_de_producto(id_producto):
        """Devuelve lista de categorías asignadas a un producto"""
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT c.Id_Categoria, c.Nom_Categoria
                FROM   categoriaxproducto cp
                JOIN   categoria c ON cp.Id_Categoria = c.Id_Categoria
                WHERE  cp.Id_Producto = %s
            """, (id_producto,))
            cats = cursor.fetchall()
            close_connection(conn)
            return cats

    @staticmethod
    def asignar(id_producto, id_categoria):
        """Inserta en CATEGORIAXPRODUCTO si no existe"""
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT IGNORE INTO categoriaxproducto (Id_Categoria, Id_Producto)
                VALUES (%s, %s)
            """, (id_categoria, id_producto))
            conn.commit()
            close_connection(conn)

    @staticmethod
    def reemplazar(id_producto, ids_categorias):
        """Borra categorías anteriores y asigna las nuevas"""
        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM categoriaxproducto WHERE Id_Producto = %s",
                (id_producto,))
            for id_cat in ids_categorias:
                cursor.execute("""
                    INSERT INTO categoriaxproducto (Id_Categoria, Id_Producto)
                    VALUES (%s, %s)
                """, (id_cat, id_producto))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"❌ Error asignando categorías: {e}")
        finally:
            close_connection(conn)
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

    # ─── CREAR ──────────────────────────────────────────
    @staticmethod
    def crear(nom_categoria):
        conn = get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO categoria (Nom_Categoria) VALUES (%s)",
                (nom_categoria,))
            id_categoria = cursor.lastrowid
            conn.commit()
            print(f"✅ Categoría '{nom_categoria}' creada (ID:{id_categoria})")
            return id_categoria
        except Exception as e:
            conn.rollback()
            print(f"❌ Error creando categoría: {e}")
            raise e
        finally:
            close_connection(conn)

    # ─── EDITAR ─────────────────────────────────────────
    @staticmethod
    def editar(id_categoria, nom_categoria):
        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE categoria SET Nom_Categoria=%s WHERE Id_Categoria=%s",
                (nom_categoria, id_categoria))
            conn.commit()
            print(f"✅ Categoría {id_categoria} actualizada")
        except Exception as e:
            conn.rollback()
            print(f"❌ Error editando categoría: {e}")
            raise e
        finally:
            close_connection(conn)

    # ─── CONTAR PRODUCTOS ASOCIADOS (activos) ───────────
    @staticmethod
    def contar_productos(id_categoria):
        conn = get_connection()
        if not conn:
            return 0
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM categoriaxproducto cp
            JOIN producto p ON cp.Id_Producto = p.Id_Producto
            WHERE cp.Id_Categoria = %s AND p.Activo = 1
        """, (id_categoria,))
        total = cursor.fetchone()[0]
        close_connection(conn)
        return total

    # ─── ELIMINAR ────────────────────────────────────────
    @staticmethod
    def eliminar(id_categoria):
        """
        Elimina la categoría físicamente. La FK RESTRICT en
        CATEGORIAXPRODUCTO impide borrarla si todavía hay productos
        asociados (fk_categoriaxproducto_categoria).
        """
        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM categoria WHERE Id_Categoria = %s",
                (id_categoria,))
            conn.commit()
            print(f"✅ Categoría {id_categoria} eliminada")
        except Exception as e:
            conn.rollback()
            print(f"❌ Error eliminando categoría: {e}")
            raise e
        finally:
            close_connection(conn)

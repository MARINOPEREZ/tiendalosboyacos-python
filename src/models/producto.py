import sys
sys.path.append("../../")
from config.db import get_connection, close_connection

class Producto:

    # ─── AGREGAR ────────────────────────────────────────
    @staticmethod
    def agregar(nom, descripcion, vlr_unitario, cant_stock,
                fech_vencimiento, iva, imagen=None, ids_categorias=None):
        conn = get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()

            # 1. PRODUCTO
            cursor.execute("""
                INSERT INTO producto
                    (Nom_Producto, Descripcion, Vlr_Unitario,
                     Cant_Stock, Fech_Vencimiento, IVA, Img_Producto)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (nom, descripcion, vlr_unitario,
                  cant_stock, fech_vencimiento or None, iva, imagen))
            id_producto = cursor.lastrowid

            # 2. INVENTARIO
            cursor.execute("""
                INSERT INTO inventario
                    (Id_Producto, Cant_Inventario, Fech_Registro, Observacion)
                VALUES (%s, %s, NOW(), 'Stock inicial al crear producto')
            """, (id_producto, cant_stock))

            # 3. CATEGORIAXPRODUCTO
            if ids_categorias:
                for id_cat in ids_categorias:
                    cursor.execute("""
                        INSERT INTO categoriaxproducto (Id_Categoria, Id_Producto)
                        VALUES (%s, %s)
                    """, (id_cat, id_producto))

            conn.commit()
            print(f"✅ Producto '{nom}' (ID:{id_producto}) — inventario y categorías registrados")
            return id_producto

        except Exception as e:
            conn.rollback()
            print(f"❌ Error creando producto: {e}")
            raise e
        finally:
            close_connection(conn)

    # ─── LISTAR ─────────────────────────────────────────
    @staticmethod
    def listar():
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM producto WHERE Activo = 1")
            productos = cursor.fetchall()
            close_connection(conn)
            return productos

    # ─── BUSCAR ─────────────────────────────────────────
    @staticmethod
    def buscar(id_producto):
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM producto WHERE Id_Producto = %s",
                (id_producto,))
            producto = cursor.fetchone()
            close_connection(conn)
            return producto

    # ─── EDITAR ─────────────────────────────────────────
    @staticmethod
    def editar(id_producto, nom, descripcion, vlr_unitario,
               cant_stock, fech_vencimiento, iva,
               imagen=None, ids_categorias=None):
        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()

            # 1. PRODUCTO
            if imagen:
                cursor.execute("""
                    UPDATE producto SET
                        Nom_Producto=%s, Descripcion=%s, Vlr_Unitario=%s,
                        Cant_Stock=%s, Fech_Vencimiento=%s, IVA=%s,
                        Img_Producto=%s
                    WHERE Id_Producto=%s
                """, (nom, descripcion, vlr_unitario,
                      cant_stock, fech_vencimiento or None,
                      iva, imagen, id_producto))
            else:
                cursor.execute("""
                    UPDATE producto SET
                        Nom_Producto=%s, Descripcion=%s, Vlr_Unitario=%s,
                        Cant_Stock=%s, Fech_Vencimiento=%s, IVA=%s
                    WHERE Id_Producto=%s
                """, (nom, descripcion, vlr_unitario,
                      cant_stock, fech_vencimiento or None,
                      iva, id_producto))

            # 2. INVENTARIO — actualizar si ya existe, insertar si no
            cursor.execute("""
                INSERT INTO inventario
                    (Id_Producto, Cant_Inventario, Fech_Registro, Observacion)
                VALUES (%s, %s, NOW(), 'Actualización de stock por admin')
                ON DUPLICATE KEY UPDATE
                    Cant_Inventario = VALUES(Cant_Inventario),
                    Fech_Registro   = NOW(),
                    Observacion     = 'Actualización de stock por admin'
            """, (id_producto, cant_stock))

            # 3. CATEGORIAXPRODUCTO (reemplazar)
            if ids_categorias is not None:
                cursor.execute(
                    "DELETE FROM categoriaxproducto WHERE Id_Producto = %s",
                    (id_producto,))
                for id_cat in ids_categorias:
                    cursor.execute("""
                        INSERT INTO categoriaxproducto (Id_Categoria, Id_Producto)
                        VALUES (%s, %s)
                    """, (id_cat, id_producto))

            conn.commit()
            print(f"✅ Producto {id_producto} actualizado — inventario y categorías actualizados")

        except Exception as e:
            conn.rollback()
            print(f"❌ Error editando producto: {e}")
            raise e
        finally:
            close_connection(conn)

    # ─── ELIMINAR (borrado lógico) ──────────────────────
    @staticmethod
    def eliminar(id_producto):
        """
        Desactiva el producto en lugar de borrarlo físicamente.
        Esto preserva el historial de ventas en DETALLE.
        """
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE producto SET Activo = 0 WHERE Id_Producto = %s",
                (id_producto,))
            conn.commit()
            print(f"✅ Producto {id_producto} desactivado (borrado lógico)")
            close_connection(conn)

    # ─── ELIMINAR FÍSICO (solo si no tiene ventas) ──────
    @staticmethod
    def eliminar_fisico(id_producto):
        """Solo usar si el producto no tiene ventas asociadas."""
        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM categoriaxproducto WHERE Id_Producto = %s",
                (id_producto,))
            cursor.execute(
                "DELETE FROM inventario WHERE Id_Producto = %s",
                (id_producto,))
            cursor.execute(
                "DELETE FROM producto WHERE Id_Producto = %s",
                (id_producto,))
            conn.commit()
            print(f"✅ Producto {id_producto} eliminado físicamente")
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            close_connection(conn)
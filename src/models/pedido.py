import sys
sys.path.append("../../")
from config.db import get_connection, close_connection

class Pedido:

    # ─── CREAR PEDIDO CON DETALLE ────────────────────────
    @staticmethod
    def crear(num_doc, total, items, direccion="", observaciones=""):
        """
        items: lista de dicts con keys:
               id_producto, nombre, cantidad, precio_unitario
        """
        conn = get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            # 1. Insertar cabecera del pedido
            cursor.execute("""
                INSERT INTO PEDIDO
                    (NumDoc_Usuario, Total_Pedido, Direccion, Observaciones)
                VALUES (%s, %s, %s, %s)
            """, (num_doc, total, direccion, observaciones))
            id_pedido = cursor.lastrowid

            # 2. Insertar líneas de detalle_pedido + descontar stock
            for item in items:
                subtotal = item["cantidad"] * item["precio_unitario"]
                cursor.execute("""
                    INSERT INTO DETALLE_PEDIDO
                        (Id_Pedido, Id_Producto, Cantidad,
                         Precio_Unitario, Subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_pedido, item["id_producto"],
                      item["cantidad"], item["precio_unitario"], subtotal))
                # Descontar stock
                cursor.execute("""
                    UPDATE PRODUCTO
                    SET Cant_Stock = Cant_Stock - %s
                    WHERE Id_Producto = %s AND Cant_Stock >= %s
                """, (item["cantidad"], item["id_producto"], item["cantidad"]))
            # 2. Insertar líneas de detalle 
            for item in items:
                subtotal = item["cantidad"] * item["precio_unitario"]
                cursor.execute("""
                    INSERT INTO DETALLE
                        (Id_detalle, Cantidad, Vlr_SubTotal,
                         Vlr_total, id_Venta, id_producto)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_pedido, item["cantidad"], item["precio_unitario"], subtotal, 
                       item["id_producto"]))
            conn.commit()
            print(f"✅ Pedido #{id_pedido} creado — total: ${total:,.0f}")
            return id_pedido
        except Exception as e:
            conn.rollback()
            print(f"❌ Error creando pedido: {e}")
            return None
        finally:
            close_connection(conn)

    # ─── BUSCAR PEDIDO POR ID ────────────────────────────
    @staticmethod
    def buscar(id_pedido):
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.*, u.Nom1_Usuario, u.Ape1_Usuario, u.Mail_Usuario
                FROM PEDIDO p
                JOIN USUARIO u ON p.NumDoc_Usuario = u.NumDoc_Usuario
                WHERE p.Id_Pedido = %s
            """, (id_pedido,))
            pedido = cursor.fetchone()
            close_connection(conn)
            return pedido

    # ─── DETALLE DE UN PEDIDO ────────────────────────────
    @staticmethod
    def detalle(id_pedido):
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT d.*, pr.Nom_Producto, pr.Img_Producto
                FROM DETALLE_PEDIDO d
                JOIN PRODUCTO pr ON d.Id_Producto = pr.Id_Producto
                WHERE d.Id_Pedido = %s
            """, (id_pedido,))
            items = cursor.fetchall()
            close_connection(conn)
            return items

    # ─── LISTAR TODOS (admin) ────────────────────────────
    @staticmethod
    def listar(limite=100):
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.*, u.Nom1_Usuario, u.Ape1_Usuario, u.Mail_Usuario
                FROM PEDIDO p
                JOIN USUARIO u ON p.NumDoc_Usuario = u.NumDoc_Usuario
                ORDER BY p.Fecha_Pedido DESC
                LIMIT %s
            """, (limite,))
            pedidos = cursor.fetchall()
            close_connection(conn)
            return pedidos

    # ─── PEDIDOS DE UN CLIENTE ───────────────────────────
    @staticmethod
    def por_cliente(num_doc):
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM PEDIDO
                WHERE NumDoc_Usuario = %s
                ORDER BY Fecha_Pedido DESC
            """, (num_doc,))
            pedidos = cursor.fetchall()
            close_connection(conn)
            return pedidos

    # ─── ACTUALIZAR ESTADO ───────────────────────────────
    @staticmethod
    def actualizar_estado(id_pedido, nuevo_estado):
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE PEDIDO SET Estado_Pedido = %s
                WHERE Id_Pedido = %s
            """, (nuevo_estado, id_pedido))
            conn.commit()
            print(f"✅ Pedido #{id_pedido} → {nuevo_estado}")
            close_connection(conn)
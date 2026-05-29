import sys
sys.path.append("../../")
from config.db import get_connection, close_connection

class Venta:

    # ─── CREAR VENTA CON DETALLE ─────────────────────────
    @staticmethod
    def crear(num_doc, total, items, direccion="", observaciones="", metodo_pago="Efectivo", tipo_entrega="Envio", id_qr=None):
        conn = get_connection()
        if not conn:
            raise Exception("No se pudo conectar a la base de datos")
        try:
            cursor = conn.cursor()

            # 1. Insertar cabecera en VENTA
            # Estado según tipo de entrega
            estado = 'Entregado' if tipo_entrega == 'Punto de venta' else 'Pendiente'
            cursor.execute("""
                INSERT INTO venta (NumDoc_Usuario, Total_Venta,
                                   Estado_Venta, Direccion,
                                   Observaciones, Metodo_Pago,
                                   Tipo_Entrega, Id_QR)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (num_doc, total, estado,
                  direccion or None,
                  observaciones or None,
                  metodo_pago, tipo_entrega,
                  int(id_qr) if id_qr else None))
            id_venta = cursor.lastrowid

            # 2. Insertar líneas en DETALLE y descontar stock
            for item in items:
                vlr_sub = round(item["cantidad"] * item["precio_unitario"], 2)
                cursor.execute("""
                    INSERT INTO detalle
                        (Id_Venta, Id_Producto, Cantidad, Vlr_SubTotal, Vlr_Total)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_venta, item["id_producto"],
                      item["cantidad"], vlr_sub, vlr_sub))

                # Descontar stock con verificación
                cursor.execute("""
                    UPDATE producto
                    SET    Cant_Stock = Cant_Stock - %s
                    WHERE  Id_Producto = %s
                      AND  Cant_Stock  >= %s
                """, (item["cantidad"], item["id_producto"], item["cantidad"]))

                if cursor.rowcount == 0:
                    raise Exception(
                        f"Stock insuficiente para '{item['nombre']}'")

            conn.commit()
            print(f"✅ Venta #{id_venta} creada — total: ${total:,.0f}")
            return id_venta

        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"❌ Error en venta: {e}")
            raise Exception(str(e))  # re-lanzar con mensaje limpio
        finally:
            close_connection(conn)

    # ─── BUSCAR POR ID ───────────────────────────────────
    @staticmethod
    def buscar(id_venta):
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT v.*,
                       u.Nom1_Usuario, u.Ape1_Usuario, u.Mail_Usuario
                FROM   venta v
                JOIN   usuario u ON v.NumDoc_Usuario = u.NumDoc_Usuario
                WHERE  v.Id_Venta = %s
            """, (id_venta,))
            venta = cursor.fetchone()
            close_connection(conn)
            return venta

    # ─── DETALLE DE UNA VENTA ────────────────────────────
    @staticmethod
    def detalle(id_venta):
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT d.*,
                       p.Nom_Producto, p.Img_Producto, p.Vlr_Unitario
                FROM   detalle d
                JOIN   producto p ON d.Id_Producto = p.Id_Producto
                WHERE  d.Id_Venta = %s
            """, (id_venta,))
            items = cursor.fetchall()
            close_connection(conn)
            return items

    # ─── LISTAR TODAS (admin) ────────────────────────────
    @staticmethod
    def listar(limite=100):
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT v.*,
                       u.Nom1_Usuario, u.Ape1_Usuario, u.Mail_Usuario
                FROM   venta v
                JOIN   usuario u ON v.NumDoc_Usuario = u.NumDoc_Usuario
                ORDER  BY v.Fech_Venta DESC
                LIMIT  %s
            """, (limite,))
            ventas = cursor.fetchall()
            close_connection(conn)
            return ventas

    # ─── VENTAS DE UN CLIENTE ────────────────────────────
    @staticmethod
    def por_cliente(num_doc):
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM venta
                WHERE  NumDoc_Usuario = %s
                ORDER  BY Fech_Venta DESC
            """, (num_doc,))
            ventas = cursor.fetchall()
            close_connection(conn)
            return ventas

    # ─── ACTUALIZAR ESTADO ───────────────────────────────
    @staticmethod
    def actualizar_estado(id_venta, nuevo_estado):
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE venta SET Estado_Venta = %s
                WHERE Id_Venta = %s
            """, (nuevo_estado, id_venta))
            conn.commit()
            print(f"✅ Venta #{id_venta} → {nuevo_estado}")
            close_connection(conn)
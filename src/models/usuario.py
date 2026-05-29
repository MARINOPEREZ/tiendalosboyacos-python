import sys
sys.path.append("../../")
from config.db import get_connection, close_connection

class Usuario:

    # ─── REGISTRAR + CUENTA ──────────────────────────────
    @staticmethod
    def registrar(num_doc, tipo_doc, nom1, nom2,
                  ape1, ape2, indicativo, tel, mail,
                  password, foto=None, id_rol="2"):
        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()

            # 1. Insertar USUARIO
            cursor.execute("""
                INSERT INTO usuario
                    (NumDoc_Usuario, TipoDoc_Usuario,
                     Nom1_Usuario,   Nom2_Usuario,
                     Ape1_Usuario,   Ape2_Usuario,
                     Indicativo_Usuario, Tel_Usuario,
                     Mail_Usuario,   Password, Foto_Usuario)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (num_doc, tipo_doc, nom1, nom2,
                  ape1, ape2, indicativo, tel,
                  mail, password, foto))

            # 2. Crear CUENTA automáticamente
            nom_cuenta = f"{nom1} {ape1}".strip()
            cursor.execute("""
                INSERT INTO cuenta
                    (Nom_Cuenta, Est_Cuenta, NumDoc_Usuario)
                VALUES (%s, 'activa', %s)
            """, (nom_cuenta, num_doc))

            # 3. Asignar ROL en ROLXUSUARIO
            cursor.execute("""
                INSERT INTO rolxusuario (Cod_Rol, NumDoc_Usuario)
                VALUES (%s, %s)
            """, (int(id_rol), num_doc))

            conn.commit()
            print(f"✅ Usuario '{nom1} {ape1}' registrado — cuenta creada")

        except Exception as e:
            conn.rollback()
            print(f"❌ Error registrando usuario: {e}")
            raise e
        finally:
            close_connection(conn)

    # ─── BUSCAR POR DOCUMENTO ───────────────────────────
    @staticmethod
    def buscar(num_doc):
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM usuario WHERE NumDoc_Usuario = %s",
                (num_doc,))
            usuario = cursor.fetchone()
            close_connection(conn)
            return usuario

    # ─── LISTAR TODOS ───────────────────────────────────
    @staticmethod
    def listar():
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuario")
            usuarios = cursor.fetchall()
            close_connection(conn)
            return usuarios

    # ─── EDITAR ─────────────────────────────────────────
    @staticmethod
    def editar(num_doc, nom1, nom2, ape1, ape2,
               indicativo, tel, mail,
               nueva_password=None, foto=None):
        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()

            # Construir UPDATE dinámico según campos que cambian
            sets   = ["Nom1_Usuario=%s","Nom2_Usuario=%s",
                      "Ape1_Usuario=%s","Ape2_Usuario=%s",
                      "Indicativo_Usuario=%s","Tel_Usuario=%s",
                      "Mail_Usuario=%s"]
            valores = [nom1, nom2, ape1, ape2, indicativo, tel, mail]

            if nueva_password:
                sets.append("Password=%s")
                valores.append(nueva_password)
            if foto:
                sets.append("Foto_Usuario=%s")
                valores.append(foto)

            valores.append(num_doc)
            cursor.execute(
                f"UPDATE usuario SET {', '.join(sets)} WHERE NumDoc_Usuario=%s",
                valores)

            # Actualizar nombre en CUENTA si cambiaron nombre o apellido
            cursor.execute("""
                UPDATE cuenta
                SET    Nom_Cuenta = %s
                WHERE  NumDoc_Usuario = %s
            """, (f"{nom1} {ape1}".strip(), num_doc))

            conn.commit()
            print(f"✅ Usuario {num_doc} actualizado — filas: {cursor.rowcount}")

        except Exception as e:
            conn.rollback()
            print(f"❌ Error editando usuario: {e}")
            raise e
        finally:
            close_connection(conn)

    # ─── ELIMINAR ───────────────────────────────────────
    @staticmethod
    def eliminar(num_doc):
        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            # 1. Verificar que no tiene ventas — si tiene, no se puede eliminar
            cursor.execute(
                "SELECT COUNT(*) AS total FROM venta WHERE NumDoc_Usuario=%s",
                (num_doc,))
            row = cursor.fetchone()
            total_ventas = row[0] if isinstance(row, tuple) else row.get("total", 0)
            if total_ventas > 0:
                raise Exception(
                    f"El usuario tiene {total_ventas} venta(s) registrada(s) "
                    f"y no puede eliminarse para preservar el historial")
            # 2. Borrar en orden correcto respetando FKs
            cursor.execute(
                "DELETE FROM rolxusuario WHERE NumDoc_Usuario=%s", (num_doc,))
            cursor.execute(
                "DELETE FROM cuenta WHERE NumDoc_Usuario=%s", (num_doc,))
            cursor.execute(
                "DELETE FROM usuario WHERE NumDoc_Usuario=%s", (num_doc,))
            conn.commit()
            print(f"✅ Usuario {num_doc} eliminado correctamente")
        except Exception as e:
            conn.rollback()
            print(f"❌ Error eliminando usuario: {e}")
            raise e
        finally:
            close_connection(conn)
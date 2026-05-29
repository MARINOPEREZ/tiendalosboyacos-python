import sys
sys.path.append("../")
from config.db import get_connection, close_connection

def seed_roles():
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()

    print("\n--- PREPARANDO BASE DE DATOS ---")

    # ─── 1. Columna Password ─────────────────────────────
    try:
        cursor.execute("""
            ALTER TABLE USUARIO
            ADD COLUMN Password VARCHAR(255) NOT NULL
            DEFAULT '' AFTER Mail_Usuario
        """)
        conn.commit()
        print("✅ Columna Password agregada a USUARIO")
    except Exception as e:
        if "Duplicate column" in str(e):
            print("ℹ️  Columna Password ya existe")
        else:
            print(f"❌ Error: {e}")

    # ─── 2. Insertar roles ───────────────────────────────
    roles = [
        (1, "Admin"),
        (2, "Cliente"),
        (3, "Domiciliario"),
    ]
    for cod, nom in roles:
        try:
            cursor.execute(
                "INSERT INTO ROL (Cod_Rol, Nom_Rol) VALUES (%s, %s)",
                (cod, nom))
            conn.commit()
            print(f"✅ Rol '{nom}' creado")
        except Exception as e:
            if "Duplicate entry" in str(e):
                print(f"ℹ️  Rol '{nom}' ya existe")
            else:
                print(f"❌ Error rol '{nom}': {e}")

    # ─── 3. Usuario administrador ────────────────────────
    from werkzeug.security import generate_password_hash
    pwd_admin = generate_password_hash("admin123")
    try:
        cursor.execute("""
            INSERT INTO USUARIO
                (NumDoc_Usuario, TipoDoc_Usuario, Nom1_Usuario,
                 Nom2_Usuario, Ape1_Usuario, Ape2_Usuario,
                 Tel_Usuario, Mail_Usuario, Password)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, ("000001","CC","Admin","","Boyacos","",
              "3000000000","admin@losboyacos.com", pwd_admin))
        conn.commit()
        print("✅ Usuario administrador creado")
    except Exception as e:
        if "Duplicate entry" in str(e):
            print("ℹ️  Usuario admin ya existe")
        else:
            print(f"❌ Error admin: {e}")

    # ─── 4. Rol Admin → administrador ───────────────────
    try:
        cursor.execute(
            "INSERT INTO ROLXUSUARIO (Cod_Rol, NumDoc_Usuario) VALUES (%s,%s)",
            (1, "000001"))
        conn.commit()
        print("✅ Rol Admin asignado al administrador")
    except Exception as e:
        if "Duplicate entry" in str(e):
            print("ℹ️  Rol ya asignado")
        else:
            print(f"❌ Error asignar rol: {e}")

    # ─── 5. Usuario domiciliario demo ────────────────────
    pwd_domi = generate_password_hash("domi123")
    try:
        cursor.execute("""
            INSERT INTO USUARIO
                (NumDoc_Usuario, TipoDoc_Usuario, Nom1_Usuario,
                 Nom2_Usuario, Ape1_Usuario, Ape2_Usuario,
                 Tel_Usuario, Mail_Usuario, Password)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, ("000002","CC","Carlos","","Ramirez","",
              "3111111111","domiciliario@losboyacos.com", pwd_domi))
        conn.commit()
        print("✅ Usuario domiciliario demo creado")
    except Exception as e:
        if "Duplicate entry" in str(e):
            print("ℹ️  Usuario domiciliario ya existe")
        else:
            print(f"❌ Error domiciliario: {e}")

    try:
        cursor.execute(
            "INSERT INTO ROLXUSUARIO (Cod_Rol, NumDoc_Usuario) VALUES (%s,%s)",
            (3, "000002"))
        conn.commit()
        print("✅ Rol Domiciliario asignado")
    except Exception as e:
        if "Duplicate entry" in str(e):
            print("ℹ️  Rol ya asignado")
        else:
            print(f"❌ {e}")

    close_connection(conn)
    print("\n🎉 Base de datos lista!")
    print("─" * 45)
    print("👤 Admin:        admin@losboyacos.com  /  admin123")
    print("🛵 Domiciliario: domiciliario@losboyacos.com  /  domi123")
    print("─" * 45)

if __name__ == "__main__":
    seed_roles()
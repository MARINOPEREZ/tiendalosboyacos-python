# ═══════════════════════════════════════════════════════════════════════
# Servicio web de autenticación — Registro e Inicio de sesión
# Evidencia SENA: GA7-220501096-AA5-EV01 (Diseño y desarrollo de servicios web)
#
# Blueprint independiente del login por sesión que ya usa app.py (/login).
# Este servicio es JSON puro (stateless): pensado para ser consumido por
# cualquier cliente HTTP (curl, Postman, un front-end externo) sin depender
# de cookies de sesión de Flask.
# ═══════════════════════════════════════════════════════════════════════
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash

from config.db import get_connection, close_connection
from src.controllers.usuario_ctrl import UsuarioController

# Se registra en app.py con url_prefix="/api/auth" -> /api/auth/registro y /api/auth/login
auth_bp = Blueprint("auth", __name__)


# ─── SERVICIO DE REGISTRO ────────────────────────────────────────────────
@auth_bp.route("/registro", methods=["POST"])
def registro():
    """
    Recibe los datos de un usuario nuevo (JSON) y lo registra en la BD.

    Reutiliza UsuarioController.registrar_usuario, que ya se encarga de:
      - validar que los campos obligatorios estén presentes,
      - exigir contraseña de mínimo 6 caracteres,
      - rechazar documentos duplicados,
      - guardar la contraseña con hash (nunca en texto plano).
    """
    data = request.get_json(silent=True) or {}

    # Campos mínimos indispensables para poder crear el registro
    num_doc  = data.get("num_doc")
    mail     = data.get("mail")
    password = data.get("password")

    if not num_doc or not mail or not password:
        return jsonify({
            "ok": False,
            "mensaje": "Error en la autenticación",
            "detalle": "Documento, correo y contraseña son obligatorios"
        }), 400

    resultado = UsuarioController.registrar_usuario(
        num_doc    = num_doc,
        tipo_doc   = data.get("tipo_doc", "CC"),
        nom1       = data.get("nom1", ""),
        nom2       = data.get("nom2", ""),
        ape1       = data.get("ape1", ""),
        ape2       = data.get("ape2", ""),
        indicativo = data.get("indicativo", "+57"),
        tel        = data.get("tel", ""),
        mail       = mail,
        password   = password,
        id_rol     = data.get("id_rol", "2")  # 2 = Cliente por defecto
    )

    if resultado["ok"]:
        # Registro correcto -> 201 Created
        return jsonify({
            "ok": True,
            "mensaje": "Autenticación satisfactoria",
            "detalle": resultado["msg"]
        }), 201

    # Alguna validación de negocio falló (duplicado, datos inválidos, etc.)
    return jsonify({
        "ok": False,
        "mensaje": "Error en la autenticación",
        "detalle": resultado["msg"]
    }), 400


# ─── SERVICIO DE INICIO DE SESIÓN ────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Recibe correo y contraseña (JSON) y valida las credenciales contra la
    tabla USUARIO. Responde con el mensaje exacto pedido por la evidencia:
      - "Autenticación satisfactoria" si el correo existe y la contraseña
        coincide con el hash guardado.
      - "Error en la autenticación" en cualquier otro caso (usuario
        inexistente, contraseña incorrecta o datos faltantes).
    """
    data     = request.get_json(silent=True) or {}
    mail     = data.get("mail")
    password = data.get("password")

    if not mail or not password:
        return jsonify({"ok": False, "mensaje": "Error en la autenticación"}), 400

    conn = get_connection()
    if not conn:
        return jsonify({"ok": False, "mensaje": "Error en la autenticación"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        # LEFT JOIN con rol para devolver también el rol del usuario autenticado
        cursor.execute("""
            SELECT u.NumDoc_Usuario, u.Nom1_Usuario, u.Ape1_Usuario,
                   u.Password, r.Nom_Rol
            FROM   usuario u
            LEFT JOIN rolxusuario ru ON u.NumDoc_Usuario = ru.NumDoc_Usuario
            LEFT JOIN rol r          ON ru.Cod_Rol = r.Cod_Rol
            WHERE  u.Mail_Usuario = %s
        """, (mail,))
        usuario = cursor.fetchone()
    finally:
        close_connection(conn)

    # Verificación de credenciales: el usuario debe existir Y el hash debe coincidir
    if usuario and check_password_hash(usuario["Password"], password):
        return jsonify({
            "ok": True,
            "mensaje": "Autenticación satisfactoria",
            "usuario": f"{usuario['Nom1_Usuario']} {usuario['Ape1_Usuario']}",
            "rol": usuario["Nom_Rol"] or "Cliente"
        }), 200

    return jsonify({"ok": False, "mensaje": "Error en la autenticación"}), 401

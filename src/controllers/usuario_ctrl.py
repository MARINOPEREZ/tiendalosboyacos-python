import sys
sys.path.append("../../")
from src.models.usuario import Usuario
from werkzeug.security import generate_password_hash

class UsuarioController:

    # ─── REGISTRAR ──────────────────────────────────────
    @staticmethod
    def registrar_usuario(num_doc, tipo_doc, nom1, nom2,
                          ape1, ape2, indicativo, tel, mail,
                          password, foto=None, id_rol="2"):
        if not num_doc or not nom1 or not ape1 or not mail:
            return {"ok": False, "msg": "Documento, nombre, apellido y correo son obligatorios"}
        if not password or len(password) < 6:
            return {"ok": False, "msg": "La contraseña debe tener mínimo 6 caracteres"}
        existente = Usuario.buscar(num_doc)
        if existente:
            return {"ok": False, "msg": f"Ya existe un usuario con documento {num_doc}"}
        password_hash = generate_password_hash(password)
        Usuario.registrar(num_doc, tipo_doc, nom1, nom2,
                          ape1, ape2, indicativo, tel,
                          mail, password_hash, foto, id_rol)
        return {"ok": True, "msg": f"Usuario '{nom1} {ape1}' registrado correctamente"}

    # ─── BUSCAR ─────────────────────────────────────────
    @staticmethod
    def buscar_usuario(num_doc):
        if not num_doc:
            return {"ok": False, "msg": "Documento requerido"}
        usuario = Usuario.buscar(num_doc)
        if not usuario:
            return {"ok": False, "msg": "Usuario no encontrado"}
        return {"ok": True, "data": usuario}

    # ─── LISTAR ─────────────────────────────────────────
    @staticmethod
    def listar_usuarios():
        usuarios = Usuario.listar()
        if not usuarios:
            return {"ok": False, "msg": "No hay usuarios registrados"}
        return {"ok": True, "data": usuarios}

    # ─── EDITAR ─────────────────────────────────────────
    @staticmethod
    def editar_usuario(num_doc, nom1, nom2, ape1, ape2,
                       indicativo, tel, mail,
                       nueva_password=None, confirmar_password=None,
                       foto=None):
        if not num_doc:
            return {"ok": False, "msg": "Documento requerido"}
        password_hash = None
        if nueva_password:
            if len(nueva_password) < 6:
                return {"ok": False, "msg": "La nueva contraseña debe tener mínimo 6 caracteres"}
            if nueva_password != confirmar_password:
                return {"ok": False, "msg": "Las contraseñas no coinciden"}
            password_hash = generate_password_hash(nueva_password)
        Usuario.editar(num_doc, nom1, nom2, ape1, ape2,
                       indicativo, tel, mail, password_hash, foto)
        if password_hash:
            return {"ok": True, "msg": "Usuario y contraseña actualizados correctamente"}
        return {"ok": True, "msg": "Usuario actualizado correctamente"}

    # ─── ELIMINAR ───────────────────────────────────────
    @staticmethod
    def eliminar_usuario(num_doc):
        if not num_doc:
            return {"ok": False, "msg": "Documento requerido"}
        usuario = Usuario.buscar(num_doc)
        if not usuario:
            return {"ok": False, "msg": "Usuario no encontrado"}
        try:
            Usuario.eliminar(num_doc)
            return {"ok": True, "msg": "Usuario eliminado correctamente"}
        except Exception as e:
            return {"ok": False, "msg": str(e)}
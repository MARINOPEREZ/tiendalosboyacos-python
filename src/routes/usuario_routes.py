from flask import Blueprint, request, jsonify
from src.controllers.usuario_ctrl import UsuarioController

usuario_bp = Blueprint("usuarios", __name__)

# ─── LISTAR TODOS ───────────────────────────────────────
@usuario_bp.route("/usuarios", methods=["GET"])
def listar():
    resultado = UsuarioController.listar_usuarios()
    return jsonify(resultado)

# ─── BUSCAR POR DOCUMENTO ───────────────────────────────
@usuario_bp.route("/usuarios/<num_doc>", methods=["GET"])
def buscar(num_doc):
    resultado = UsuarioController.buscar_usuario(num_doc)
    return jsonify(resultado)

# ─── REGISTRAR ──────────────────────────────────────────
@usuario_bp.route("/usuarios/registrar", methods=["POST"])
def registrar():
    data = request.get_json()
    resultado = UsuarioController.registrar_usuario(
        data["num_doc"],
        data["tipo_doc"],
        data["nom1"],
        data["nom2"],
        data["ape1"],
        data["ape2"],
        data["tel"],
        data["mail"]
    )
    return jsonify(resultado)
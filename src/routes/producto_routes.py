from flask import Blueprint, request, jsonify
from src.controllers.producto_ctrl import ProductoController

producto_bp = Blueprint("productos", __name__)

# ─── LISTAR TODOS ───────────────────────────────────────
@producto_bp.route("/productos", methods=["GET"])
def listar():
    resultado = ProductoController.listar_productos()
    return jsonify(resultado)

# ─── BUSCAR POR ID ──────────────────────────────────────
@producto_bp.route("/productos/<int:id>", methods=["GET"])
def buscar(id):
    resultado = ProductoController.buscar_producto(id)
    return jsonify(resultado)

# ─── AGREGAR ────────────────────────────────────────────
@producto_bp.route("/productos/agregar", methods=["POST"])
def agregar():
    data = request.get_json()
    resultado = ProductoController.agregar_producto(
        data["nom"],
        data["descripcion"],
        data["vlr_unitario"],
        data["cant_stock"],
        data["fech_vencimiento"],
        data["iva"]
    )
    return jsonify(resultado)

# ─── EDITAR ─────────────────────────────────────────────
@producto_bp.route("/productos/editar/<int:id>", methods=["PUT"])
def editar(id):
    data = request.get_json()
    resultado = ProductoController.editar_producto(
        id,
        data["nom"],
        data["descripcion"],
        data["vlr_unitario"],
        data["cant_stock"],
        data["fech_vencimiento"],
        data["iva"]
    )
    return jsonify(resultado)

# ─── ELIMINAR ───────────────────────────────────────────
@producto_bp.route("/productos/eliminar/<int:id>", methods=["DELETE"])
def eliminar(id):
    resultado = ProductoController.eliminar_producto(id)
    return jsonify(resultado)
# ═══════════════════════════════════════════════════════════════════════
# Servicio web de categorías — expone en JSON lo que antes solo existía
# como vistas HTML (app.py: /categorias, /categorias/nueva, ...).
#
# Evidencia SENA: GA8-220501096-AA2-EV02 (módulos móvil según
# requerimientos del proyecto). El catálogo de la app Android necesita
# poder listar categorías y saber a qué categorías pertenece un producto,
# así que este módulo reutiliza CategoriaController tal como
# producto_routes.py reutiliza ProductoController — mismo patrón, para
# no romper nada de lo ya entregado en AA5-EV01.
# ═══════════════════════════════════════════════════════════════════════
from flask import Blueprint, jsonify
from src.controllers.categoria_ctrl import CategoriaController

# Se registra en app.py con url_prefix="/api" -> /api/categorias, etc.
categoria_bp = Blueprint("categorias", __name__)


# ─── LISTAR TODAS ───────────────────────────────────────
@categoria_bp.route("/categorias", methods=["GET"])
def listar():
    resultado = CategoriaController.listar_categorias()
    return jsonify(resultado)


# ─── BUSCAR POR ID ──────────────────────────────────────
@categoria_bp.route("/categorias/<int:id>", methods=["GET"])
def buscar(id):
    resultado = CategoriaController.buscar_categoria(id)
    return jsonify(resultado)


# ─── CATEGORÍAS DE UN PRODUCTO ──────────────────────────
# Vive aquí (y no en producto_routes.py) porque solo necesita el modelo
# Categoria — así producto_routes.py, ya entregado como evidencia
# AA5-EV01, queda intacto.
@categoria_bp.route("/productos/<int:id>/categorias", methods=["GET"])
def categorias_de_producto(id):
    resultado = CategoriaController.obtener_categorias_de_producto(id)
    return jsonify(resultado)

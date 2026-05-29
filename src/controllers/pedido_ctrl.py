import sys
sys.path.append("../../")
from src.models.pedido import Pedido
from src.models.producto import Producto

ESTADOS_VALIDOS = ["Pendiente","Confirmado","En camino","Entregado","Cancelado"]

class PedidoController:

    # ─── CREAR ───────────────────────────────────────────
    @staticmethod
    def crear_pedido(num_doc, items, direccion="", observaciones=""):
        """
        items: [{"id_producto":X, "cantidad":Y, "precio_unitario":Z}, ...]
        """
        if not num_doc:
            return {"ok": False, "msg": "Debes iniciar sesión para hacer un pedido"}
        if not items or len(items) == 0:
            return {"ok": False, "msg": "El carrito está vacío"}

        # Validar stock disponible para cada ítem
        items_validados = []
        for item in items:
            producto = Producto.buscar(item["id_producto"])
            if not producto:
                return {"ok": False,
                        "msg": f"El producto ID {item['id_producto']} ya no existe"}
            if producto["Cant_Stock"] < item["cantidad"]:
                return {"ok": False,
                        "msg": f"Stock insuficiente para '{producto['Nom_Producto']}'. "
                               f"Disponible: {producto['Cant_Stock']}"}
            items_validados.append({
                "id_producto":    item["id_producto"],
                "nombre":         producto["Nom_Producto"],
                "cantidad":       item["cantidad"],
                "precio_unitario": float(producto["Vlr_Unitario"])
            })

        total = sum(i["cantidad"] * i["precio_unitario"] for i in items_validados)
        id_pedido = Pedido.crear(num_doc, total, items_validados,
                                 direccion, observaciones)
        if not id_pedido:
            return {"ok": False, "msg": "Error al guardar el pedido. Intenta de nuevo."}

        return {"ok": True,
                "msg": f"¡Pedido #{id_pedido} confirmado! Total: ${total:,.0f}",
                "id_pedido": id_pedido,
                "total": total}

    # ─── CAMBIAR ESTADO ──────────────────────────────────
    @staticmethod
    def cambiar_estado(id_pedido, nuevo_estado):
        if nuevo_estado not in ESTADOS_VALIDOS:
            return {"ok": False,
                    "msg": f"Estado inválido. Válidos: {', '.join(ESTADOS_VALIDOS)}"}
        pedido = Pedido.buscar(id_pedido)
        if not pedido:
            return {"ok": False, "msg": "Pedido no encontrado"}
        Pedido.actualizar_estado(id_pedido, nuevo_estado)
        return {"ok": True, "msg": f"Pedido #{id_pedido} actualizado a '{nuevo_estado}'"}
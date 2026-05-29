import sys
sys.path.append("../../")
from src.models.venta    import Venta
from src.models.producto import Producto

ESTADOS_VALIDOS = ["Pendiente","Confirmado","En camino","Entregado","Cancelado"]

class VentaController:

    # ─── CREAR VENTA ─────────────────────────────────────────
    @staticmethod
    def crear_venta(num_doc, items, direccion="",
                    observaciones="", metodo_pago="Efectivo",
                    tipo_entrega="Envio", id_qr=None):
        if not num_doc:
            return {"ok": False,
                    "msg": "Debes iniciar sesión para hacer un pedido"}
        if not items:
            return {"ok": False, "msg": "El carrito está vacío"}

        items_validados = []
        for item in items:
            producto = Producto.buscar(item["id_producto"])
            if not producto:
                return {"ok": False,
                        "msg": f"El producto ID {item['id_producto']} ya no existe"}

            stock_disponible = int(float(str(producto["Cant_Stock"])))
            cantidad_pedida  = int(item["cantidad"])

            if stock_disponible < cantidad_pedida:
                return {"ok": False,
                        "msg": (f"Stock insuficiente para "
                                f"'{producto['Nom_Producto']}'. "
                                f"Disponible: {stock_disponible}")}

            items_validados.append({
                "id_producto":     int(producto["Id_Producto"]),
                "nombre":          producto["Nom_Producto"],
                "cantidad":        cantidad_pedida,
                "precio_unitario": float(producto["Vlr_Unitario"])
            })

        total = sum(i["cantidad"] * i["precio_unitario"]
                    for i in items_validados)

        try:
            id_venta = Venta.crear(num_doc, total, items_validados,
                                   direccion, observaciones,
                                   metodo_pago, tipo_entrega, id_qr)
        except Exception as e:
            return {"ok": False, "msg": str(e)}

        return {
            "ok":       True,
            "msg":      (f"¡Venta #{id_venta} confirmada! "
                         f"Total: ${total:,.0f}"),
            "id_venta": id_venta,
            "total":    total
        }

    # ─── CAMBIAR ESTADO ──────────────────────────────────────
    @staticmethod
    def cambiar_estado(id_venta, nuevo_estado):
        if nuevo_estado not in ESTADOS_VALIDOS:
            return {"ok": False,
                    "msg": f"Estado inválido. Válidos: {', '.join(ESTADOS_VALIDOS)}"}
        venta = Venta.buscar(id_venta)
        if not venta:
            return {"ok": False, "msg": "Venta no encontrada"}
        Venta.actualizar_estado(id_venta, nuevo_estado)
        return {"ok": True,
                "msg": f"Venta #{id_venta} → '{nuevo_estado}'"}
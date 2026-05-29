import sys
sys.path.append("../../")
from src.models.producto import Producto

class ProductoController:

    @staticmethod
    def agregar_producto(nom, descripcion, vlr_unitario, cant_stock,
                         fech_vencimiento, iva, imagen=None,
                         ids_categorias=None):
        if not nom or not vlr_unitario:
            return {"ok": False, "msg": "Nombre y precio son obligatorios"}
        if float(vlr_unitario) <= 0:
            return {"ok": False, "msg": "El precio debe ser mayor a 0"}
        if int(cant_stock) < 0:
            return {"ok": False, "msg": "El stock no puede ser negativo"}
        try:
            Producto.agregar(nom, descripcion, vlr_unitario,
                             cant_stock, fech_vencimiento, iva,
                             imagen, ids_categorias)
        except Exception as e:
            return {"ok": False, "msg": str(e)}
        return {"ok": True, "msg": f"Producto '{nom}' agregado correctamente"}

    @staticmethod
    def listar_productos():
        productos = Producto.listar()
        if not productos:
            return {"ok": False, "msg": "No hay productos registrados"}
        return {"ok": True, "data": productos}

    @staticmethod
    def buscar_producto(id_producto):
        if not id_producto:
            return {"ok": False, "msg": "ID de producto requerido"}
        producto = Producto.buscar(id_producto)
        if not producto:
            return {"ok": False, "msg": "Producto no encontrado"}
        return {"ok": True, "data": producto}

    @staticmethod
    def editar_producto(id_producto, nom, descripcion, vlr_unitario,
                        cant_stock, fech_vencimiento, iva,
                        imagen=None, ids_categorias=None):
        if not id_producto:
            return {"ok": False, "msg": "ID de producto requerido"}
        if float(vlr_unitario) <= 0:
            return {"ok": False, "msg": "El precio debe ser mayor a 0"}
        try:
            Producto.editar(id_producto, nom, descripcion, vlr_unitario,
                            cant_stock, fech_vencimiento, iva,
                            imagen, ids_categorias)
        except Exception as e:
            return {"ok": False, "msg": str(e)}
        return {"ok": True, "msg": "Producto actualizado correctamente"}

    @staticmethod
    def eliminar_producto(id_producto):
        if not id_producto:
            return {"ok": False, "msg": "ID de producto requerido"}
        producto = Producto.buscar(id_producto)
        if not producto:
            return {"ok": False, "msg": "Producto no encontrado"}
        try:
            # Intentar borrado físico primero
            Producto.eliminar_fisico(id_producto)
            return {"ok": True, "msg": f"Producto '{producto['Nom_Producto']}' eliminado"}
        except Exception:
            # Si tiene ventas asociadas → borrado lógico
            Producto.eliminar(id_producto)
            return {"ok": True,
                    "msg": (f"Producto '{producto['Nom_Producto']}' desactivado — "
                            f"tiene ventas registradas y no puede borrarse definitivamente")}
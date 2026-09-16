import sys
sys.path.append("../../")
from src.models.categoria import Categoria

class CategoriaController:

    # ─── LISTAR ─────────────────────────────────────────
    @staticmethod
    def listar_categorias():
        categorias = Categoria.listar()
        if not categorias:
            return {"ok": False, "msg": "No hay categorías registradas"}
        return {"ok": True, "data": categorias}

    # ─── BUSCAR ─────────────────────────────────────────
    @staticmethod
    def buscar_categoria(id_categoria):
        if not id_categoria:
            return {"ok": False, "msg": "ID de categoría requerido"}
        categoria = Categoria.buscar(id_categoria)
        if not categoria:
            return {"ok": False, "msg": "Categoría no encontrada"}
        return {"ok": True, "data": categoria}

    # ─── AGREGAR ────────────────────────────────────────
    @staticmethod
    def agregar_categoria(nom_categoria):
        nom_categoria = (nom_categoria or "").strip()
        if not nom_categoria:
            return {"ok": False, "msg": "El nombre de la categoría es obligatorio"}
        if len(nom_categoria) > 30:
            return {"ok": False, "msg": "El nombre no puede superar 30 caracteres"}

        existentes = Categoria.listar() or []
        if any(c["Nom_Categoria"].strip().lower() == nom_categoria.lower()
               for c in existentes):
            return {"ok": False,
                    "msg": f"Ya existe una categoría llamada '{nom_categoria}'"}

        try:
            Categoria.crear(nom_categoria)
        except Exception as e:
            return {"ok": False, "msg": str(e)}
        return {"ok": True, "msg": f"Categoría '{nom_categoria}' creada correctamente"}

    # ─── EDITAR ─────────────────────────────────────────
    @staticmethod
    def editar_categoria(id_categoria, nom_categoria):
        if not id_categoria:
            return {"ok": False, "msg": "ID de categoría requerido"}
        nom_categoria = (nom_categoria or "").strip()
        if not nom_categoria:
            return {"ok": False, "msg": "El nombre de la categoría es obligatorio"}
        if len(nom_categoria) > 30:
            return {"ok": False, "msg": "El nombre no puede superar 30 caracteres"}
        try:
            Categoria.editar(id_categoria, nom_categoria)
        except Exception as e:
            return {"ok": False, "msg": str(e)}
        return {"ok": True, "msg": "Categoría actualizada correctamente"}

    # ─── CATEGORÍAS DE UN PRODUCTO (AA2-EV02 — módulo móvil) ─
    @staticmethod
    def obtener_categorias_de_producto(id_producto):
        """
        Devuelve las categorías asignadas a un producto (tabla N:M
        CATEGORIAXPRODUCTO). Se agrega para el catálogo de la app Android,
        que necesita mostrar a qué categoría(s) pertenece cada producto
        en la pantalla de detalle.
        """
        if not id_producto:
            return {"ok": False, "msg": "ID de producto requerido"}
        categorias = Categoria.categorias_de_producto(id_producto)
        return {"ok": True, "data": categorias or []}

    # ─── ELIMINAR ───────────────────────────────────────
    @staticmethod
    def eliminar_categoria(id_categoria):
        if not id_categoria:
            return {"ok": False, "msg": "ID de categoría requerido"}
        categoria = Categoria.buscar(id_categoria)
        if not categoria:
            return {"ok": False, "msg": "Categoría no encontrada"}

        total_productos = Categoria.contar_productos(id_categoria)
        if total_productos > 0:
            return {"ok": False,
                    "msg": (f"No se puede eliminar '{categoria['Nom_Categoria']}': "
                            f"tiene {total_productos} producto(s) asociado(s)")}
        try:
            Categoria.eliminar(id_categoria)
        except Exception:
            return {"ok": False,
                    "msg": "No se pudo eliminar: la categoría todavía tiene "
                           "productos asociados"}
        return {"ok": True, "msg": f"Categoría '{categoria['Nom_Categoria']}' eliminada"}

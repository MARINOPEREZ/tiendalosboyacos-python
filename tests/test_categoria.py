"""
Pruebas unitarias del nuevo módulo de gestión de Categorías
(src/models/categoria.py y src/controllers/categoria_ctrl.py),
agregado en esta sesión porque antes solo existía la asociación
producto-categoría, sin alta/edición/baja del catálogo de categorías.
"""
from unittest.mock import MagicMock, patch

from src.models.categoria import Categoria
from src.controllers.categoria_ctrl import CategoriaController


# ─── MODELO ───────────────────────────────────────────────────────

@patch("src.models.categoria.get_connection")
def test_crear_categoria_inserta_y_retorna_id(mock_get_conn):
    cursor = MagicMock()
    cursor.lastrowid = 11
    conn = MagicMock()
    conn.cursor.return_value = cursor
    conn.is_connected.return_value = True
    mock_get_conn.return_value = conn

    id_categoria = Categoria.crear("Lácteos")

    assert id_categoria == 11
    assert "INSERT INTO categoria" in cursor.execute.call_args[0][0]
    conn.commit.assert_called_once()


@patch("src.models.categoria.get_connection")
def test_eliminar_categoria_propaga_error_de_fk(mock_get_conn):
    """Si la categoría todavía tiene productos, la FK RESTRICT de la BD
    debe rechazar el DELETE — el modelo debe re-lanzar ese error."""
    cursor = MagicMock()
    cursor.execute.side_effect = Exception("Cannot delete or update a parent row: "
                                            "a foreign key constraint fails")
    conn = MagicMock()
    conn.cursor.return_value = cursor
    conn.is_connected.return_value = True
    mock_get_conn.return_value = conn

    try:
        Categoria.eliminar(3)
        assert False, "se esperaba que eliminar() propagara el error de FK"
    except Exception:
        pass
    conn.rollback.assert_called_once()


# ─── CONTROLADOR ──────────────────────────────────────────────────

@patch("src.controllers.categoria_ctrl.Categoria")
def test_agregar_categoria_rechaza_nombre_vacio(mock_categoria):
    resultado = CategoriaController.agregar_categoria("   ")
    assert resultado["ok"] is False
    assert "obligatorio" in resultado["msg"]
    mock_categoria.crear.assert_not_called()


@patch("src.controllers.categoria_ctrl.Categoria")
def test_agregar_categoria_rechaza_duplicado_sin_importar_mayusculas(mock_categoria):
    mock_categoria.listar.return_value = [{"Nom_Categoria": "Lácteos"}]

    resultado = CategoriaController.agregar_categoria("lácteos")

    assert resultado["ok"] is False
    assert "Ya existe" in resultado["msg"]
    mock_categoria.crear.assert_not_called()


@patch("src.controllers.categoria_ctrl.Categoria")
def test_agregar_categoria_ok(mock_categoria):
    mock_categoria.listar.return_value = [{"Nom_Categoria": "Carnes"}]

    resultado = CategoriaController.agregar_categoria("Lácteos")

    assert resultado["ok"] is True
    mock_categoria.crear.assert_called_once_with("Lácteos")


@patch("src.controllers.categoria_ctrl.Categoria")
def test_eliminar_categoria_bloqueada_si_tiene_productos(mock_categoria):
    mock_categoria.buscar.return_value = {"Id_Categoria": 3, "Nom_Categoria": "Lácteos"}
    mock_categoria.contar_productos.return_value = 4

    resultado = CategoriaController.eliminar_categoria(3)

    assert resultado["ok"] is False
    assert "4 producto" in resultado["msg"]
    mock_categoria.eliminar.assert_not_called()


@patch("src.controllers.categoria_ctrl.Categoria")
def test_eliminar_categoria_ok_sin_productos_asociados(mock_categoria):
    mock_categoria.buscar.return_value = {"Id_Categoria": 3, "Nom_Categoria": "Lácteos"}
    mock_categoria.contar_productos.return_value = 0

    resultado = CategoriaController.eliminar_categoria(3)

    assert resultado["ok"] is True
    mock_categoria.eliminar.assert_called_once_with(3)


# ─── CATEGORÍAS DE UN PRODUCTO (AA2-EV02) ────────────────────────

@patch("src.controllers.categoria_ctrl.Categoria")
def test_obtener_categorias_de_producto_requiere_id(mock_categoria):
    resultado = CategoriaController.obtener_categorias_de_producto(None)
    assert resultado["ok"] is False
    assert "requerido" in resultado["msg"]
    mock_categoria.categorias_de_producto.assert_not_called()


@patch("src.controllers.categoria_ctrl.Categoria")
def test_obtener_categorias_de_producto_ok(mock_categoria):
    mock_categoria.categorias_de_producto.return_value = [
        {"Id_Categoria": 1, "Nom_Categoria": "Lácteos"},
        {"Id_Categoria": 2, "Nom_Categoria": "Artesanías"},
    ]

    resultado = CategoriaController.obtener_categorias_de_producto(18)

    assert resultado["ok"] is True
    assert len(resultado["data"]) == 2
    mock_categoria.categorias_de_producto.assert_called_once_with(18)


@patch("src.controllers.categoria_ctrl.Categoria")
def test_obtener_categorias_de_producto_sin_categorias_devuelve_lista_vacia(mock_categoria):
    mock_categoria.categorias_de_producto.return_value = None

    resultado = CategoriaController.obtener_categorias_de_producto(99)

    assert resultado["ok"] is True
    assert resultado["data"] == []

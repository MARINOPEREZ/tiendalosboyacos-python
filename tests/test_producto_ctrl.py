"""Pruebas unitarias de ProductoController (src/controllers/producto_ctrl.py)."""
from unittest.mock import patch

from src.controllers.producto_ctrl import ProductoController


@patch("src.controllers.producto_ctrl.Producto")
def test_agregar_producto_rechaza_precio_negativo(mock_producto):
    resultado = ProductoController.agregar_producto(
        "Café", "desc", -500, 10, None, 19)
    assert resultado["ok"] is False
    assert "mayor a 0" in resultado["msg"]
    mock_producto.agregar.assert_not_called()


@patch("src.controllers.producto_ctrl.Producto")
def test_agregar_producto_rechaza_precio_cero_como_campo_faltante(mock_producto):
    # 0 es "falsy" en Python, así que cae en la validación de campos
    # obligatorios (nom/vlr_unitario) antes de llegar al chequeo de "> 0".
    # Se documenta este comportamiento real del controlador tal como está.
    resultado = ProductoController.agregar_producto(
        "Café", "desc", 0, 10, None, 19)
    assert resultado["ok"] is False
    assert "obligatorios" in resultado["msg"]
    mock_producto.agregar.assert_not_called()


@patch("src.controllers.producto_ctrl.Producto")
def test_agregar_producto_rechaza_stock_negativo(mock_producto):
    resultado = ProductoController.agregar_producto(
        "Café", "desc", 1000, -5, None, 19)
    assert resultado["ok"] is False
    assert "negativo" in resultado["msg"]
    mock_producto.agregar.assert_not_called()


@patch("src.controllers.producto_ctrl.Producto")
def test_agregar_producto_ok(mock_producto):
    resultado = ProductoController.agregar_producto(
        "Café", "desc", 15000, 10, "2025-12-31", 19)
    assert resultado["ok"] is True
    mock_producto.agregar.assert_called_once()


@patch("src.controllers.producto_ctrl.Producto")
def test_eliminar_producto_no_encontrado(mock_producto):
    mock_producto.buscar.return_value = None
    resultado = ProductoController.eliminar_producto(999)
    assert resultado["ok"] is False
    assert "no encontrado" in resultado["msg"].lower()


@patch("src.controllers.producto_ctrl.Producto")
def test_eliminar_producto_con_ventas_hace_borrado_logico(mock_producto):
    mock_producto.buscar.return_value = {"Id_Producto": 5, "Nom_Producto": "Café"}
    # Simula la FK que impide el borrado físico porque hay ventas asociadas
    mock_producto.eliminar_fisico.side_effect = Exception("fk constraint")

    resultado = ProductoController.eliminar_producto(5)

    assert resultado["ok"] is True
    assert "desactivado" in resultado["msg"].lower()
    mock_producto.eliminar.assert_called_once_with(5)

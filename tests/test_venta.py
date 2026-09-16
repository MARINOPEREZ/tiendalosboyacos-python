"""
Pruebas unitarias del MODELO Venta (src/models/venta.py) y su controlador.

Cubren específicamente el hallazgo corregido en esta sesión: una venta
descontaba PRODUCTO.Cant_Stock pero nunca actualizaba
INVENTARIO.Cant_Inventario (ver migraciones/2026_08_09_fix_esquema.sql,
sección 8) — lo que hacía que ambos valores de stock divergieran después
de cada venta.
"""
from unittest.mock import MagicMock, patch

from src.models.venta import Venta
from src.controllers.venta_ctrl import VentaController


def _conn_cursor_mock(lastrowid=99, rowcount=1, nuevo_stock=7):
    cursor = MagicMock()
    cursor.lastrowid = lastrowid
    cursor.rowcount = rowcount
    cursor.fetchone.return_value = (nuevo_stock,)
    conn = MagicMock()
    conn.cursor.return_value = cursor
    conn.is_connected.return_value = True
    return conn, cursor


ITEM = {"id_producto": 5, "nombre": "Café Boyacense",
        "cantidad": 3, "precio_unitario": 15000.0}


@patch("src.models.venta.Producto")
@patch("src.models.venta.get_connection")
def test_crear_venta_descuenta_stock_y_sincroniza_inventario(mock_get_conn, mock_producto):
    conn, cursor = _conn_cursor_mock(lastrowid=99, rowcount=1, nuevo_stock=7)
    mock_get_conn.return_value = conn

    id_venta = Venta.crear("123456", 45000.0, [ITEM])

    assert id_venta == 99
    conn.commit.assert_called_once()

    # La sincronización debe llamarse con el stock YA descontado (7),
    # no con el stock previo a la venta.
    mock_producto.sincronizar_inventario.assert_called_once()
    args = mock_producto.sincronizar_inventario.call_args.args
    assert args[1] == 5          # id_producto
    assert args[2] == 7          # nuevo stock, tras el descuento
    assert "venta #99" in args[3].lower()


@patch("src.models.venta.Producto")
@patch("src.models.venta.get_connection")
def test_crear_venta_con_stock_insuficiente_no_sincroniza_y_hace_rollback(mock_get_conn, mock_producto):
    conn, cursor = _conn_cursor_mock(lastrowid=99, rowcount=0)  # UPDATE no afectó filas
    mock_get_conn.return_value = conn

    try:
        Venta.crear("123456", 45000.0, [ITEM])
        assert False, "se esperaba una excepción por stock insuficiente"
    except Exception as e:
        assert "Stock insuficiente" in str(e)

    conn.rollback.assert_called_once()
    mock_producto.sincronizar_inventario.assert_not_called()


# ─── CONTROLADOR ─────────────────────────────────────────────────

@patch("src.controllers.venta_ctrl.Producto")
def test_crear_venta_rechaza_carrito_vacio(mock_producto):
    resultado = VentaController.crear_venta("123456", [])
    assert resultado["ok"] is False
    assert "carrito" in resultado["msg"].lower()


def test_crear_venta_rechaza_sin_sesion():
    resultado = VentaController.crear_venta(None, [{"id_producto": 1, "cantidad": 1}])
    assert resultado["ok"] is False
    assert "iniciar sesión" in resultado["msg"].lower()


@patch("src.controllers.venta_ctrl.Producto")
def test_crear_venta_rechaza_stock_insuficiente(mock_producto):
    mock_producto.buscar.return_value = {
        "Id_Producto": 5, "Nom_Producto": "Café Boyacense",
        "Cant_Stock": 2, "Vlr_Unitario": 15000.0}

    resultado = VentaController.crear_venta(
        "123456", [{"id_producto": 5, "cantidad": 10}])

    assert resultado["ok"] is False
    assert "stock insuficiente" in resultado["msg"].lower()


@patch("src.controllers.venta_ctrl.Venta")
@patch("src.controllers.venta_ctrl.Producto")
def test_cambiar_estado_rechaza_estado_invalido(mock_producto, mock_venta):
    resultado = VentaController.cambiar_estado(1, "Enviado a la luna")
    assert resultado["ok"] is False
    assert "inválido" in resultado["msg"].lower()
    mock_venta.actualizar_estado.assert_not_called()

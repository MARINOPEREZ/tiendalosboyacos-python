"""
Pruebas unitarias del MODELO Producto (src/models/producto.py).

Reemplaza el antiguo tests/test_modelos.py, que llamaba a
Usuario.registrar(...) con argumentos posicionales incompletos (faltaban
indicativo y password, ambos obligatorios) y solo imprimía resultados sin
ningún assert — no era realmente una prueba automatizable.

Estas pruebas no requieren una base de datos real: se aísla la capa de
acceso a datos simulando get_connection()/close_connection(), tal como
recomienda la buena práctica de pruebas unitarias (no depender de un
recurso externo para validar la lógica del módulo).
"""
from unittest.mock import MagicMock, patch

from src.models.producto import Producto


def _conn_cursor_mock(lastrowid=1):
    """Crea un par (conn, cursor) simulados listos para usar con Producto."""
    cursor = MagicMock()
    cursor.lastrowid = lastrowid
    conn = MagicMock()
    conn.cursor.return_value = cursor
    conn.is_connected.return_value = True
    return conn, cursor


@patch("src.models.producto.get_connection")
def test_agregar_inserta_producto_e_inventario(mock_get_conn):
    conn, cursor = _conn_cursor_mock(lastrowid=42)
    mock_get_conn.return_value = conn

    id_producto = Producto.agregar(
        "Café Boyacense", "Café premium 500g",
        15000, 50, "2025-12-31", 19)

    assert id_producto == 42
    sql_ejecutados = " || ".join(c.args[0] for c in cursor.execute.call_args_list)
    assert "INSERT INTO producto" in sql_ejecutados
    assert "INSERT INTO inventario" in sql_ejecutados
    conn.commit.assert_called_once()


@patch("src.models.producto.get_connection")
def test_editar_sincroniza_inventario_con_nuevo_stock(mock_get_conn):
    conn, cursor = _conn_cursor_mock()
    mock_get_conn.return_value = conn

    Producto.editar(42, "Café Boyacense", "Café premium 500g",
                     15000, 30, "2025-12-31", 19)

    sql_ejecutados = [c.args[0] for c in cursor.execute.call_args_list]
    assert any("UPDATE producto" in s for s in sql_ejecutados)
    inventario_calls = [c for c in cursor.execute.call_args_list
                        if "INSERT INTO inventario" in c.args[0]]
    assert len(inventario_calls) == 1
    # El nuevo stock (30) debe viajar como parámetro hacia INVENTARIO
    assert 30 in inventario_calls[0].args[1]
    conn.commit.assert_called_once()


@patch("src.models.producto.get_connection")
def test_eliminar_logico_desactiva_no_borra(mock_get_conn):
    conn, cursor = _conn_cursor_mock()
    mock_get_conn.return_value = conn

    Producto.eliminar(42)

    sql = cursor.execute.call_args[0][0]
    assert "UPDATE producto SET Activo = 0" in sql
    conn.commit.assert_called_once()


@patch("src.models.producto.get_connection")
def test_agregar_hace_rollback_si_falla_la_insercion(mock_get_conn):
    conn, cursor = _conn_cursor_mock()
    cursor.execute.side_effect = Exception("fallo simulado de BD")
    mock_get_conn.return_value = conn

    try:
        Producto.agregar("X", "Y", 1000, 1, None, 19)
        assert False, "se esperaba que agregar() propagara la excepción"
    except Exception:
        pass

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()

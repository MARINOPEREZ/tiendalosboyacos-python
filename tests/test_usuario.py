"""Pruebas unitarias de UsuarioController (src/controllers/usuario_ctrl.py)."""
from unittest.mock import patch
from werkzeug.security import check_password_hash

from src.controllers.usuario_ctrl import UsuarioController


@patch("src.controllers.usuario_ctrl.Usuario")
def test_registrar_usuario_ok_guarda_password_hasheada(mock_usuario):
    mock_usuario.buscar.return_value = None  # no existe todavía

    resultado = UsuarioController.registrar_usuario(
        "123456", "CC", "Juan", "", "Pérez", "",
        "+57", "3001234567", "juan@email.com", "clave123")

    assert resultado["ok"] is True
    mock_usuario.registrar.assert_called_once()
    password_guardada = mock_usuario.registrar.call_args.args[9]
    assert password_guardada != "clave123"                      # nunca texto plano
    assert check_password_hash(password_guardada, "clave123")   # pero verificable


@patch("src.controllers.usuario_ctrl.Usuario")
def test_registrar_usuario_rechaza_password_corta(mock_usuario):
    mock_usuario.buscar.return_value = None

    resultado = UsuarioController.registrar_usuario(
        "123456", "CC", "Juan", "", "Pérez", "",
        "+57", "3001234567", "juan@email.com", "abc")

    assert resultado["ok"] is False
    assert "6 caracteres" in resultado["msg"]
    mock_usuario.registrar.assert_not_called()


@patch("src.controllers.usuario_ctrl.Usuario")
def test_registrar_usuario_rechaza_documento_duplicado(mock_usuario):
    mock_usuario.buscar.return_value = {"NumDoc_Usuario": "123456"}

    resultado = UsuarioController.registrar_usuario(
        "123456", "CC", "Juan", "", "Pérez", "",
        "+57", "3001234567", "juan@email.com", "clave123")

    assert resultado["ok"] is False
    assert "Ya existe" in resultado["msg"]
    mock_usuario.registrar.assert_not_called()


@patch("src.controllers.usuario_ctrl.Usuario")
def test_editar_usuario_rechaza_passwords_que_no_coinciden(mock_usuario):
    resultado = UsuarioController.editar_usuario(
        "123456", "Juan", "", "Pérez", "", "+57", "3001234567",
        "juan@email.com", nueva_password="clave123",
        confirmar_password="otraclave")

    assert resultado["ok"] is False
    assert "no coinciden" in resultado["msg"].lower()
    mock_usuario.editar.assert_not_called()


@patch("src.controllers.usuario_ctrl.Usuario")
def test_eliminar_usuario_no_encontrado(mock_usuario):
    mock_usuario.buscar.return_value = None
    resultado = UsuarioController.eliminar_usuario("999999")
    assert resultado["ok"] is False
    assert "no encontrado" in resultado["msg"].lower()

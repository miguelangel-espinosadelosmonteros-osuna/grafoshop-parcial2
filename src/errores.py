"""Errores propios de la aplicación."""


class ErrorDeNegocio(Exception):
    """Una regla del negocio no se cumple (dato inválido, stock insuficiente, etc.).

    La interfaz muestra el mensaje tal cual al usuario.
    """

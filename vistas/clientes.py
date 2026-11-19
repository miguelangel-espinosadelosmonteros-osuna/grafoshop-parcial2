"""Pantalla Clientes: CRUD de clientes."""
import streamlit as st

from src import clientes
from src.errores import ErrorDeNegocio
from vistas.comun import avisar, limpiar, mostrar_aviso, tabla, ver_cypher


def mostrar() -> None:
    st.title("Clientes")
    mostrar_aviso()

    lista = clientes.listar()
    tabla(lista)
    ver_cypher(clientes.LISTAR, "Ver consulta Cypher (leer)")

    agregar, editar, eliminar = st.tabs(["Agregar", "Editar", "Eliminar"])

    with agregar:
        nombre = st.text_input("Nombre", key="cli_nombre")
        email = st.text_input("Correo", key="cli_email")
        ciudad = st.text_input("Ciudad", key="cli_ciudad")
        if st.button("Crear cliente", type="primary"):
            try:
                nuevo_id = clientes.crear(nombre, email, ciudad)
                avisar(f"Cliente {nuevo_id} creado.")
                limpiar("cli_nombre", "cli_email", "cli_ciudad")
                st.rerun()
            except ErrorDeNegocio as error:
                st.error(str(error))
        ver_cypher(clientes.CREAR, "Ver consulta Cypher (crear)")

    por_id = {c["id"]: c for c in lista}
    nombres = {c["id"]: f"{c['nombre']} ({c['id']})" for c in lista}

    with editar:
        if lista:
            elegido = st.selectbox("Cliente a editar", list(nombres), format_func=nombres.get,
                                   key="cli_editar")
            actual = por_id[elegido]
            nombre = st.text_input("Nombre", actual["nombre"], key=f"cli_ed_nombre_{elegido}")
            email = st.text_input("Correo", actual["email"], key=f"cli_ed_email_{elegido}")
            ciudad = st.text_input("Ciudad", actual["ciudad"], key=f"cli_ed_ciudad_{elegido}")
            if st.button("Guardar cambios", type="primary"):
                try:
                    clientes.actualizar(elegido, nombre, email, ciudad)
                    avisar(f"Cliente {elegido} actualizado.")
                    st.rerun()
                except ErrorDeNegocio as error:
                    st.error(str(error))
            ver_cypher(clientes.ACTUALIZAR, "Ver consulta Cypher (actualizar)")

    with eliminar:
        if lista:
            elegido = st.selectbox("Cliente a eliminar", list(nombres), format_func=nombres.get,
                                   key="cli_eliminar")
            st.caption("Se borran también sus pedidos y lo que tenga en el carrito.")
            if st.button("Eliminar cliente"):
                try:
                    clientes.eliminar(elegido)
                    avisar(f"Cliente {elegido} eliminado.")
                    st.rerun()
                except ErrorDeNegocio as error:
                    st.error(str(error))
            ver_cypher(clientes.ELIMINAR, "Ver consulta Cypher (eliminar)")

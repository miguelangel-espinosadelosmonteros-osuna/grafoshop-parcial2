"""Pantalla Catálogo: CRUD de productos."""
import streamlit as st

from src import productos
from src.errores import ErrorDeNegocio
from vistas.comun import DINERO, avisar, limpiar, mostrar_aviso, tabla, ver_cypher

NUEVA = "Nueva categoría..."


def _campo_categoria(clave: str, actual: str | None = None) -> str:
    """Selector de categoría con opción de escribir una nueva."""
    opciones = productos.categorias() + [NUEVA]
    indice = opciones.index(actual) if actual in opciones else 0
    elegida = st.selectbox("Categoría", opciones, index=indice, key=f"{clave}_cat")
    if elegida == NUEVA:
        return st.text_input("Nombre de la nueva categoría", key=f"{clave}_cat_nueva")
    return elegida


def mostrar() -> None:
    st.title("Catálogo de productos")
    mostrar_aviso()

    a, b = st.columns([1, 2])
    categoria = a.selectbox("Filtrar por categoría", ["Todas"] + productos.categorias())
    texto = b.text_input("Buscar por nombre")
    lista = productos.listar(None if categoria == "Todas" else categoria, texto)
    tabla(lista, precio=DINERO)
    st.caption(f"{len(lista)} productos")
    ver_cypher(productos.LISTAR, "Ver consulta Cypher (leer)")

    agregar, editar, eliminar = st.tabs(["Agregar", "Editar", "Eliminar"])

    with agregar:
        nombre = st.text_input("Nombre", key="nuevo_nombre")
        cat = _campo_categoria("nuevo")
        precio = st.number_input("Precio (MXN)", min_value=0.0, step=50.0, key="nuevo_precio")
        stock = st.number_input("Stock", min_value=0, step=1, key="nuevo_stock")
        if st.button("Crear producto", type="primary"):
            try:
                nuevo_id = productos.crear(nombre, cat, precio, stock)
                avisar(f"Producto {nuevo_id} creado.")
                limpiar("nuevo_nombre", "nuevo_precio", "nuevo_stock", "nuevo_cat_nueva")
                st.rerun()
            except ErrorDeNegocio as error:
                st.error(str(error))
        ver_cypher(productos.CREAR, "Ver consulta Cypher (crear)")

    todos = productos.listar()
    nombres = {p["id"]: f"{p['nombre']} ({p['id']})" for p in todos}

    with editar:
        if todos:
            elegido = st.selectbox("Producto a editar", list(nombres), format_func=nombres.get,
                                   key="editar_id")
            actual = productos.obtener(elegido)
            nombre = st.text_input("Nombre", actual["nombre"], key=f"ed_nombre_{elegido}")
            cat = _campo_categoria(f"ed_{elegido}", actual["categoria"])
            precio = st.number_input("Precio (MXN)", min_value=0.0, step=50.0,
                                     value=float(actual["precio"]), key=f"ed_precio_{elegido}")
            stock = st.number_input("Stock", min_value=0, step=1,
                                    value=int(actual["stock"]), key=f"ed_stock_{elegido}")
            if st.button("Guardar cambios", type="primary"):
                try:
                    productos.actualizar(elegido, nombre, cat, precio, stock)
                    avisar(f"Producto {elegido} actualizado.")
                    st.rerun()
                except ErrorDeNegocio as error:
                    st.error(str(error))
            ver_cypher(productos.ACTUALIZAR, "Ver consulta Cypher (actualizar)")

    with eliminar:
        if todos:
            elegido = st.selectbox("Producto a eliminar", list(nombres), format_func=nombres.get,
                                   key="eliminar_id")
            st.caption("Solo se pueden eliminar productos que no aparecen en ningún pedido.")
            if st.button("Eliminar producto"):
                try:
                    productos.eliminar(elegido)
                    avisar(f"Producto {elegido} eliminado.")
                    st.rerun()
                except ErrorDeNegocio as error:
                    st.error(str(error))
            ver_cypher(productos.ELIMINAR, "Ver consulta Cypher (eliminar)")

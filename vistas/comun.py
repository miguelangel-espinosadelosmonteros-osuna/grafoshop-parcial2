"""Funciones de apoyo que comparten todas las pantallas."""
import pandas as pd
import streamlit as st

from src import clientes, productos

DINERO = st.column_config.NumberColumn(format="dollar")

COLORES = {
    "Cliente": "#F4B183",
    "Pedido": "#BDD7EE",
    "Producto": "#C5E0B4",
    "Categoria": "#FFE699",
}


def avisar(mensaje: str) -> None:
    """Guarda un mensaje para mostrarlo después de recargar la pantalla."""
    st.session_state["aviso"] = mensaje


def limpiar(*claves: str) -> None:
    """Borra el valor guardado de los campos de un formulario."""
    for clave in claves:
        st.session_state.pop(clave, None)


def mostrar_aviso() -> None:
    mensaje = st.session_state.pop("aviso", None)
    if mensaje:
        st.success(mensaje)


def tabla(filas: list[dict], **columnas) -> None:
    """Muestra una lista de diccionarios como tabla."""
    st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch",
                 column_config=columnas or None)


def ver_cypher(consulta: str, titulo: str = "Ver consulta Cypher") -> None:
    """Muestra la consulta que se ejecutó en Neo4j."""
    with st.expander(titulo):
        st.code(consulta.strip(), language="cypher")


def elegir_cliente(etiqueta: str = "Cliente", clave: str = "cliente",
                   ultimo: bool = False) -> str | None:
    """Selector de cliente. Regresa el id elegido.

    Con ultimo=True aparece seleccionado el último de la lista en vez del primero.
    """
    lista = clientes.listar()
    if not lista:
        st.info("Todavía no hay clientes. Crea uno en la pantalla Clientes.")
        return None
    nombres = {c["id"]: f"{c['nombre']} ({c['id']})" for c in lista}
    inicial = len(nombres) - 1 if ultimo else 0
    return st.selectbox(etiqueta, list(nombres), index=inicial,
                        format_func=nombres.get, key=clave)


def elegir_producto(etiqueta: str = "Producto", clave: str = "producto") -> str | None:
    """Selector de producto. Regresa el id elegido."""
    lista = productos.listar()
    if not lista:
        st.info("Todavía no hay productos. Crea uno en la pantalla Catálogo.")
        return None
    nombres = {p["id"]: f"{p['nombre']} (${p['precio']:,.2f})" for p in lista}
    return st.selectbox(etiqueta, list(nombres), format_func=nombres.get, key=clave)


def dibujar_grafo(grafo: dict) -> None:
    """Dibuja nodos y relaciones con Graphviz (lenguaje DOT)."""
    lineas = [
        "digraph {",
        "  rankdir=LR; bgcolor=transparent;",
        '  node [style=filled, fontname="Helvetica", fontsize=11, color="#555555"];',
        '  edge [fontname="Helvetica", fontsize=9, color="#555555"];',
    ]
    ids = {}
    for numero, nodo in enumerate(grafo["nodos"]):
        ids[nodo["clave"]] = f"n{numero}"
        forma = "ellipse" if nodo["etiqueta"] == "Cliente" else "box"
        texto = f"{nodo['etiqueta']}\\n{nodo['nombre']}".replace('"', "'")
        color = COLORES.get(nodo["etiqueta"], "#DDDDDD")
        lineas.append(f'  n{numero} [label="{texto}", shape={forma}, fillcolor="{color}"];')
    for arista in grafo["aristas"]:
        texto = arista["tipo"]
        if arista.get("cantidad"):
            texto += f" x{arista['cantidad']}"
        lineas.append(f'  {ids[arista["origen"]]} -> {ids[arista["destino"]]} [label="{texto}"];')
    lineas.append("}")
    st.graphviz_chart("\n".join(lineas), width="stretch")

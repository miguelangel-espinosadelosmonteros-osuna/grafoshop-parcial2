"""Pantalla Recomendaciones: recorridos del grafo por cliente y por producto."""
import streamlit as st

from src import recomendaciones
from vistas.comun import DINERO, elegir_cliente, elegir_producto, tabla, ver_cypher


def mostrar() -> None:
    st.title("Recomendaciones")
    por_cliente, por_producto = st.tabs(["Para un cliente", "Para un producto"])

    with por_cliente:
        cliente_id = elegir_cliente(clave="rec_cliente")
        if cliente_id:
            st.subheader("Clientes como tú también compraron")
            sugerencias = recomendaciones.por_clientes_similares(cliente_id)
            if sugerencias:
                tabla(sugerencias, precio=DINERO)
                st.caption("Puntaje: suma de productos en común con los clientes que lo compraron.")
            else:
                st.info("Este cliente no tiene compras todavía, así que se muestran "
                        "los productos más vendidos de la tienda.")
                tabla(recomendaciones.mas_vendidos(), precio=DINERO)
            ver_cypher(recomendaciones.POR_CLIENTES_SIMILARES)

            st.subheader("Clientes con gustos parecidos")
            parecidos = recomendaciones.clientes_similares(cliente_id)
            if parecidos:
                tabla(parecidos)
                st.caption("Jaccard = productos en común / productos distintos entre los dos "
                           "clientes. Va de 0 (nada en común) a 1 (compraron lo mismo).")
            else:
                st.caption("No hay clientes con productos en común.")
            ver_cypher(recomendaciones.CLIENTES_SIMILARES)

    with por_producto:
        producto_id = elegir_producto(clave="rec_producto")
        if producto_id:
            st.subheader("Se compra junto con")
            juntos = recomendaciones.comprados_juntos(producto_id)
            if juntos:
                tabla(juntos, precio=DINERO)
            else:
                st.caption("Este producto todavía no aparece en pedidos con otros productos.")
            ver_cypher(recomendaciones.COMPRADOS_JUNTOS)

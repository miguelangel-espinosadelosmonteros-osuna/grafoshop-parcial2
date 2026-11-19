"""Pantalla Explorador: camino más corto y vecindad de un cliente."""
import streamlit as st

from src import grafo
from src.errores import ErrorDeNegocio
from vistas.comun import dibujar_grafo, elegir_cliente, ver_cypher


def mostrar() -> None:
    st.title("Explorador del grafo")
    camino, vecindad = st.tabs(["Camino más corto", "Vecindad de un cliente"])

    with camino:
        st.write("Busca cómo se conectan dos clientes a través de sus pedidos y productos.")
        a, b = st.columns(2)
        with a:
            origen = elegir_cliente("Desde", clave="camino_origen")
        with b:
            destino = elegir_cliente("Hasta", clave="camino_destino", ultimo=True)
        if origen and destino:
            try:
                resultado = grafo.camino_mas_corto(origen, destino)
                if resultado is None:
                    st.info("No hay ningún camino entre estos clientes: "
                            "no comparten productos, ni directa ni indirectamente.")
                else:
                    st.metric("Saltos", resultado["saltos"])
                    dibujar_grafo(resultado)
                    st.caption(" → ".join(resultado["pasos"]))
            except ErrorDeNegocio as error:
                st.warning(str(error))
        ver_cypher(grafo.CAMINO_MAS_CORTO)

    with vecindad:
        st.write("Todo lo que está a 1 o 2 saltos del cliente: carrito, pedidos y productos.")
        cliente_id = elegir_cliente(clave="vecindad_cliente")
        if cliente_id:
            resultado = grafo.vecindad_cliente(cliente_id)
            if resultado["nodos"]:
                dibujar_grafo(resultado)
            else:
                st.info("Este cliente no tiene pedidos ni productos en el carrito.")
        ver_cypher(grafo.VECINDAD_CLIENTE)

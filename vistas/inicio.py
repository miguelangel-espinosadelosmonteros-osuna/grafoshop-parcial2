"""Pantalla de inicio: estado de la conexión y resumen del grafo."""
import pandas as pd
import streamlit as st

from src import db, grafo, recomendaciones
from src.config import cargar_configuracion
from vistas.comun import DINERO, tabla, ver_cypher


def mostrar() -> None:
    st.title("GrafoShop")
    st.write("Tienda en línea con recomendaciones calculadas sobre un grafo en Neo4j AuraDB.")

    cfg = cargar_configuracion()
    info = db.info_servidor()
    st.subheader("Conexión")
    a, b, c = st.columns(3)
    a.metric("Servidor", info["direccion"].split(":")[0])
    b.metric("Motor", info["version"])
    c.metric("Protocolo", info["protocolo"])
    st.caption(f"URI: {cfg.uri}  |  Base de datos: {cfg.base_datos}  |  Usuario: {cfg.usuario}")
    if cfg.es_local:
        st.warning("La URI apunta a localhost. Para la evaluación debe apuntar a AuraDB.")

    resumen = grafo.resumen()
    if not resumen["nodos"]:
        st.info("La base está vacía. Corre `python scripts/seed.py` para cargar los datos iniciales.")
        return

    st.subheader("Nodos por etiqueta")
    columnas = st.columns(len(resumen["nodos"]))
    for columna, (etiqueta, total) in zip(columnas, resumen["nodos"].items()):
        columna.metric(etiqueta, total)

    st.subheader("Relaciones por tipo")
    columnas = st.columns(len(resumen["relaciones"]))
    for columna, (tipo, total) in zip(columnas, resumen["relaciones"].items()):
        columna.metric(tipo, total)

    izquierda, derecha = st.columns(2)
    with izquierda:
        st.subheader("Productos más vendidos")
        tabla(recomendaciones.mas_vendidos(8), precio=DINERO)
        ver_cypher(recomendaciones.MAS_VENDIDOS)
    with derecha:
        st.subheader("Ingresos por categoría")
        ventas = pd.DataFrame(grafo.ventas_por_categoria())
        st.bar_chart(ventas, x="categoria", y="ingresos", x_label="", y_label="MXN")
        ver_cypher(grafo.VENTAS_POR_CATEGORIA)

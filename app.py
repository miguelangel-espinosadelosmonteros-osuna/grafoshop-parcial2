"""GrafoShop: tienda en línea con recomendaciones sobre Neo4j AuraDB.

Punto de entrada de la interfaz. Ejecutar con:  streamlit run app.py
"""
import streamlit as st
from neo4j.exceptions import AuthError, ServiceUnavailable

from src import db
from src.config import ConfiguracionIncompleta
from vistas import carrito, catalogo, clientes, explorador, inicio, recomendaciones

PANTALLAS = {
    "Inicio": inicio.mostrar,
    "Catálogo": catalogo.mostrar,
    "Clientes": clientes.mostrar,
    "Carrito y compra": carrito.mostrar,
    "Recomendaciones": recomendaciones.mostrar,
    "Explorador del grafo": explorador.mostrar,
}


def conectar() -> None:
    """Abre la conexión con AuraDB o detiene la app con un mensaje claro."""
    try:
        db.obtener_driver()
    except ConfiguracionIncompleta as error:
        st.error(str(error))
        st.stop()
    except AuthError:
        st.error("Neo4j rechazó el usuario o la contraseña. Revisa tu archivo .env.")
        st.stop()
    except (ServiceUnavailable, ValueError) as error:
        st.error("No se pudo conectar con Neo4j AuraDB. Revisa la URI y que la instancia "
                 f"esté encendida (no pausada). Detalle: {error}")
        st.stop()


def main() -> None:
    st.set_page_config(page_title="GrafoShop", layout="wide")
    conectar()
    st.sidebar.title("GrafoShop")
    pantalla = st.sidebar.radio("Menú", list(PANTALLAS), label_visibility="collapsed")
    st.sidebar.caption("Neo4j AuraDB + Python + Streamlit")
    PANTALLAS[pantalla]()


main()

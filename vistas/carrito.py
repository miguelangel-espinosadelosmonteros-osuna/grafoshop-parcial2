"""Pantalla Carrito: agregar productos, cerrar la compra y ver el historial."""
import streamlit as st

from src import carrito, recomendaciones
from src.errores import ErrorDeNegocio
from vistas.comun import (DINERO, avisar, elegir_cliente, elegir_producto, mostrar_aviso,
                          tabla, ver_cypher)


def mostrar() -> None:
    st.title("Carrito y compra")
    mostrar_aviso()

    cliente_id = elegir_cliente(clave="carrito_cliente")
    if cliente_id is None:
        return

    st.subheader("Agregar al carrito")
    a, b, c = st.columns([4, 1, 1], vertical_alignment="bottom")
    with a:
        producto_id = elegir_producto(clave="carrito_producto")
    cantidad = b.number_input("Cantidad", min_value=1, value=1, step=1)
    if c.button("Agregar", type="primary", disabled=producto_id is None):
        try:
            carrito.agregar(cliente_id, producto_id, cantidad)
            avisar("Producto agregado al carrito.")
            st.rerun()
        except ErrorDeNegocio as error:
            st.error(str(error))
    ver_cypher(carrito.AGREGAR, "Ver consulta Cypher (agregar al carrito)")

    st.subheader("Carrito actual")
    lineas = carrito.ver(cliente_id)
    if not lineas:
        st.info("El carrito está vacío.")
    else:
        tabla(lineas, precio=DINERO, subtotal=DINERO)
        total = sum(linea["subtotal"] for linea in lineas)
        st.metric("Total", f"${total:,.2f}")

        nombres = {l["id"]: l["producto"] for l in lineas}
        a, b, c = st.columns([4, 1, 1], vertical_alignment="bottom")
        elegido = a.selectbox("Producto del carrito", list(nombres), format_func=nombres.get)
        nueva = b.number_input("Nueva cantidad", min_value=0, step=1,
                               value=next(l["cantidad"] for l in lineas if l["id"] == elegido),
                               key=f"cant_{elegido}", help="Con 0 se quita del carrito")
        if c.button("Actualizar"):
            carrito.cambiar_cantidad(cliente_id, elegido, nueva)
            avisar("Carrito actualizado.")
            st.rerun()

        a, b = st.columns(2)
        if a.button("Comprar", type="primary", width="stretch"):
            try:
                pedido = carrito.comprar(cliente_id)
                avisar(f"Compra realizada. Pedido {pedido['pedido_id']} por "
                       f"${pedido['total']:,.2f}.")
                st.rerun()
            except ErrorDeNegocio as error:
                st.error(f"{error} No se guardó ningún cambio.")
        if b.button("Vaciar carrito", width="stretch"):
            carrito.vaciar(cliente_id)
            avisar("Carrito vacío.")
            st.rerun()
        ver_cypher(carrito.CREAR_PEDIDO, "Ver consulta Cypher (compra en una transacción)")

        sugerencias = recomendaciones.segun_carrito(cliente_id)
        if sugerencias:
            st.subheader("Se suele comprar junto con lo que llevas")
            tabla(sugerencias, precio=DINERO)
            ver_cypher(recomendaciones.SEGUN_CARRITO)

    st.subheader("Pedidos anteriores")
    pedidos = carrito.historial(cliente_id)
    if pedidos:
        tabla(pedidos, total=DINERO)
    else:
        st.caption("Este cliente todavía no tiene pedidos.")

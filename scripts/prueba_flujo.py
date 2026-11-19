"""Prueba de punta a punta contra la base real (requiere haber corrido seed.py).

Recorre el flujo completo: CRUD de producto y cliente, carrito, compra,
recomendaciones y caminos. Todo lo que crea lo borra al final.

Uso: python scripts/prueba_flujo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import carrito, clientes, db, grafo, productos, recomendaciones  # noqa: E402
from src.errores import ErrorDeNegocio  # noqa: E402


def paso(texto: str) -> None:
    print(f"  OK  {texto}")


def espera_error(funcion, *args) -> str:
    try:
        funcion(*args)
    except ErrorDeNegocio as error:
        return str(error)
    raise AssertionError(f"{funcion.__name__} debió rechazar la operación")


def main() -> None:
    print("Prueba de flujo de GrafoShop")
    cliente_id = producto_id = None
    try:
        # CRUD de producto
        producto_id = productos.crear("Producto de prueba", "Pruebas", 100.0, 2)
        assert productos.obtener(producto_id)["stock"] == 2
        productos.actualizar(producto_id, "Producto de prueba", "Pruebas", 150.0, 2)
        assert productos.obtener(producto_id)["precio"] == 150.0
        assert any(p["id"] == producto_id for p in productos.listar(texto="prueba"))
        espera_error(productos.crear, "", "Pruebas", 10.0, 1)
        paso("crear, leer, actualizar y validar producto")

        # CRUD de cliente
        cliente_id = clientes.crear("Cliente de prueba", "prueba@correo.mx", "Mérida")
        clientes.actualizar(cliente_id, "Cliente de prueba", "prueba@correo.mx", "Progreso")
        fila = next(c for c in clientes.listar() if c["id"] == cliente_id)
        assert fila["ciudad"] == "Progreso"
        espera_error(clientes.crear, "Otro", "prueba@correo.mx", "Mérida")
        paso("crear, leer, actualizar cliente y correo único")

        # Carrito
        carrito.agregar(cliente_id, producto_id, 1)
        assert carrito.agregar(cliente_id, producto_id, 2) == 3
        assert carrito.ver(cliente_id)[0]["subtotal"] == 450.0
        paso("agregar al carrito y sumar cantidades")

        # Compra sin stock suficiente: debe hacer rollback completo
        mensaje = espera_error(carrito.comprar, cliente_id)
        assert "stock" in mensaje
        assert productos.obtener(producto_id)["stock"] == 2
        assert len(carrito.ver(cliente_id)) == 1
        assert carrito.historial(cliente_id) == []
        paso("compra rechazada por stock y rollback de la transacción")

        # Compra correcta
        carrito.cambiar_cantidad(cliente_id, producto_id, 2)
        carrito.agregar(cliente_id, "P003", 1)
        pedido = carrito.comprar(cliente_id)
        assert pedido["productos"] == 2 and pedido["total"] == 749.0
        assert productos.obtener(producto_id)["stock"] == 0
        assert carrito.ver(cliente_id) == []
        assert len(carrito.historial(cliente_id)) == 1
        espera_error(carrito.comprar, cliente_id)
        espera_error(productos.eliminar, producto_id)
        paso(f"compra {pedido['pedido_id']}: pedido creado, stock descontado, carrito vacío")

        # Recomendaciones y caminos
        assert recomendaciones.por_clientes_similares("C001")
        assert recomendaciones.comprados_juntos("P001")
        assert recomendaciones.clientes_similares("C001")
        assert recomendaciones.mas_vendidos()
        camino = grafo.camino_mas_corto("C001", "C012")
        assert camino and camino["saltos"] >= 4
        assert grafo.camino_mas_corto("C001", "C013") is None
        assert grafo.vecindad_cliente("C001")["nodos"]
        paso(f"recomendaciones y camino más corto ({camino['saltos']} saltos)")
    finally:
        # Limpieza: devuelve el stock del mouse y borra los datos de prueba
        if cliente_id:
            vendidos = db.leer(
                "MATCH (:Cliente {id: $id})-[:REALIZO]->(:Pedido)-[con:CONTIENE]->"
                "(:Producto {id: 'P003'}) RETURN sum(con.cantidad) AS total", id=cliente_id,
            )[0]["total"]
            db.escribir("MATCH (p:Producto {id: 'P003'}) SET p.stock = p.stock + $n", n=vendidos)
            clientes.eliminar(cliente_id)
        if producto_id:
            productos.eliminar(producto_id)
        db.cerrar()
    print("Todo funcionó y se borraron los datos de prueba.")


if __name__ == "__main__":
    main()

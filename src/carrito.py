"""Carrito de compras y cierre de la compra (pedido).

El carrito no es una tabla aparte: es la relación TIENE_EN_CARRITO entre un
cliente y un producto, y la cantidad es una propiedad de esa relación.
"""
from src import db
from src.errores import ErrorDeNegocio

AGREGAR = """
MATCH (c:Cliente {id: $cliente_id}), (p:Producto {id: $producto_id})
MERGE (c)-[r:TIENE_EN_CARRITO]->(p)
ON CREATE SET r.cantidad = $cantidad, r.agregado = datetime()
ON MATCH SET r.cantidad = r.cantidad + $cantidad
RETURN r.cantidad AS cantidad, p.stock AS stock
"""

CAMBIAR_CANTIDAD = """
MATCH (:Cliente {id: $cliente_id})-[r:TIENE_EN_CARRITO]->(:Producto {id: $producto_id})
SET r.cantidad = $cantidad
RETURN r.cantidad AS cantidad
"""

QUITAR = """
MATCH (:Cliente {id: $cliente_id})-[r:TIENE_EN_CARRITO]->(:Producto {id: $producto_id})
DELETE r
"""

VACIAR = """
MATCH (:Cliente {id: $cliente_id})-[r:TIENE_EN_CARRITO]->(:Producto)
DELETE r
"""

VER = """
MATCH (:Cliente {id: $cliente_id})-[r:TIENE_EN_CARRITO]->(p:Producto)
RETURN p.id AS id, p.nombre AS producto, p.precio AS precio,
       r.cantidad AS cantidad, p.precio * r.cantidad AS subtotal, p.stock AS stock
ORDER BY r.agregado
"""

# Convierte el carrito en un pedido: crea el nodo Pedido, pasa cada producto
# del carrito a una relación CONTIENE, descuenta el stock y vacía el carrito.
CREAR_PEDIDO = """
MATCH (c:Cliente {id: $cliente_id})-[r:TIENE_EN_CARRITO]->(p:Producto)
WITH c, collect({producto: p, linea: r}) AS lineas,
     sum(p.precio * r.cantidad) AS total
CREATE (c)-[:REALIZO]->(pe:Pedido {
    id: 'PED-' + toUpper(left(randomUUID(), 8)),
    fecha: datetime(),
    total: total
})
WITH pe, lineas
UNWIND lineas AS item
WITH pe, item.producto AS p, item.linea AS r
CREATE (pe)-[:CONTIENE {cantidad: r.cantidad, precio_unitario: p.precio}]->(p)
SET p.stock = p.stock - r.cantidad
DELETE r
RETURN pe.id AS pedido_id, pe.total AS total, count(p) AS productos
"""

# Se ejecuta dentro de la misma transacción, después de descontar el stock.
SIN_STOCK = """
MATCH (:Pedido {id: $pedido_id})-[:CONTIENE]->(p:Producto)
WHERE p.stock < 0
RETURN collect(p.nombre) AS productos
"""

HISTORIAL = """
MATCH (:Cliente {id: $cliente_id})-[:REALIZO]->(pe:Pedido)-[con:CONTIENE]->(p:Producto)
WITH pe, collect(toString(con.cantidad) + ' x ' + p.nombre) AS productos
RETURN pe.id AS pedido, toString(date(pe.fecha)) AS fecha,
       pe.total AS total, productos
ORDER BY pe.fecha DESC
"""


def agregar(cliente_id: str, producto_id: str, cantidad: int = 1) -> int:
    """Agrega un producto al carrito; si ya estaba, suma la cantidad."""
    if cantidad < 1:
        raise ErrorDeNegocio("La cantidad debe ser al menos 1.")
    filas = db.escribir(AGREGAR, cliente_id=cliente_id, producto_id=producto_id,
                        cantidad=int(cantidad))
    if not filas:
        raise ErrorDeNegocio("El cliente o el producto no existe.")
    return filas[0]["cantidad"]


def cambiar_cantidad(cliente_id: str, producto_id: str, cantidad: int) -> None:
    """Cambia la cantidad de un producto; con 0 lo quita del carrito."""
    if cantidad <= 0:
        quitar(cliente_id, producto_id)
        return
    filas = db.escribir(CAMBIAR_CANTIDAD, cliente_id=cliente_id,
                        producto_id=producto_id, cantidad=int(cantidad))
    if not filas:
        raise ErrorDeNegocio("Ese producto no está en el carrito.")


def quitar(cliente_id: str, producto_id: str) -> None:
    db.escribir(QUITAR, cliente_id=cliente_id, producto_id=producto_id)


def vaciar(cliente_id: str) -> None:
    db.escribir(VACIAR, cliente_id=cliente_id)


def ver(cliente_id: str) -> list[dict]:
    return db.leer(VER, cliente_id=cliente_id)


def _transaccion_compra(tx, cliente_id: str) -> dict:
    """Pasos de la compra. Todos ocurren en la misma transacción."""
    registro = tx.run(CREAR_PEDIDO, cliente_id=cliente_id).single()
    if registro is None:
        raise ErrorDeNegocio("El carrito está vacío.")
    pedido = registro.data()
    agotados = tx.run(SIN_STOCK, pedido_id=pedido["pedido_id"]).single()["productos"]
    if agotados:
        # Al lanzar la excepción el driver hace rollback: no queda pedido,
        # el stock vuelve a su valor y el carrito sigue como estaba.
        raise ErrorDeNegocio("No hay stock suficiente de: " + ", ".join(agotados) + ".")
    return pedido


def comprar(cliente_id: str) -> dict:
    """Cierra la compra del carrito. Regresa el id del pedido, el total y el número de productos."""
    return db.transaccion_de_escritura(_transaccion_compra, cliente_id)


def historial(cliente_id: str) -> list[dict]:
    """Pedidos anteriores del cliente, del más reciente al más antiguo."""
    return db.leer(HISTORIAL, cliente_id=cliente_id)

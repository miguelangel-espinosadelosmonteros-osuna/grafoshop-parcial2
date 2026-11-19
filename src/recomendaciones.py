"""Consultas de recomendación.

Todas son recorridos (traversals) del grafo: se parte de un nodo y se siguen
las relaciones REALIZO y CONTIENE hasta llegar a otros clientes o productos.
"""
from src import db

# "Clientes que compraron lo mismo que tú también compraron..."
# Recorrido: yo -> mis pedidos -> mis productos <- pedidos de otros <- otros
#            y de esos otros -> sus pedidos -> productos que yo no tengo.
POR_CLIENTES_SIMILARES = """
MATCH (yo:Cliente {id: $cliente_id})-[:REALIZO]->(:Pedido)-[:CONTIENE]->(p:Producto)
      <-[:CONTIENE]-(:Pedido)<-[:REALIZO]-(otro:Cliente)
WHERE otro <> yo
WITH yo, otro, count(DISTINCT p) AS en_comun
MATCH (otro)-[:REALIZO]->(:Pedido)-[:CONTIENE]->(rec:Producto)
WHERE rec.stock > 0
  AND NOT EXISTS { (yo)-[:REALIZO]->(:Pedido)-[:CONTIENE]->(rec) }
WITH DISTINCT otro, en_comun, rec
RETURN rec.id AS id, rec.nombre AS producto, rec.precio AS precio,
       sum(en_comun) AS puntaje, count(otro) AS clientes_similares
ORDER BY puntaje DESC, clientes_similares DESC, producto
LIMIT $limite
"""

# Productos que salen en el mismo pedido que el producto dado.
COMPRADOS_JUNTOS = """
MATCH (p:Producto {id: $producto_id})<-[:CONTIENE]-(pe:Pedido)-[:CONTIENE]->(otro:Producto)
RETURN otro.id AS id, otro.nombre AS producto, otro.precio AS precio,
       count(DISTINCT pe) AS pedidos_juntos
ORDER BY pedidos_juntos DESC, producto
LIMIT $limite
"""

# Sugerencias a partir de lo que el cliente tiene ahora en el carrito.
SEGUN_CARRITO = """
MATCH (c:Cliente {id: $cliente_id})-[:TIENE_EN_CARRITO]->(p:Producto)
      <-[:CONTIENE]-(pe:Pedido)-[:CONTIENE]->(rec:Producto)
WHERE rec.stock > 0
  AND NOT EXISTS { (c)-[:TIENE_EN_CARRITO]->(rec) }
RETURN rec.id AS id, rec.nombre AS producto, rec.precio AS precio,
       count(DISTINCT pe) AS pedidos_juntos,
       collect(DISTINCT p.nombre) AS porque
ORDER BY pedidos_juntos DESC, producto
LIMIT $limite
"""

# Vecindad del cliente: otros clientes con productos en común.
# Similitud de Jaccard = productos en común / productos distintos entre los dos.
CLIENTES_SIMILARES = """
MATCH (yo:Cliente {id: $cliente_id})-[:REALIZO]->(:Pedido)-[:CONTIENE]->(p:Producto)
WITH yo, collect(DISTINCT p) AS mios
MATCH (otro:Cliente)-[:REALIZO]->(:Pedido)-[:CONTIENE]->(q:Producto)
WHERE otro <> yo
WITH otro, mios, collect(DISTINCT q) AS suyos
WITH otro, mios, suyos, [x IN mios WHERE x IN suyos] AS comunes
WHERE size(comunes) > 0
RETURN otro.id AS id, otro.nombre AS cliente, size(comunes) AS en_comun,
       round(1.0 * size(comunes) / (size(mios) + size(suyos) - size(comunes)), 2) AS jaccard,
       [x IN comunes | x.nombre] AS productos
ORDER BY jaccard DESC, cliente
LIMIT $limite
"""

# Respaldo para clientes nuevos sin compras (problema de "arranque en frío").
MAS_VENDIDOS = """
MATCH (:Pedido)-[con:CONTIENE]->(p:Producto)-[:PERTENECE_A]->(cat:Categoria)
RETURN p.id AS id, p.nombre AS producto, cat.nombre AS categoria,
       p.precio AS precio, sum(con.cantidad) AS unidades
ORDER BY unidades DESC, producto
LIMIT $limite
"""


def por_clientes_similares(cliente_id: str, limite: int = 5) -> list[dict]:
    """Filtrado colaborativo: productos que compraron clientes parecidos a este."""
    return db.leer(POR_CLIENTES_SIMILARES, cliente_id=cliente_id, limite=limite)


def comprados_juntos(producto_id: str, limite: int = 5) -> list[dict]:
    """Productos que suelen comprarse en el mismo pedido que el producto dado."""
    return db.leer(COMPRADOS_JUNTOS, producto_id=producto_id, limite=limite)


def segun_carrito(cliente_id: str, limite: int = 4) -> list[dict]:
    """Productos que combinan con lo que el cliente ya tiene en el carrito."""
    return db.leer(SEGUN_CARRITO, cliente_id=cliente_id, limite=limite)


def clientes_similares(cliente_id: str, limite: int = 5) -> list[dict]:
    """Clientes con gustos parecidos, ordenados por similitud de Jaccard."""
    return db.leer(CLIENTES_SIMILARES, cliente_id=cliente_id, limite=limite)


def mas_vendidos(limite: int = 5) -> list[dict]:
    """Productos con más unidades vendidas en toda la tienda."""
    return db.leer(MAS_VENDIDOS, limite=limite)

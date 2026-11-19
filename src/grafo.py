"""Consultas que exploran la estructura del grafo: caminos, vecindades y totales."""
from src import db
from src.errores import ErrorDeNegocio

# Camino más corto entre dos clientes pasando por pedidos y productos.
# Las relaciones se recorren sin dirección y con un máximo de 8 saltos.
CAMINO_MAS_CORTO = """
MATCH (a:Cliente {id: $origen}), (b:Cliente {id: $destino})
MATCH ruta = shortestPath((a)-[:REALIZO|CONTIENE*..8]-(b))
RETURN ruta
"""

# Vecindad de un cliente: todo lo que está a 1 o 2 saltos de él
# (su carrito, sus pedidos y los productos de esos pedidos).
VECINDAD_CLIENTE = """
MATCH ruta = (:Cliente {id: $cliente_id})-[:REALIZO|CONTIENE|TIENE_EN_CARRITO*1..2]->()
RETURN ruta
"""

CONTAR_NODOS = """
MATCH (n)
RETURN labels(n)[0] AS etiqueta, count(*) AS total
ORDER BY etiqueta
"""

CONTAR_RELACIONES = """
MATCH ()-[r]->()
RETURN type(r) AS tipo, count(*) AS total
ORDER BY tipo
"""

VENTAS_POR_CATEGORIA = """
MATCH (:Pedido)-[con:CONTIENE]->(:Producto)-[:PERTENECE_A]->(cat:Categoria)
RETURN cat.nombre AS categoria,
       sum(con.cantidad) AS unidades,
       sum(con.cantidad * con.precio_unitario) AS ingresos
ORDER BY ingresos DESC
"""


def _nombre_de(nodo) -> str:
    """Texto corto para mostrar un nodo en el diagrama."""
    return nodo.get("nombre") or nodo.get("id") or "?"


def rutas_a_grafo(rutas: list) -> dict:
    """Convierte objetos Path del driver en listas simples de nodos y aristas.

    Así la interfaz puede dibujar el resultado sin conocer el driver.
    """
    nodos, aristas = {}, {}
    for ruta in rutas:
        for nodo in ruta.nodes:
            nodos[nodo.element_id] = {
                "clave": nodo.element_id,
                "etiqueta": next(iter(nodo.labels)),
                "nombre": _nombre_de(nodo),
            }
        for rel in ruta.relationships:
            aristas[rel.element_id] = {
                "origen": rel.start_node.element_id,
                "destino": rel.end_node.element_id,
                "tipo": rel.type,
                "cantidad": rel.get("cantidad"),
            }
    return {"nodos": list(nodos.values()), "aristas": list(aristas.values())}


def camino_mas_corto(origen: str, destino: str) -> dict | None:
    """Camino más corto entre dos clientes. Regresa None si no están conectados."""
    if origen == destino:
        raise ErrorDeNegocio("Elige dos clientes distintos.")
    rutas = db.leer_rutas(CAMINO_MAS_CORTO, origen=origen, destino=destino)
    if not rutas:
        return None
    ruta = rutas[0]
    grafo = rutas_a_grafo([ruta])
    grafo["saltos"] = len(ruta.relationships)
    grafo["pasos"] = [f"{next(iter(n.labels))}: {_nombre_de(n)}" for n in ruta.nodes]
    return grafo


def vecindad_cliente(cliente_id: str) -> dict:
    """Subgrafo alrededor de un cliente (carrito, pedidos y productos)."""
    return rutas_a_grafo(db.leer_rutas(VECINDAD_CLIENTE, cliente_id=cliente_id))


def resumen() -> dict:
    """Totales de nodos por etiqueta y de relaciones por tipo."""
    return {
        "nodos": {f["etiqueta"]: f["total"] for f in db.leer(CONTAR_NODOS)},
        "relaciones": {f["tipo"]: f["total"] for f in db.leer(CONTAR_RELACIONES)},
    }


def ventas_por_categoria() -> list[dict]:
    return db.leer(VENTAS_POR_CATEGORIA)

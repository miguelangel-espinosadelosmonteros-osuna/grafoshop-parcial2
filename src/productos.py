"""CRUD de productos y categorías."""
import uuid

from src import db
from src.errores import ErrorDeNegocio

CREAR = """
MERGE (cat:Categoria {nombre: $categoria})
CREATE (p:Producto {id: $id, nombre: $nombre, precio: $precio,
                    stock: $stock, creado: datetime()})
CREATE (p)-[:PERTENECE_A]->(cat)
RETURN p.id AS id
"""

LISTAR = """
MATCH (p:Producto)-[:PERTENECE_A]->(cat:Categoria)
WHERE ($categoria IS NULL OR cat.nombre = $categoria)
  AND ($texto IS NULL OR toLower(p.nombre) CONTAINS toLower($texto))
RETURN p.id AS id, p.nombre AS nombre, cat.nombre AS categoria,
       p.precio AS precio, p.stock AS stock
ORDER BY p.nombre
"""

OBTENER = """
MATCH (p:Producto {id: $id})-[:PERTENECE_A]->(cat:Categoria)
RETURN p.id AS id, p.nombre AS nombre, cat.nombre AS categoria,
       p.precio AS precio, p.stock AS stock
"""

ACTUALIZAR = """
MATCH (p:Producto {id: $id})
SET p.nombre = $nombre, p.precio = $precio, p.stock = $stock,
    p.actualizado = datetime()
WITH p
OPTIONAL MATCH (p)-[rel:PERTENECE_A]->(anterior:Categoria)
WHERE anterior.nombre <> $categoria
DELETE rel
WITH DISTINCT p
MERGE (cat:Categoria {nombre: $categoria})
MERGE (p)-[:PERTENECE_A]->(cat)
RETURN p.id AS id
"""

ELIMINAR = """
MATCH (p:Producto {id: $id})
WHERE NOT EXISTS { (:Pedido)-[:CONTIENE]->(p) }
DETACH DELETE p
RETURN count(*) AS eliminados
"""

LISTAR_CATEGORIAS = """
MATCH (cat:Categoria)
RETURN cat.nombre AS nombre
ORDER BY nombre
"""

LIMPIAR_CATEGORIAS_VACIAS = """
MATCH (cat:Categoria)
WHERE NOT EXISTS { (:Producto)-[:PERTENECE_A]->(cat) }
DELETE cat
"""


def _validar(nombre: str, categoria: str, precio: float, stock: int) -> None:
    if not nombre.strip():
        raise ErrorDeNegocio("El nombre del producto no puede estar vacío.")
    if not categoria.strip():
        raise ErrorDeNegocio("La categoría no puede estar vacía.")
    if precio <= 0:
        raise ErrorDeNegocio("El precio debe ser mayor que cero.")
    if stock < 0:
        raise ErrorDeNegocio("El stock no puede ser negativo.")


def crear(nombre: str, categoria: str, precio: float, stock: int) -> str:
    """Crea un producto y lo conecta con su categoría. Regresa el id nuevo."""
    _validar(nombre, categoria, precio, stock)
    nuevo_id = "P-" + uuid.uuid4().hex[:6].upper()
    db.escribir(CREAR, id=nuevo_id, nombre=nombre.strip(), categoria=categoria.strip(),
                precio=float(precio), stock=int(stock))
    return nuevo_id


def listar(categoria: str | None = None, texto: str | None = None) -> list[dict]:
    """Lista productos, con filtro opcional por categoría y por texto en el nombre."""
    return db.leer(LISTAR, categoria=categoria or None, texto=texto or None)


def obtener(producto_id: str) -> dict | None:
    filas = db.leer(OBTENER, id=producto_id)
    return filas[0] if filas else None


def actualizar(producto_id: str, nombre: str, categoria: str, precio: float, stock: int) -> None:
    """Cambia las propiedades del producto y, si hace falta, su categoría."""
    _validar(nombre, categoria, precio, stock)
    filas = db.escribir(ACTUALIZAR, id=producto_id, nombre=nombre.strip(),
                        categoria=categoria.strip(), precio=float(precio), stock=int(stock))
    if not filas:
        raise ErrorDeNegocio(f"No existe el producto {producto_id}.")
    db.escribir(LIMPIAR_CATEGORIAS_VACIAS)


def eliminar(producto_id: str) -> None:
    """Elimina un producto solo si no aparece en ningún pedido.

    Si ya se vendió, borrarlo rompería el historial de compras, así que se rechaza.
    """
    if obtener(producto_id) is None:
        raise ErrorDeNegocio(f"No existe el producto {producto_id}.")
    eliminados = db.escribir(ELIMINAR, id=producto_id)[0]["eliminados"]
    if eliminados == 0:
        raise ErrorDeNegocio(
            "No se puede eliminar: el producto aparece en pedidos anteriores. "
            "Si ya no se vende, pon su stock en 0."
        )
    db.escribir(LIMPIAR_CATEGORIAS_VACIAS)


def categorias() -> list[str]:
    return [fila["nombre"] for fila in db.leer(LISTAR_CATEGORIAS)]

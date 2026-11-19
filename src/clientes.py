"""CRUD de clientes."""
import uuid

from neo4j.exceptions import ConstraintError

from src import db
from src.errores import ErrorDeNegocio

CREAR = """
CREATE (c:Cliente {id: $id, nombre: $nombre, email: $email,
                   ciudad: $ciudad, creado: datetime()})
RETURN c.id AS id
"""

LISTAR = """
MATCH (c:Cliente)
RETURN c.id AS id, c.nombre AS nombre, c.email AS email, c.ciudad AS ciudad,
       COUNT { (c)-[:REALIZO]->(:Pedido) } AS pedidos,
       COUNT { (c)-[:TIENE_EN_CARRITO]->(:Producto) } AS en_carrito
ORDER BY c.nombre
"""

ACTUALIZAR = """
MATCH (c:Cliente {id: $id})
SET c.nombre = $nombre, c.email = $email, c.ciudad = $ciudad,
    c.actualizado = datetime()
RETURN c.id AS id
"""

ELIMINAR = """
MATCH (c:Cliente {id: $id})
OPTIONAL MATCH (c)-[:REALIZO]->(pe:Pedido)
DETACH DELETE pe, c
RETURN count(DISTINCT c) AS eliminados
"""


def _validar(nombre: str, email: str, ciudad: str) -> None:
    if not nombre.strip():
        raise ErrorDeNegocio("El nombre del cliente no puede estar vacío.")
    if "@" not in email or "." not in email.split("@")[-1]:
        raise ErrorDeNegocio("El correo no tiene un formato válido.")
    if not ciudad.strip():
        raise ErrorDeNegocio("La ciudad no puede estar vacía.")


def crear(nombre: str, email: str, ciudad: str) -> str:
    """Crea un cliente. El correo es único gracias a un constraint en la base."""
    _validar(nombre, email, ciudad)
    nuevo_id = "C-" + uuid.uuid4().hex[:6].upper()
    try:
        db.escribir(CREAR, id=nuevo_id, nombre=nombre.strip(),
                    email=email.strip().lower(), ciudad=ciudad.strip())
    except ConstraintError:
        raise ErrorDeNegocio(f"Ya existe un cliente con el correo {email}.") from None
    return nuevo_id


def listar() -> list[dict]:
    """Lista los clientes con cuántos pedidos y productos en carrito tiene cada uno."""
    return db.leer(LISTAR)


def actualizar(cliente_id: str, nombre: str, email: str, ciudad: str) -> None:
    _validar(nombre, email, ciudad)
    try:
        filas = db.escribir(ACTUALIZAR, id=cliente_id, nombre=nombre.strip(),
                            email=email.strip().lower(), ciudad=ciudad.strip())
    except ConstraintError:
        raise ErrorDeNegocio(f"Ya existe otro cliente con el correo {email}.") from None
    if not filas:
        raise ErrorDeNegocio(f"No existe el cliente {cliente_id}.")


def eliminar(cliente_id: str) -> None:
    """Elimina al cliente junto con sus pedidos y su carrito.

    En un grafo no hay ON DELETE CASCADE: hay que indicar qué nodos se borran.
    DETACH DELETE quita también todas las relaciones de esos nodos.
    """
    eliminados = db.escribir(ELIMINAR, id=cliente_id)[0]["eliminados"]
    if eliminados == 0:
        raise ErrorDeNegocio(f"No existe el cliente {cliente_id}.")

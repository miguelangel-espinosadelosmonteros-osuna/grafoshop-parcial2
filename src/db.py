"""Capa de conexión con Neo4j AuraDB usando el driver oficial de Python.

Se crea un solo objeto Driver para toda la aplicación. El driver mantiene un
pool de conexiones, así que es seguro reutilizarlo en todas las consultas.
"""
from neo4j import Driver, GraphDatabase, RoutingControl

from src.config import cargar_configuracion

_driver: Driver | None = None


def obtener_driver() -> Driver:
    """Regresa el driver (lo crea y prueba la conexión la primera vez)."""
    global _driver
    if _driver is None:
        cfg = cargar_configuracion()
        driver = GraphDatabase.driver(cfg.uri, auth=(cfg.usuario, cfg.contrasena))
        driver.verify_connectivity()
        _driver = driver
    return _driver


def cerrar() -> None:
    """Cierra el driver y libera las conexiones del pool."""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


def leer(consulta: str, **parametros) -> list[dict]:
    """Ejecuta una consulta de lectura y regresa las filas como diccionarios."""
    registros, _, _ = obtener_driver().execute_query(
        consulta,
        parameters_=parametros,
        database_=cargar_configuracion().base_datos,
        routing_=RoutingControl.READ,
    )
    return [registro.data() for registro in registros]


def escribir(consulta: str, **parametros) -> list[dict]:
    """Ejecuta una consulta de escritura dentro de una transacción administrada.

    Si algo falla, el driver hace rollback; si es un error transitorio, reintenta.
    """
    registros, _, _ = obtener_driver().execute_query(
        consulta,
        parameters_=parametros,
        database_=cargar_configuracion().base_datos,
        routing_=RoutingControl.WRITE,
    )
    return [registro.data() for registro in registros]


def leer_rutas(consulta: str, **parametros) -> list:
    """Ejecuta una lectura que regresa rutas (Path) y las entrega sin convertir."""
    registros, _, _ = obtener_driver().execute_query(
        consulta,
        parameters_=parametros,
        database_=cargar_configuracion().base_datos,
        routing_=RoutingControl.READ,
    )
    return [registro["ruta"] for registro in registros]


def transaccion_de_escritura(funcion, *args):
    """Ejecuta varias consultas en UNA sola transacción (todo o nada).

    `funcion` recibe la transacción como primer argumento. Si lanza una
    excepción, no se guarda ningún cambio.
    """
    with obtener_driver().session(database=cargar_configuracion().base_datos) as sesion:
        return sesion.execute_write(funcion, *args)


def info_servidor() -> dict:
    """Datos del servidor al que está conectada la aplicación."""
    info = obtener_driver().get_server_info()
    return {
        "direccion": f"{info.address[0]}:{info.address[1]}",
        "version": info.agent,
        "protocolo": f"Bolt {info.protocol_version[0]}.{info.protocol_version[1]}",
    }

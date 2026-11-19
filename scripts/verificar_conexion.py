"""Prueba rápida de la conexión con Neo4j AuraDB.

Uso: python scripts/verificar_conexion.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import db  # noqa: E402
from src.config import cargar_configuracion  # noqa: E402


def main() -> None:
    cfg = cargar_configuracion()
    print(f"URI: {cfg.uri}")
    if cfg.es_local:
        print("AVISO: la URI apunta a localhost, no a un servicio en la nube.")
    info = db.info_servidor()
    print(f"Servidor: {info['direccion']}")
    print(f"Versión: {info['version']} ({info['protocolo']})")
    nodos = db.leer("MATCH (n) RETURN count(n) AS total")[0]["total"]
    print(f"Nodos en la base: {nodos}")
    print("Conexión correcta.")
    db.cerrar()


if __name__ == "__main__":
    main()

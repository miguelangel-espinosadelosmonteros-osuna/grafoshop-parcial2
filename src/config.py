"""Configuración de la aplicación.

Las credenciales de Neo4j AuraDB se leen de variables de entorno (archivo .env).
Nunca se escriben en el código ni se suben al repositorio.
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

VARIABLES_OBLIGATORIAS = ("NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD")


class ConfiguracionIncompleta(RuntimeError):
    """Falta alguna variable de entorno necesaria para conectarse."""


@dataclass(frozen=True)
class Configuracion:
    uri: str
    usuario: str
    contrasena: str
    base_datos: str

    @property
    def es_local(self) -> bool:
        """True si la URI apunta a la propia computadora y no a la nube."""
        return "localhost" in self.uri or "127.0.0.1" in self.uri


def cargar_configuracion() -> Configuracion:
    faltantes = [v for v in VARIABLES_OBLIGATORIAS if not os.getenv(v)]
    if faltantes:
        raise ConfiguracionIncompleta(
            "Faltan variables de entorno: " + ", ".join(faltantes)
            + ". Copia .env.example como .env y llena los datos de tu instancia de AuraDB."
        )
    return Configuracion(
        uri=os.environ["NEO4J_URI"],
        usuario=os.environ["NEO4J_USERNAME"],
        contrasena=os.environ["NEO4J_PASSWORD"],
        base_datos=os.getenv("NEO4J_DATABASE", "neo4j"),
    )

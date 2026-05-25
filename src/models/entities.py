"""
entities.py
-----------
Define las entidades del dominio del problema de horarios escolares.
Cada clase representa un elemento real de la institución educativa.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Materia:
    """
    Representa una materia

    Atributos:
        id          : Identificador único (ej. "MAT01")
        nombre      : Nombre legible (ej. "Matemáticas")
        horas_semana: Número de clases que necesita por semana
    """
    id: str
    nombre: str
    horas_semana: int


@dataclass
class Profesor:
    """
    Representa a un profesor

    Atributos:
        id            : Identificador único (ej. "PROF01")
        nombre        : Nombre completo
        materias_ids  : Lista de IDs de materias que puede impartir
        disponibilidad: Lista de slots disponibles, cada uno es [dia, hora]
                        ej. [["Lunes", 7], ["Martes", 9], ...]
    """
    id: str
    nombre: str
    materias_ids: List[str]
    disponibilidad: List[List]  # Lista de [dia, hora]


@dataclass
class Aula:
    """
    Representa un aula o espacio físico.

    Atributos:
        id        : Identificador único (ej. "AULA01")
        nombre    : Nombre del aula (ej. "Salón 101")
        capacidad : Número máximo de alumnos que puede albergar
    """
    id: str
    nombre: str
    capacidad: int


@dataclass
class Grupo:
    """
    Representa un grupo de estudiantes.

    Atributos:
        id          : Identificador único (ej. "GRP01")
        nombre      : Nombre del grupo (ej. "1°A")
        num_alumnos : Número de alumnos en el grupo
        materias_ids: Lista de IDs de materias que debe cursar este grupo
    """
    id: str
    nombre: str
    num_alumnos: int
    materias_ids: List[str]

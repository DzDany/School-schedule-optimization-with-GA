"""
horario.py
----------
Define Sesion (una clase asignada a un slot) y Horario (conjunto de sesiones).
Estas son las unidades de salida del algoritmo genético.
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Sesion:
    """
    Representa una clase asignada en un slot de tiempo concreto.
    Es la unidad mínima (gen) dentro de un cromosoma.

    Atributos:
        grupo_id   : ID del grupo que recibe la clase
        materia_id : ID de la materia que se imparte
        profesor_id: ID del profesor que la imparte
        aula_id    : ID del aula donde se realiza
        dia        : Día de la semana (ej. "Lunes")
        hora       : Hora de inicio en formato entero (ej. 7 = 7:00 am)
    """
    grupo_id: str
    materia_id: str
    profesor_id: str
    aula_id: str
    dia: str
    hora: int


@dataclass
class Horario:
    """
    Representa un horario escolar completo: el conjunto de todas las sesiones
    asignadas para todos los grupos, materias y profesores.

    Es la representación de alto nivel de un cromosoma ya evaluado.
    """
    sesiones: List[Sesion] = field(default_factory=list)

    def sesiones_de_grupo(self, grupo_id: str) -> List[Sesion]:
        """Filtra las sesiones de un grupo específico."""
        return [s for s in self.sesiones if s.grupo_id == grupo_id]

    def sesiones_de_profesor(self, profesor_id: str) -> List[Sesion]:
        """Filtra las sesiones de un profesor específico."""
        return [s for s in self.sesiones if s.profesor_id == profesor_id]

    def sesiones_en_slot(self, dia: str, hora: int) -> List[Sesion]:
        """Retorna todas las sesiones que ocurren en un día y hora dados."""
        return [s for s in self.sesiones if s.dia == dia and s.hora == hora]

    def to_dict(self) -> List[Dict]:
        """Convierte el horario a una lista de dicts (útil para exportar)."""
        return [
            {
                "grupo_id": s.grupo_id,
                "materia_id": s.materia_id,
                "profesor_id": s.profesor_id,
                "aula_id": s.aula_id,
                "dia": s.dia,
                "hora": f"{s.hora}:00"
            }
            for s in self.sesiones
        ]

    def __len__(self) -> int:
        return len(self.sesiones)

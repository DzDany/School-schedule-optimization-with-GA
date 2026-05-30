"""
chromosome.py
-------------
Define el Cromosoma: la representación de un horario completo como individuo
del algoritmo genético.

Cada cromosoma es una lista de Sesiones (genes). Una sesión = un gen =
la asignación de (grupo, materia, profesor, aula, día, hora).

El número de genes de un cromosoma es fijo:
    suma de (horas_semana de cada materia * número de grupos que la cursan)
"""

import random
from typing import List, Dict

from src.models.entities import Materia, Profesor, Aula, Grupo
from src.models.horario import Sesion, Horario

# ─── Constantes del espacio de búsqueda ──────────────────────────────────────

DIAS: List[str] = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
HORAS: List[int] = list(range(7, 17))  # 7:00 am – 4:00 pm (10 franjas)


# ─── Clase Cromosoma ──────────────────────────────────────────────────────────

class Chromosome:
    """
    Representa a un individuo de la población: un horario escolar completo.

    Atributos:
        genes        : Lista de Sesion — cada gen es una clase asignada
        fitness_score: Puntuación asignada por FitnessEvaluator (0.0 – 1.0)
                       1.0 = horario perfecto sin conflictos
    """

    def __init__(self, genes: List[Sesion]):
        self.genes: List[Sesion] = genes
        self.fitness_score: float = 0.0

    # ── Generación aleatoria ──────────────────────────────────────────────────

    @staticmethod
    def generar_aleatorio(
        grupos: Dict[str, Grupo],
        materias: Dict[str, Materia],
        profesores_por_materia: Dict[str, List[Profesor]],
        aulas: List[Aula]
    ) -> "Chromosome":
        """
        Crea un cromosoma con asignaciones completamente aleatorias.

        Para cada grupo y cada materia que debe cursar, genera tantos genes
        como horas_semana indique la materia. Cada gen elige aleatoriamente
        profesor, aula, día y hora dentro del espacio válido.

        Parámetros:
            grupos                : Dict de grupos del problema
            materias              : Dict de materias del problema
            profesores_por_materia: Índice {materia_id -> [Profesor, ...]}
            aulas                 : Lista de aulas disponibles

        Retorna:
            Un Chromosome con genes generados al azar (aún sin evaluar)
        """
        genes: List[Sesion] = []

        for grupo in grupos.values():
            for materia_id in grupo.materias_ids:

                materia = materias.get(materia_id)
                candidatos = profesores_por_materia.get(materia_id, [])

                if not materia or not candidatos:
                    continue  # Dato incompleto: se omite esta sesión

                for _ in range(materia.horas_semana):
                    # 1. Elegir un profesor aleatorio válido para la materia
                    prof_elegido = random.choice(candidatos)
                    
                    # 2. Elegir un día y hora SOLO de su lista de disponibilidad
                    if prof_elegido.disponibilidad:
                        slot_elegido = random.choice(prof_elegido.disponibilidad)
                        dia_elegido = slot_elegido[0]
                        hora_elegida = slot_elegido[1]
                    else:
                        # Fallback por si el profe no tiene disponibilidad declarada
                        dia_elegido = random.choice(DIAS)
                        hora_elegida = random.choice(HORAS)

                    genes.append(Sesion(
                        grupo_id=grupo.id,
                        materia_id=materia_id,
                        profesor_id=prof_elegido.id,
                        aula_id=random.choice(aulas).id,
                        dia=dia_elegido,
                        hora=hora_elegida
                    ))

        return Chromosome(genes)

    # ── Utilidades ────────────────────────────────────────────────────────────

    def to_horario(self) -> Horario:
        """Convierte el cromosoma en un objeto Horario listo para exportar."""
        return Horario(sesiones=list(self.genes))

    def copy(self) -> "Chromosome":
        """Devuelve una copia profunda del cromosoma."""
        copia = Chromosome([
            Sesion(
                grupo_id=s.grupo_id,
                materia_id=s.materia_id,
                profesor_id=s.profesor_id,
                aula_id=s.aula_id,
                dia=s.dia,
                hora=s.hora
            )
            for s in self.genes
        ])
        copia.fitness_score = self.fitness_score
        return copia

    def __len__(self) -> int:
        return len(self.genes)

    def __repr__(self) -> str:
        return f"Chromosome(genes={len(self.genes)}, fitness={self.fitness_score:.4f})"

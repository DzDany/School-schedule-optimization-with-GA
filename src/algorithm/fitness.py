"""
fitness.py
----------
Evalúa la calidad de un cromosoma contando violaciones de restricciones.

Restricciones DURAS (penalizan mucho — el horario no es válido si ocurren):
    1. Conflicto de profesor: el mismo profesor en dos lugares al mismo tiempo
    2. Conflicto de aula   : la misma aula ocupada dos veces al mismo tiempo
    3. Conflicto de grupo  : el mismo grupo con dos clases al mismo tiempo
    4. Disponibilidad      : el profesor no está disponible en ese slot

Restricciones BLANDAS (penalizan menos — el horario es válido pero no óptimo):
    5. Capacidad de aula   : el grupo tiene más alumnos que el aforo del aula

Fórmula de fitness:
    score = 1 / (1 + total_penalización)
    → varía entre (0, 1], donde 1.0 es un horario perfecto sin violaciones.
"""

from collections import defaultdict
from typing import Dict, List

from src.algorithm.chromosome import Cromosoma
from src.models.entities import Profesor, Aula, Grupo


# Pesos de penalización por tipo de violación
PENALIZACION_CONFLICTO_PROFESOR = 10
PENALIZACION_CONFLICTO_AULA     = 10
PENALIZACION_CONFLICTO_GRUPO    = 10
PENALIZACION_DISPONIBILIDAD     = 10
PENALIZACION_CAPACIDAD          = 5


class EvaluadorAptitud:
    """
    Evalúa cromosomas del horario escolar.

    Uso:
        evaluador = EvaluadorAptitud(profesores, aulas, grupos)
        score = evaluador.evaluar(cromosoma)
        # cromosoma.puntaje_aptitud también queda actualizado
    """

    def __init__(
        self,
        profesores: Dict[str, Profesor],
        aulas: Dict[str, Aula],
        grupos: Dict[str, Grupo]
    ):
        self.profesores = profesores
        self.aulas = aulas
        self.grupos = grupos

    # ── Método principal ──────────────────────────────────────────────────────

    def evaluar(self, cromosoma: Cromosoma) -> float:
        """
        Calcula y asigna el puntaje_aptitud del cromosoma.

        Retorna:
            float en (0.0, 1.0] — mayor es mejor
        """
        penalizacion = self._calcular_penalizacion(cromosoma)
        score = 1.0 / (1.0 + penalizacion)
        cromosoma.puntaje_aptitud = score
        return score

    # ── Desglose para debugging ───────────────────────────────────────────────

    def reporte_violaciones(self, cromosoma: Cromosoma) -> Dict[str, int]:
        """
        Retorna un desglose de cuántas violaciones hay por tipo.
        Útil para diagnosticar qué restricciones se están rompiendo más.

        Retorna:
            Dict con claves: 'conflicto_profesor', 'conflicto_aula',
            'conflicto_grupo', 'disponibilidad', 'capacidad', 'total'
        """
        slots_profesor: Dict = defaultdict(list)
        slots_aula    : Dict = defaultdict(list)
        slots_grupo   : Dict = defaultdict(list)

        for s in cromosoma.genes:
            slots_profesor[(s.profesor_id, s.dia, s.hora)].append(s)
            slots_aula    [(s.aula_id,     s.dia, s.hora)].append(s)
            slots_grupo   [(s.grupo_id,    s.dia, s.hora)].append(s)

        conflicto_profesor = sum(
            len(v) - 1 for v in slots_profesor.values() if len(v) > 1
        )
        conflicto_aula = sum(
            len(v) - 1 for v in slots_aula.values() if len(v) > 1
        )
        conflicto_grupo = sum(
            len(v) - 1 for v in slots_grupo.values() if len(v) > 1
        )

        disponibilidad = sum(
            1
            for s in cromosoma.genes
            if self.profesores.get(s.profesor_id)
            and [s.dia, s.hora] not in self.profesores[s.profesor_id].disponibilidad
        )

        capacidad = sum(
            1
            for s in cromosoma.genes
            if self.aulas.get(s.aula_id)
            and self.grupos.get(s.grupo_id)
            and self.grupos[s.grupo_id].num_alumnos > self.aulas[s.aula_id].capacidad
        )

        total = (
            conflicto_profesor + conflicto_aula + conflicto_grupo
            + disponibilidad + capacidad
        )

        return {
            "conflicto_profesor": conflicto_profesor,
            "conflicto_aula"    : conflicto_aula,
            "conflicto_grupo"   : conflicto_grupo,
            "disponibilidad"    : disponibilidad,
            "capacidad"         : capacidad,
            "total_violaciones" : total
        }

    # ── Lógica interna ────────────────────────────────────────────────────────

    def _calcular_penalizacion(self, cromosoma: Cromosoma) -> float:
        """Suma las penalizaciones de todas las restricciones."""
        penalizacion = 0.0

        slots_profesor: Dict = defaultdict(int)
        slots_aula    : Dict = defaultdict(int)
        slots_grupo   : Dict = defaultdict(int)

        for s in cromosoma.genes:
            slots_profesor[(s.profesor_id, s.dia, s.hora)] += 1
            slots_aula    [(s.aula_id,     s.dia, s.hora)] += 1
            slots_grupo   [(s.grupo_id,    s.dia, s.hora)] += 1

        # Restricción 1: conflicto de profesor
        for count in slots_profesor.values():
            if count > 1:
                penalizacion += (count - 1) * PENALIZACION_CONFLICTO_PROFESOR

        # Restricción 2: conflicto de aula
        for count in slots_aula.values():
            if count > 1:
                penalizacion += (count - 1) * PENALIZACION_CONFLICTO_AULA

        # Restricción 3: conflicto de grupo
        for count in slots_grupo.values():
            if count > 1:
                penalizacion += (count - 1) * PENALIZACION_CONFLICTO_GRUPO

        # Restricción 4: disponibilidad del profesor
        for s in cromosoma.genes:
            prof = self.profesores.get(s.profesor_id)
            if prof and [s.dia, s.hora] not in prof.disponibilidad:
                penalizacion += PENALIZACION_DISPONIBILIDAD

        # Restricción 5 (blanda): capacidad del aula
        for s in cromosoma.genes:
            aula  = self.aulas.get(s.aula_id)
            grupo = self.grupos.get(s.grupo_id)
            if aula and grupo and grupo.num_alumnos > aula.capacidad:
                penalizacion += PENALIZACION_CAPACIDAD

        # Restricción 6: una materia debe tomarse siempre en el mismo aula
        aula_por_materia = {}
        for s in cromosoma.genes:
            clave = (s.grupo_id, s.materia_id, s.profesor_id)
            if clave not in aula_por_materia:
                aula_por_materia[clave] = s.aula_id
            elif aula_por_materia[clave] != s.aula_id:
                penalizacion += 8

        return penalizacion

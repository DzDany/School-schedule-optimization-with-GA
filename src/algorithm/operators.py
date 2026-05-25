"""
operators.py
------------
Implementa los tres operadores del algoritmo genético:

    1. Selección por torneo  — elige al mejor de un subconjunto aleatorio
    2. Cruce de un punto     — combina dos padres para producir dos hijos
    3. Mutación aleatoria    — modifica genes con probabilidad tasa_mutacion

Todos los operadores devuelven NUEVOS objetos sin modificar los originales.
"""

import random
from typing import List, Dict, Tuple

from src.algorithm.chromosome import Chromosome, DIAS, HORAS
from src.models.entities import Profesor, Aula
from src.models.horario import Sesion


class GeneticOperators:
    """
    Contiene los operadores genéticos parametrizables.

    Parámetros de construcción:
        profesores_por_materia: Dict {materia_id -> [Profesor, ...]}
                                Necesario para mutar el gen 'profesor' con un
                                candidato válido para esa materia.
        aulas                 : Lista de Aula disponibles (para mutar 'aula')
        tasa_mutacion         : Probabilidad de mutar cada gen (0.0 – 1.0)
                                Recomendado: 0.01 – 0.05
        tam_torneo            : Candidatos por torneo en la selección
                                Recomendado: 3 – 5
    """

    def __init__(
        self,
        profesores_por_materia: Dict[str, List[Profesor]],
        aulas: List[Aula],
        tasa_mutacion: float = 0.03,
        tam_torneo: int = 3
    ):
        self.profesores_por_materia = profesores_por_materia
        self.aulas = aulas
        self.tasa_mutacion = tasa_mutacion
        self.tam_torneo = tam_torneo

    # ── 1. Selección por torneo ───────────────────────────────────────────────

    def seleccion_torneo(self, poblacion: List[Chromosome]) -> Chromosome:
        """
        Selecciona al mejor individuo de un subconjunto aleatorio de la
        población (torneo). Favorece a los mejores sin eliminar a los peores.

        Parámetros:
            poblacion: Lista de cromosomas ya evaluados (con fitness_score)

        Retorna:
            El cromosoma con mayor fitness_score del torneo (sin copiarlo)
        """
        k = min(self.tam_torneo, len(poblacion))
        candidatos = random.sample(poblacion, k)
        return max(candidatos, key=lambda c: c.fitness_score)

    # ── 2. Cruce de un punto ──────────────────────────────────────────────────

    def cruce_un_punto(
        self, padre1: Chromosome, padre2: Chromosome
    ) -> Tuple[Chromosome, Chromosome]:
        """
        Cruce de un punto: divide ambos padres en el mismo punto aleatorio
        e intercambia sus segmentos para producir dos hijos.

        Si los cromosomas tienen distinto largo (no debería ocurrir con datos
        consistentes), devuelve copias de los padres sin cruzar.

        Parámetros:
            padre1, padre2: Cromosomas seleccionados como padres

        Retorna:
            Tupla (hijo1, hijo2) — nuevos cromosomas, fitness_score = 0.0
        """
        n = len(padre1)
        if n != len(padre2) or n < 2:
            return padre1.copy(), padre2.copy()

        punto = random.randint(1, n - 1)

        hijo1 = Chromosome(padre1.genes[:punto] + padre2.genes[punto:])
        hijo2 = Chromosome(padre2.genes[:punto] + padre1.genes[punto:])

        return hijo1, hijo2

    # ── 3. Mutación aleatoria ─────────────────────────────────────────────────

    def mutar(self, cromosoma: Chromosome) -> Chromosome:
        """
        Recorre cada gen del cromosoma y, con probabilidad tasa_mutacion,
        cambia aleatoriamente UNO de sus atributos:
            • 'profesor' → otro profesor válido para esa materia
            • 'aula'     → otra aula aleatoria
            • 'dia'      → otro día de la semana
            • 'hora'     → otra hora del día

        Parámetros:
            cromosoma: Cromosoma a mutar (no se modifica el original)

        Retorna:
            Nuevo cromosoma con los genes potencialmente mutados
        """
        nuevo = cromosoma.copy()

        for i, sesion in enumerate(nuevo.genes):
            if random.random() >= self.tasa_mutacion:
                continue  # Este gen no muta

            aspecto = random.choice(["profesor", "aula", "dia", "hora"])

            if aspecto == "profesor":
                candidatos = self.profesores_por_materia.get(sesion.materia_id, [])
                if candidatos:
                    nuevo.genes[i] = Sesion(
                        grupo_id=sesion.grupo_id,
                        materia_id=sesion.materia_id,
                        profesor_id=random.choice(candidatos).id,
                        aula_id=sesion.aula_id,
                        dia=sesion.dia,
                        hora=sesion.hora
                    )

            elif aspecto == "aula":
                nuevo.genes[i] = Sesion(
                    grupo_id=sesion.grupo_id,
                    materia_id=sesion.materia_id,
                    profesor_id=sesion.profesor_id,
                    aula_id=random.choice(self.aulas).id,
                    dia=sesion.dia,
                    hora=sesion.hora
                )

            elif aspecto == "dia":
                nuevo.genes[i] = Sesion(
                    grupo_id=sesion.grupo_id,
                    materia_id=sesion.materia_id,
                    profesor_id=sesion.profesor_id,
                    aula_id=sesion.aula_id,
                    dia=random.choice(DIAS),
                    hora=sesion.hora
                )

            elif aspecto == "hora":
                nuevo.genes[i] = Sesion(
                    grupo_id=sesion.grupo_id,
                    materia_id=sesion.materia_id,
                    profesor_id=sesion.profesor_id,
                    aula_id=sesion.aula_id,
                    dia=sesion.dia,
                    hora=random.choice(HORAS)
                )

        nuevo.fitness_score = 0.0  # Requiere re-evaluación
        return nuevo

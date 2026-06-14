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

from src.algorithm.chromosome import Cromosoma, DIAS, HORAS
from src.models.entities import Profesor, Aula
from src.models.horario import Sesion


class OperadoresGeneticos:
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
        profesores: Dict[str, Profesor] = None,
        tasa_mutacion: float = 0.02,
        tam_torneo: int = 3
    ):
        self.profesores_por_materia = profesores_por_materia
        self.aulas = aulas
        self.profesores = profesores
        self.tasa_mutacion = tasa_mutacion
        self.tam_torneo = tam_torneo

    # ── 1. Selección por torneo ───────────────────────────────────────────────

    def seleccion_torneo(self, poblacion: List[Cromosoma]) -> Cromosoma:
        """
        Selecciona al mejor individuo de un subconjunto aleatorio de la
        población (torneo). Favorece a los mejores sin eliminar a los peores.

        Parámetros:
            poblacion: Lista de cromosomas ya evaluados (con puntaje_aptitud)

        Retorna:
            El cromosoma con mayor puntaje_aptitud del torneo (sin copiarlo)
        """
        k = min(self.tam_torneo, len(poblacion))
        candidatos = random.sample(poblacion, k)
        return max(candidatos, key=lambda c: c.puntaje_aptitud)

    # ── 2. Cruce de un punto ──────────────────────────────────────────────────

    def cruce_por_materias(
        self, padre1: Cromosoma, padre2: Cromosoma) -> Tuple[Cromosoma, Cromosoma]:
        """
        Cruce por Materias: En lugar de intercambiar grupos completos, 
        intercambia los horarios completos de cada MATERIA (por grupo) entre los padres.
        Garantiza que no se dupliquen ni falten horas de ninguna materia.
        """
        # 1. Identificar todos los bloques únicos (grupo, materia)
        bloques_ids = list(set((s.grupo_id, s.materia_id) for s in padre1.genes))

        # Si solo hay una materia en total, el cruce no tiene sentido.
        if len(bloques_ids) < 2:
            return padre1.copy(), padre2.copy()

        # 2. Elegir un punto de corte aleatorio
        punto = random.randint(1, len(bloques_ids) - 1)
        bloques_mitad_1 = set(bloques_ids[:punto])
        bloques_mitad_2 = set(bloques_ids[punto:])

        # 3. Construir los genes del Hijo 1
        hijo1_genes = []
        for s in padre1.genes:
            if (s.grupo_id, s.materia_id) in bloques_mitad_1:
                hijo1_genes.append(Sesion(
                    s.grupo_id, s.materia_id, s.profesor_id, s.aula_id, s.dia, s.hora
                ))
        for s in padre2.genes:
            if (s.grupo_id, s.materia_id) in bloques_mitad_2:
                hijo1_genes.append(Sesion(
                    s.grupo_id, s.materia_id, s.profesor_id, s.aula_id, s.dia, s.hora
                ))

        # 4. Construir los genes del Hijo 2
        hijo2_genes = []
        for s in padre2.genes:
            if (s.grupo_id, s.materia_id) in bloques_mitad_1:
                hijo2_genes.append(Sesion(
                    s.grupo_id, s.materia_id, s.profesor_id, s.aula_id, s.dia, s.hora
                ))
        for s in padre1.genes:
            if (s.grupo_id, s.materia_id) in bloques_mitad_2:
                hijo2_genes.append(Sesion(
                    s.grupo_id, s.materia_id, s.profesor_id, s.aula_id, s.dia, s.hora
                ))

        # 5. Retornar los nuevos individuos
        return Cromosoma(hijo1_genes), Cromosoma(hijo2_genes)

    # ── 3. Mutación aleatoria ─────────────────────────────────────────────────

    def mutar(self, cromosoma: Cromosoma) -> Cromosoma:
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

            # Agrupamos dia y hora en "tiempo"
            aspecto = random.choice(["profesor", "tiempo"])

            if aspecto == "profesor":
                candidatos = self.profesores_por_materia.get(sesion.materia_id, [])
                if candidatos:
                    nuevo_prof = random.choice(candidatos)
                    # CRÍTICO: Si cambiamos de profesor, DEBEMOS asignarle una hora en la que él pueda.
                    if nuevo_prof.disponibilidad:
                        nuevo_slot = random.choice(nuevo_prof.disponibilidad)
                        nuevo_dia, nueva_hora = nuevo_slot[0], nuevo_slot[1]
                    else:
                        nuevo_dia, nueva_hora = sesion.dia, sesion.hora
                        
                    nuevo.genes[i] = Sesion(
                        grupo_id=sesion.grupo_id,
                        materia_id=sesion.materia_id,
                        profesor_id=nuevo_prof.id,
                        aula_id=sesion.aula_id,
                        dia=nuevo_dia,
                        hora=nueva_hora
                    )

            elif aspecto == "tiempo":
                # Cambiamos la hora, pero sacándola de la disponibilidad del profesor actual
                prof_actual = self.profesores.get(sesion.profesor_id)
                if prof_actual and prof_actual.disponibilidad:
                    nuevo_slot = random.choice(prof_actual.disponibilidad)
                    nuevo_dia, nueva_hora = nuevo_slot[0], nuevo_slot[1]
                else:
                    nuevo_dia, nueva_hora = random.choice(DIAS), random.choice(HORAS)
                    
                nuevo.genes[i] = Sesion(
                    grupo_id=sesion.grupo_id,
                    materia_id=sesion.materia_id,
                    profesor_id=sesion.profesor_id,
                    aula_id=sesion.aula_id,
                    dia=nuevo_dia,
                    hora=nueva_hora
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

        nuevo.puntaje_aptitud = 0.0  # Requiere re-evaluación
        return nuevo

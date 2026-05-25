"""
loader.py
---------
Carga la configuración del problema desde archivos JSON.
Produce los diccionarios de entidades que el algoritmo necesita.
"""

import json
from typing import Dict, List, Tuple

from src.models.entities import Materia, Profesor, Aula, Grupo


class DataLoader:
    """
    Encargado de leer los datos de entrada del problema.

    Uso:
        loader = DataLoader()
        materias, profesores, aulas, grupos = loader.cargar_desde_json("data/config.json")
    """

    def cargar_desde_json(
        self, ruta: str
    ) -> Tuple[Dict[str, Materia], Dict[str, Profesor], Dict[str, Aula], Dict[str, Grupo]]:
        """
        Lee un archivo JSON con la configuración escolar y devuelve
        diccionarios de entidades indexados por su ID.

        Parámetros:
            ruta: Ruta al archivo JSON

        Retorna:
            (materias, profesores, aulas, grupos) — cada uno es un dict {id: entidad}
        """
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)

        materias = {
            m["id"]: Materia(
                id=m["id"],
                nombre=m["nombre"],
                horas_semana=m["horas_semana"]
            )
            for m in data["materias"]
        }

        profesores = {
            p["id"]: Profesor(
                id=p["id"],
                nombre=p["nombre"],
                materias_ids=p["materias_ids"],
                disponibilidad=p["disponibilidad"]
            )
            for p in data["profesores"]
        }

        aulas = {
            a["id"]: Aula(
                id=a["id"],
                nombre=a["nombre"],
                capacidad=a["capacidad"]
            )
            for a in data["aulas"]
        }

        grupos = {
            g["id"]: Grupo(
                id=g["id"],
                nombre=g["nombre"],
                num_alumnos=g["num_alumnos"],
                materias_ids=g["materias_ids"]
            )
            for g in data["grupos"]
        }

        return materias, profesores, aulas, grupos

    def construir_profesores_por_materia(
        self, profesores: Dict[str, Profesor]
    ) -> Dict[str, List[Profesor]]:
        """
        Construye un índice de qué profesores pueden impartir cada materia.
        Útil para generar cromosomas válidos rápidamente.

        Retorna:
            Dict {materia_id: [lista de Profesores que la pueden impartir]}
        """
        resultado: Dict[str, List[Profesor]] = {}
        for prof in profesores.values():
            for mat_id in prof.materias_ids:
                if mat_id not in resultado:
                    resultado[mat_id] = []
                resultado[mat_id].append(prof)
        return resultado

    def validar_datos(
        self,
        materias: Dict[str, Materia],
        profesores: Dict[str, Profesor],
        aulas: Dict[str, Aula],
        grupos: Dict[str, Grupo]
    ) -> List[str]:
        """
        Verifica que los datos sean consistentes antes de correr el algoritmo.
        Retorna una lista de advertencias (vacía si todo está bien).
        """
        advertencias = []

        # Verificar que cada materia referenciada por grupos exista
        for grupo in grupos.values():
            for mat_id in grupo.materias_ids:
                if mat_id not in materias:
                    advertencias.append(
                        f"Grupo '{grupo.id}' referencia materia inexistente '{mat_id}'"
                    )

        # Verificar que cada materia referenciada por profesores exista
        for prof in profesores.values():
            for mat_id in prof.materias_ids:
                if mat_id not in materias:
                    advertencias.append(
                        f"Profesor '{prof.id}' referencia materia inexistente '{mat_id}'"
                    )

        # Verificar que exista al menos un profesor por cada materia requerida
        profesores_por_materia = self.construir_profesores_por_materia(profesores)
        for grupo in grupos.values():
            for mat_id in grupo.materias_ids:
                if mat_id not in profesores_por_materia:
                    advertencias.append(
                        f"La materia '{mat_id}' no tiene ningún profesor asignado"
                    )

        return advertencias

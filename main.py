"""
main.py
---------------

Verifica que:
Punto de entrada principal para la optimización de horarios escolares.
Ejecuta el ciclo evolutivo completo del Algoritmo Genético.

Ejecutar desde la raíz del proyecto:
    python main.py
"""
import sys
MAX_HORAS_LIBRES = int(sys.argv[1]) if len(sys.argv) > 1 else 3
print(f"DEBUG MAX_HORAS_LIBRES: {MAX_HORAS_LIBRES}", flush=True)
import os
import json
from collections import defaultdict

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data.loader import CargadorDatos
from src.algorithm.chromosome import Cromosoma
from src.algorithm.fitness import EvaluadorAptitud
from src.algorithm.operators import OperadoresGeneticos


def separador(titulo: str):
    print(f"\n{'=' * 50}")
    print(f"  {titulo}")
    print('=' * 50)


def main():
    # ── 0. Parámetros configurables (Definidos en el reporte) ─────────────
    POP_SIZE = 100
    MAX_GENERACIONES = 500
    TASA_MUTACION = 0.03
    TAM_TORNEO = 3
    UMBRAL_FITNESS = 0.98
    GEN_SIN_MEJORA_MAX = 50
    ELITISMO = True

    # ── 1. Cargar y validar datos ─────────────────────────────────────────
    separador("1. Carga de datos")

    loader = CargadorDatos()

    materias, profesores, aulas, grupos = loader.cargar_desde_json(
        "data/sample_config.json"
    )

    print(
        f"Grupos: {len(grupos)} | "
        f"Materias: {len(materias)} | "
        f"Profesores: {len(profesores)} | "
        f"Aulas: {len(aulas)}"
    )

    advertencias = loader.validar_datos(
        materias,
        profesores,
        aulas,
        grupos
    )

    if advertencias:
        for w in advertencias:
            print(f"⚠ {w}")
    else:
        print("✓ Datos iniciales validados correctamente.")

    # ── 2. Inicialización ─────────────────────────────────────────────────
    profesores_por_materia = loader.construir_profesores_por_materia(
        profesores
    )

    lista_aulas = list(aulas.values())

    evaluador = EvaluadorAptitud(
        profesores,
        aulas,
        grupos,
        max_horas_libres=MAX_HORAS_LIBRES
    )

    operadores = OperadoresGeneticos(
        profesores_por_materia=profesores_por_materia,
        aulas=lista_aulas,
        profesores=profesores,
        tasa_mutacion=TASA_MUTACION,
        tam_torneo=TAM_TORNEO
    )

    def correr_evolucion(numero):
        separador(f"Corrida {numero}/3")

        poblacion = [
            Cromosoma.generar_aleatorio(
                grupos,
                materias,
                profesores_por_materia,
                lista_aulas
            )
            for _ in range(POP_SIZE)
        ]

        for cromosoma in poblacion:
            evaluador.evaluar(cromosoma)

        mejor = max(
            poblacion,
            key=lambda c: c.puntaje_aptitud
        )

        generaciones_sin_mejora = 0

        for generacion in range(1, MAX_GENERACIONES + 1):

            nueva_poblacion = []

            if ELITISMO:
                mejor_actual = max(
                    poblacion,
                    key=lambda c: c.puntaje_aptitud
                )
                nueva_poblacion.append(mejor_actual.copy())

            while len(nueva_poblacion) < POP_SIZE:

                padre1 = operadores.seleccion_torneo(
                    poblacion
                )

                padre2 = operadores.seleccion_torneo(
                    poblacion
                )

                hijo1, hijo2 = operadores.cruce_por_materias(
                    padre1,
                    padre2
                )

                hijo1 = operadores.mutar(hijo1)
                hijo2 = operadores.mutar(hijo2)

                evaluador.evaluar(hijo1)
                evaluador.evaluar(hijo2)

                nueva_poblacion.append(hijo1)

                if len(nueva_poblacion) < POP_SIZE:
                    nueva_poblacion.append(hijo2)

            poblacion = nueva_poblacion

            mejor_gen = max(
                poblacion,
                key=lambda c: c.puntaje_aptitud
            )

            if mejor_gen.puntaje_aptitud > mejor.puntaje_aptitud:
                mejor = mejor_gen.copy()
                generaciones_sin_mejora = 0
            else:
                generaciones_sin_mejora += 1

            if generacion % 10 == 0:
                print(
                    f"  Gen {generacion:3d} | "
                    f"Aptitud: {mejor.puntaje_aptitud:.4f}"
                )

            if mejor.puntaje_aptitud >= UMBRAL_FITNESS:
                print(
                    f"  ✓ Umbral alcanzado "
                    f"en generación {generacion}"
                )
                break

            if generaciones_sin_mejora >= GEN_SIN_MEJORA_MAX:
                print(
                    f"  ⚠ Estancamiento "
                    f"en generación {generacion}"
                )
                break

        print(
            f"  Mejor aptitud: "
            f"{mejor.puntaje_aptitud:.4f}"
        )

        slots_ocupados_grupo = defaultdict(set)
        for s in mejor.genes:
            slots_ocupados_grupo[(s.grupo_id, s.dia)].add(s.hora)

        advertencia_horas = False
        for (grupo_id, dia), horas in slots_ocupados_grupo.items():
            if horas:
                hora_min = min(horas)
                hora_max = max(horas)
                libres = (hora_max - hora_min + 1) - len(horas)
                if libres > MAX_HORAS_LIBRES:
                    print(f"  ⚠ El grupo {grupo_id} el {dia} tiene {libres} horas libres (máx. permitido: {MAX_HORAS_LIBRES})")
                    advertencia_horas = True

        if advertencia_horas:
            print(f"  ⚠ No se pudo cumplir la restricción de horas libres en esta corrida.")

        return mejor

    # ── Ejecutar 3 corridas independientes ───────────────────────────────
    separador("Iniciando 3 corridas independientes")

    top3 = [
        correr_evolucion(i)
        for i in range(1, 4)
    ]

    # ── Resultados finales ────────────────────────────────────────────────
    separador("Resultados Finales")

    for i, opcion in enumerate(top3, 1):

        print(
            f"Opción {i} | "
            f"Aptitud: {opcion.puntaje_aptitud:.4f}"
        )

        reporte = evaluador.reporte_violaciones(opcion)

        print("Violaciones:")
        for tipo, cantidad in reporte.items():
            print(f"  - {tipo:25s}: {cantidad}")

        horario = opcion.to_horario()

        ruta = f"data/horario_opcion_{i}.json"

        with open(
            ruta,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                horario.to_dict(),
                f,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"✓ Opción {i} exportada "
            f"(aptitud: {opcion.puntaje_aptitud:.4f}) "
            f"→ '{ruta}'"
        )


if __name__ == "__main__":
    main()
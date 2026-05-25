"""
demo_parte_a.py
---------------
Script de demostración / prueba de humo para la Parte A.

Verifica que:
  1. Los datos se cargan correctamente desde JSON
  2. Se pueden generar cromosomas aleatorios
  3. La función de fitness evalúa correctamente
  4. Los operadores (selección, cruce, mutación) producen resultados válidos

Ejecutar desde la raíz del proyecto:
    python demo_parte_a.py
"""

import sys
import os

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data.loader import DataLoader
from src.algorithm.chromosome import Chromosome
from src.algorithm.fitness import FitnessEvaluator
from src.algorithm.operators import GeneticOperators


def separador(titulo: str):
    print(f"\n{'─' * 50}")
    print(f"  {titulo}")
    print('─' * 50)


def main():
    # ── 1. Cargar datos ───────────────────────────────────────────────────────
    separador("1. Carga de datos")

    loader = DataLoader()
    materias, profesores, aulas, grupos = loader.cargar_desde_json(
        "data/sample_config.json"
    )

    print(f"  Materias  : {len(materias)}")
    print(f"  Profesores: {len(profesores)}")
    print(f"  Aulas     : {len(aulas)}")
    print(f"  Grupos    : {len(grupos)}")

    advertencias = loader.validar_datos(materias, profesores, aulas, grupos)
    if advertencias:
        print("\n  ⚠ Advertencias:")
        for w in advertencias:
            print(f"    - {w}")
    else:
        print("\n  ✓ Datos válidos — sin advertencias")

    # ── 2. Generar cromosomas aleatorios ──────────────────────────────────────
    separador("2. Generación de cromosomas")

    profesores_por_materia = loader.construir_profesores_por_materia(profesores)
    lista_aulas = list(aulas.values())

    poblacion = [
        Chromosome.generar_aleatorio(grupos, materias, profesores_por_materia, lista_aulas)
        for _ in range(10)
    ]

    print(f"  Población generada: {len(poblacion)} cromosomas")
    print(f"  Genes por cromosoma: {len(poblacion[0])}")

    sesiones_esperadas = sum(
        mat.horas_semana
        for grupo in grupos.values()
        for mat_id in grupo.materias_ids
        for mat in [materias[mat_id]]
    )
    print(f"  Sesiones esperadas : {sesiones_esperadas}")

    # ── 3. Evaluar fitness ────────────────────────────────────────────────────
    separador("3. Evaluación de fitness")

    evaluador = FitnessEvaluator(profesores, aulas, grupos)

    for i, cromosoma in enumerate(poblacion):
        evaluador.evaluar(cromosoma)

    scores = [c.fitness_score for c in poblacion]
    print(f"  Mejor  fitness: {max(scores):.4f}")
    print(f"  Peor   fitness: {min(scores):.4f}")
    print(f"  Promedio      : {sum(scores)/len(scores):.4f}")

    mejor = max(poblacion, key=lambda c: c.fitness_score)
    reporte = evaluador.reporte_violaciones(mejor)
    print(f"\n  Desglose del mejor cromosoma:")
    for tipo, cantidad in reporte.items():
        print(f"    {tipo:25s}: {cantidad}")

    # ── 4. Operadores genéticos ───────────────────────────────────────────────
    separador("4. Operadores genéticos")

    operadores = GeneticOperators(
        profesores_por_materia=profesores_por_materia,
        aulas=lista_aulas,
        tasa_mutacion=0.05,
        tam_torneo=3
    )

    # Selección
    seleccionado = operadores.seleccion_torneo(poblacion)
    print(f"  Selección por torneo → fitness: {seleccionado.fitness_score:.4f}")

    # Cruce
    padre1 = operadores.seleccion_torneo(poblacion)
    padre2 = operadores.seleccion_torneo(poblacion)
    hijo1, hijo2 = operadores.cruce_un_punto(padre1, padre2)
    print(f"  Cruce: padre1({len(padre1)} genes) + padre2({len(padre2)} genes)"
          f" → hijo1({len(hijo1)}), hijo2({len(hijo2)})")

    # Mutación
    mutado = operadores.mutar(seleccionado)
    evaluador.evaluar(mutado)
    print(f"  Mutación: original({seleccionado.fitness_score:.4f})"
          f" → mutado({mutado.fitness_score:.4f})")

    # ── Resumen ───────────────────────────────────────────────────────────────
    separador("✓ Parte A completada")
    print("  Todos los módulos funcionan correctamente.")
    print("  El compañero puede usar los siguientes objetos:")
    print("    • Chromosome.generar_aleatorio(...)   — crear individuos")
    print("    • FitnessEvaluator.evaluar(cromosoma) — calificarlos")
    print("    • GeneticOperators.seleccion_torneo() — seleccionar")
    print("    • GeneticOperators.cruce_un_punto()   — cruzar")
    print("    • GeneticOperators.mutar()            — mutar")
    print()


if __name__ == "__main__":
    main()

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
import os
import json

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
    ELITISMO = True  # Conservar al mejor individuo intacto de cada generación

    # ── 1. Cargar y validar datos ─────────────────────────────────────────
    separador("1. Carga de datos")
    loader = CargadorDatos()
    materias, profesores, aulas, grupos = loader.cargar_desde_json("data/sample_config.json")
    
    print(f"Grupos: {len(grupos)} | Materias: {len(materias)} | Profesores: {len(profesores)} | Aulas: {len(aulas)}")
    
    advertencias = loader.validar_datos(materias, profesores, aulas, grupos)
    if advertencias:
        for w in advertencias:
            print(f"⚠ {w}")
    else:
        print("✓ Datos iniciales validados correctamente.")

    # ── 2. Inicialización ─────────────────────────────────────────────────
    separador("2. Generando Población Inicial")
    profesores_por_materia = loader.construir_profesores_por_materia(profesores)
    lista_aulas = list(aulas.values())

    evaluador = EvaluadorAptitud(profesores, aulas, grupos)
    operadores = OperadoresGeneticos(
        profesores_por_materia=profesores_por_materia,
        aulas=lista_aulas,
        profesores=profesores,
        tasa_mutacion=TASA_MUTACION,
        tam_torneo=TAM_TORNEO
    )


    # Generar población
    poblacion = [
        Cromosoma.generar_aleatorio(grupos, materias, profesores_por_materia, lista_aulas)
        for _ in range(POP_SIZE)
    ]

    # Evaluar población inicial
    for cromosoma in poblacion:
        evaluador.evaluar(cromosoma)

    mejor_historico = max(poblacion, key=lambda c: c.puntaje_aptitud)
    top3 = [mejor_historico.copy()]
    generaciones_sin_mejora = 0

    print(f"Población inicial lista. Mejor aptitud base: {mejor_historico.puntaje_aptitud:.4f}")

    # ── 3. Bucle Evolutivo ────────────────────────────────────────────────
    separador("3. Iniciando Evolución")

    for generacion in range(1, MAX_GENERACIONES + 1):
        nueva_poblacion = []

        # Elitismo: Guardar al mejor individuo actual
        if ELITISMO:
            mejor_actual = max(poblacion, key=lambda c: c.puntaje_aptitud)
            nueva_poblacion.append(mejor_actual.copy())

        # Crear el resto de la nueva generación
        while len(nueva_poblacion) < POP_SIZE:
            # a. Seleccionar padres
            padre1 = operadores.seleccion_torneo(poblacion)
            padre2 = operadores.seleccion_torneo(poblacion)

            # b. Cruce (Usando la nueva función por grupos)
            hijo1, hijo2 = operadores.cruce_por_grupos(padre1, padre2)

            # c. Mutación
            hijo1 = operadores.mutar(hijo1)
            hijo2 = operadores.mutar(hijo2)

            # d. Evaluar hijos
            evaluador.evaluar(hijo1)
            evaluador.evaluar(hijo2)

            # Agregar a la nueva población (asegurando no pasar de POP_SIZE)
            nueva_poblacion.append(hijo1)
            if len(nueva_poblacion) < POP_SIZE:
                nueva_poblacion.append(hijo2)

        # Reemplazo de población
        poblacion = nueva_poblacion

        # Evaluar progreso
        mejor_generacion = max(poblacion, key=lambda c: c.puntaje_aptitud)
        
        if mejor_generacion.puntaje_aptitud > mejor_historico.puntaje_aptitud:
            mejor_historico = mejor_generacion.copy()
            generaciones_sin_mejora = 0
            top3 = sorted(top3 + [mejor_generacion.copy()], key=lambda c: c.puntaje_aptitud, reverse=True)[:3]
        else:
            generaciones_sin_mejora += 1

        # Imprimir progreso cada 10 generaciones
        if generacion % 10 == 0 or generacion == 1:
            print(f"Generación {generacion:3d} | Mejor Aptitud: {mejor_historico.puntaje_aptitud:.4f} | Sin mejora: {generaciones_sin_mejora}")

        # ── Criterios de Parada ──
        if mejor_historico.puntaje_aptitud >= UMBRAL_FITNESS:
            print(f"\n✓ Criterio de parada alcanzado: Umbral de aptitud superado ({UMBRAL_FITNESS}).")
            break
        
        if generaciones_sin_mejora >= GEN_SIN_MEJORA_MAX:
            print(f"\n⚠ Criterio de parada alcanzado: Estancamiento durante {GEN_SIN_MEJORA_MAX} generaciones.")
            break

    # ── 4. Resultados ─────────────────────────────────────────────────────
    separador("4. Resultados Finales")
    print(f"Mejor aptitud final: {mejor_historico.puntaje_aptitud:.4f}")
    
    reporte = evaluador.reporte_violaciones(mejor_historico)
    print("\nDesglose de violaciones restantes:")
    for tipo, cantidad in reporte.items():
        print(f"  - {tipo:25s}: {cantidad}")

    # Exportar a JSON
    for i, opcion in enumerate(top3, 1):
        horario = opcion.to_horario()
        ruta = f"data/horario_opcion_{i}.json"
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(horario.to_dict(), f, indent=4, ensure_ascii=False)
        print(f"✓ Opción {i} exportada (aptitud: {opcion.puntaje_aptitud:.4f}) → '{ruta}'")


if __name__ == "__main__":
    main()
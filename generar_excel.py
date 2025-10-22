import os
import pandas as pd
import json
from metodo_constructivo import generar_solucion_desde_archivo
from metodo_constructivo_aleatorio import randomized_solution_desde_archivo
from metodo_aleatorio import simulated_annealing_assignments
from metodo_vns import vns_assignments
from score import evaluate_solution


# ======================================================
# FUNCIONES AUXILIARES
# ======================================================

def solution_to_employee_table(sol, days=("L", "Ma", "Mi", "J", "V")) -> pd.DataFrame:
    """Convierte una solución en una tabla por empleado (como en el main anterior)."""
    employees = set()
    for d in sol.values():
        for assigns in d.values():
            for desk, emp in assigns:
                employees.add(emp)

    table = {emp: {day: None for day in days} for emp in employees}

    for day, zones in sol.items():
        if day not in days:
            continue
        for _, assignments in zones.items():
            for desk, emp in assignments:
                table[emp][day] = desk

    def emp_key(e):
        try:
            return int(e[1:]) if e and e[0] in ("E", "e") else e
        except Exception:
            return e

    employees_sorted = sorted(table.keys(), key=emp_key)
    df = pd.DataFrame([{**{"Empleado": emp}, **table[emp]} for emp in employees_sorted])
    return df


# ======================================================
# PROCESADOR DE INSTANCIAS
# ======================================================

def procesar_instancia(path_json: str):
    """
    Dada una instancia (archivo JSON), genera todas las soluciones
    y devuelve los DataFrames listos para exportar.
    """
    print(f"\n🔹 Procesando instancia: {path_json}")

    # 1️⃣ Cargar instancia
    with open(path_json, "r", encoding="utf-8") as f:
        instance = json.load(f)

    # Datos base
    days_e = instance["Days_E"]
    employees_g = instance["Employees_G"]
    groups = list(employees_g.keys())

    # 2️⃣ Soluciones base
    constructive_solution, constructive_groups = generar_solucion_desde_archivo(path_json)
    constructive_score = evaluate_solution(constructive_solution, path_json)

    randomized_solution, randomized_groups = randomized_solution_desde_archivo(path_json)
    randomized_score = evaluate_solution(randomized_solution, path_json)

    annealing_solution, annealing_score, _ = simulated_annealing_assignments(
        constructive_solution, constructive_groups, path_json
    )

    vns_solution, vns_score, _ = vns_assignments(
        constructive_solution, constructive_groups, path_json
    )

    # 3️⃣ Crear DataFrames por método
    df_constructive = solution_to_employee_table(constructive_solution)
    df_randomized = solution_to_employee_table(randomized_solution)
    df_annealing = solution_to_employee_table(annealing_solution)
    df_vns = solution_to_employee_table(vns_solution)

    # 4️⃣ Crear DataFrame de grupos y días de reunión
    df_group_days = pd.DataFrame([
        {"Grupo": g, "Dia_reunion": constructive_groups.get(g, None)} for g in groups
    ])

    # 5️⃣ Empaquetar resultados
    resultados = {
        "constructive": {"solution": df_constructive, "score": constructive_score},
        "randomized": {"solution": df_randomized, "score": randomized_score},
        "annealing": {"solution": df_annealing, "score": annealing_score},
        "vns": {"solution": df_vns, "score": vns_score},
        "group_days": df_group_days,
    }

    return resultados


# ======================================================
# PROCESAMIENTO DE TODAS LAS INSTANCIAS
# ======================================================

def procesar_todas_las_instancias(instances_folder="instances"):
    """
    Procesa las 10 instancias disponibles en la carpeta indicada.
    """
    resultados_globales = {}

    for i in range(1, 11):  # instance1.json → instance10.json
        file_path = os.path.join(instances_folder, f"instance{i}.json")
        if not os.path.exists(file_path):
            print(f"⚠️ No se encontró {file_path}")
            continue

        resultados_globales[f"instance{i}"] = procesar_instancia(file_path)

    return resultados_globales


# ======================================================
# EJECUCIÓN PRINCIPAL
# ======================================================

if __name__ == "__main__":
    resultados = procesar_todas_las_instancias()

    # 🧾 Aquí todavía NO generamos Excel
    # Solo mostramos ejemplo de cómo acceder a los DataFrames
    ejemplo = resultados["instance1"]

    print("\n✅ Ejemplo instancia 1:")
    print("\n--- Días de reunión ---")
    print(ejemplo["group_days"])

    print("\n--- Solución VNS (tabla por empleado) ---")
    print(ejemplo["vns"]["solution"].head())

    print("\n--- Puntuación VNS ---")
    print(ejemplo["vns"]["score"])

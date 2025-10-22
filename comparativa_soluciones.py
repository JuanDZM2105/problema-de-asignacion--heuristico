import time
import pandas as pd
from metodo_constructivo_aleatorio import randomized_solution_desde_archivo
from metodo_constructivo import generar_solucion_desde_archivo
from score import evaluate_solution
from metodo_aleatorio import simulated_annealing_assignments
from metodo_vns import vns_assignments
from busqueda_local import local_search


# ======================================================
# FUNCIONES AUXILIARES
# ======================================================

def solution_to_employee_table(sol, days=("L", "Ma", "Mi", "J", "V")) -> pd.DataFrame:
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
    df = pd.DataFrame([{**{"Employees": emp}, **table[emp]} for emp in employees_sorted])
    return df


# ======================================================
# CONFIGURACIÓN GENERAL
# ======================================================

archivo = "instances/instance1.json"
N = 1000

import json

with open(archivo, "r", encoding="utf-8") as f:
    instance = json.load(f)

# ======================================================
# 1) MÉTODO ALEATORIO (N corridas)
# ======================================================
scores = []
solutions = []
groups_list = []

t0 = time.perf_counter()
for _ in range(N):
    sol, groups = randomized_solution_desde_archivo(archivo)
    s = evaluate_solution(sol, archivo)
    scores.append(s)
    solutions.append(sol)
    groups_list.append(groups)
elapsed_random = time.perf_counter() - t0

mean_score = (
    sum(s[0] for s in scores) / N,
    sum(s[1] for s in scores) / N,
    sum(s[2] for s in scores) / N,
)

best_score = min(scores)
best_index = scores.index(best_score)
best_solution = solutions[best_index]
best_groups = groups_list[best_index]

# ======================================================
# 2) MÉTODO CONSTRUCTIVO
# ======================================================
t1 = time.perf_counter()
constructive_solution, constructive_groups = generar_solucion_desde_archivo(archivo)
constructive_score = evaluate_solution(constructive_solution, archivo)
elapsed_constructive = time.perf_counter() - t1

# ======================================================
# 3) RECOCIDO SIMULADO (Simulated Annealing)
# ======================================================
t2 = time.perf_counter()
best_solution_annealing, best_score_annealing, trace_annealing = simulated_annealing_assignments(
    constructive_solution, constructive_groups, archivo
)
elapsed_annealing = time.perf_counter() - t2

# ======================================================
# 4) VNS (Variable Neighborhood Search)
# ======================================================
t3 = time.perf_counter()
best_solution_vns, best_score_vns, trace_vns = vns_assignments(
    constructive_solution, constructive_groups, archivo
)
elapsed_vns = time.perf_counter() - t3

# ======================================================
# 5) BÚSQUEDA LOCAL
# ======================================================
t4 = time.perf_counter()

best_solution_local_best, best_score_local_best = local_search(archivo, instance, tipo="best")
best_solution_local_first, best_score_local_first = local_search(archivo, instance, tipo="first")

elapsed_local = time.perf_counter() - t4

# ======================================================
# 6) RESUMEN DE RESULTADOS
# ======================================================
summary = pd.DataFrame([
    {
        "method": "randomized",
        "n_runs": N,
        "mean_valid": mean_score[0],
        "mean_pref": mean_score[1],
        "mean_isolated": mean_score[2],
        "best_valid": best_score[0],
        "best_pref": best_score[1],
        "best_isolated": best_score[2],
        "total_time_s": elapsed_random,
    },
    {
        "method": "constructive",
        "n_runs": 1,
        "mean_valid": constructive_score[0],
        "mean_pref": constructive_score[1],
        "mean_isolated": constructive_score[2],
        "best_valid": constructive_score[0],
        "best_pref": constructive_score[1],
        "best_isolated": constructive_score[2],
        "total_time_s": elapsed_constructive,
    },
    {
        "method": "annealing",
        "n_runs": 1000,
        "mean_valid": best_score_annealing[0],
        "mean_pref": best_score_annealing[1],
        "mean_isolated": best_score_annealing[2],
        "best_valid": best_score_annealing[0],
        "best_pref": best_score_annealing[1],
        "best_isolated": best_score_annealing[2],
        "total_time_s": elapsed_annealing,
    },
    {
        "method": "vns",
        "n_runs": 1,
        "mean_valid": best_score_vns[0],
        "mean_pref": best_score_vns[1],
        "mean_isolated": best_score_vns[2],
        "best_valid": best_score_vns[0],
        "best_pref": best_score_vns[1],
        "best_isolated": best_score_vns[2],
        "total_time_s": elapsed_vns,
    },
    {
        "method": "local_search_best",
        "n_runs": 1,
        "mean_valid": best_score_local_best[0],
        "mean_pref": best_score_local_best[1],
        "mean_isolated": best_score_local_best[2],
        "best_valid": best_score_local_best[0],
        "best_pref": best_score_local_best[1],
        "best_isolated": best_score_local_best[2],
        "total_time_s": elapsed_local,
    },
    {
        "method": "local_search_first",
        "n_runs": 1,
        "mean_valid": best_score_local_first[0],
        "mean_pref": best_score_local_first[1],
        "mean_isolated": best_score_local_first[2],
        "best_valid": best_score_local_first[0],
        "best_pref": best_score_local_first[1],
        "best_isolated": best_score_local_first[2],
        "total_time_s": elapsed_local,
    },
])

print("\n==================== RESUMEN DE MÉTODOS ====================")
print(summary)

# ======================================================
# 7) TABLAS DE ASIGNACIÓN POR EMPLEADO
# ======================================================

constructive_table = solution_to_employee_table(constructive_solution)
random_table = solution_to_employee_table(best_solution)
annealing_table = solution_to_employee_table(best_solution_annealing)
vns_table = solution_to_employee_table(best_solution_vns)
local_table_best = solution_to_employee_table(best_solution_local_best)
local_table_first = solution_to_employee_table(best_solution_local_first)

print("\n--- Asignaciones por empleado (mejor solución aleatoria) ---")
print(random_table)
print(best_score)

print("\n--- Asignaciones por empleado (constructivo) ---")
print(constructive_table)
print(constructive_score)

print("\n--- Asignaciones por empleado (mejor solución con recocido simulado) ---")
print(annealing_table)
print(best_score_annealing)

print("\n--- Asignaciones por empleado (mejor solución con VNS) ---")
print(vns_table)
print(best_score_vns)

print("\n--- Asignaciones por empleado (búsqueda local - best improvement) ---")
print(local_table_best)
print(best_score_local_best)

print("\n--- Asignaciones por empleado (búsqueda local - first improvement) ---")
print(local_table_first)
print(best_score_local_first)

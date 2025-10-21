import time
import pandas as pd
from metodo_constructivo_aleatorio import randomized_solution_desde_archivo
from metodo_constructivo import generar_solucion_desde_archivo
from score import evaluate_solution
from metodo_aleatorio import simulated_annealing_assignments

def solution_to_employee_table(sol, days=("L","Ma","Mi","J","V")) -> pd.DataFrame:
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
            return int(e[1:]) if e and e[0] in ("E","e") else e
        except:
            return e

    employees_sorted = sorted(table.keys(), key=emp_key)
    df = pd.DataFrame([{**{"Employees": emp}, **table[emp]} for emp in employees_sorted])
    return df


archivo = "instances/instance1.json"
N = 1000

# ---------------------------
# 1) ALEATORIO (N corridas)
# ---------------------------
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

# --------------------------------
# 2) CONSTRUCTIVO
# --------------------------------
t1 = time.perf_counter()
constructive_solution, constructive_groups = generar_solucion_desde_archivo(archivo)
constructive_score = evaluate_solution(constructive_solution, archivo)
elapsed_constructive = time.perf_counter() - t1

# --------------------------------
# 3) ALEATORIO CON MUTACIONES
#---------------------------------
t2 = time.perf_counter()
best_solution1, best_score1, trace1 = simulated_annealing_assignments(constructive_solution, constructive_groups, archivo)
elapsed_annealing = time.perf_counter() - t2

# --------------------------------
# 4) RESUMEN COMBINADO EN DATAFRAME
# --------------------------------
summary = pd.DataFrame([
    {
        "method": "randomized",
        "n_runs": N,
        "mean_valid": mean_score[0],
        "mean_pref":  mean_score[1],
        "mean_isolated": mean_score[2],
        "best_valid": best_score[0],
        "best_pref":  best_score[1],
        "best_isolated": best_score[2],
        "total_time_s": elapsed_random,
    },
    {
        "method": "constructive",
        "n_runs": 1,
        "mean_valid": constructive_score[0],
        "mean_pref":  constructive_score[1],
        "mean_isolated": constructive_score[2],
        "best_valid": constructive_score[0],
        "best_pref":  constructive_score[1],
        "best_isolated": constructive_score[2],
        "total_time_s": elapsed_constructive,
    },
    {
        "method": "annealing",
        "n_runs": 1000,
        "mean_valid": best_score1[0],
        "mean_pref":  best_score1[1],
        "mean_isolated": best_score1[2],
        "best_valid": best_score1[0],
        "best_pref":  best_score1[1],
        "best_isolated": best_score1[2],
        "total_time_s": elapsed_annealing,
    }
])

print(summary)


# Tablas de empleados
constructive_solution_table = solution_to_employee_table(constructive_solution)
random_solution_table = solution_to_employee_table(best_solution)
annealing_solution_table = solution_to_employee_table(best_solution1)

print("\n--- Asignaciones por empleado (mejor solución aleatoria) ---")
print(random_solution_table)
print(best_score)

print("\n--- Asignaciones por empleado (constructiovo) ---")
print(constructive_solution_table)
print(constructive_score)

print("\n--- Asignaciones por empleado (mejor solución con recocido simulado) ---")
print(annealing_solution_table)
print(best_score1)

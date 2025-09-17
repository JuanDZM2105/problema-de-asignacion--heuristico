import copy, random
from score import evaluate_solution
import math
import json

salsa = 0

def mutate_solution(sol, days_e, employees_g, group_meeting_days):

    new_sol = copy.deepcopy(sol)

    move_type = random.choice(["desk", "zone", "day"])

    def get_group(emp):
        for g, emps in employees_g.items():
            if emp in emps:
                return g
        return None

    # --- 1) Swap dentro de la misma zona y mismo día
    if move_type == "desk":
        day = random.choice(list(new_sol.keys()))
        zone = random.choice(list(new_sol[day].keys()))
        if len(new_sol[day][zone]) >= 2:
            i1, i2 = random.sample(range(len(new_sol[day][zone])), 2)
            (desk1, emp1), (desk2, emp2) = new_sol[day][zone][i1], new_sol[day][zone][i2]

            g1, g2 = get_group(emp1), get_group(emp2)
            # no tocar si ese día es reunión de alguno de los dos grupos
            if day not in (group_meeting_days.get(g1), group_meeting_days.get(g2)):
                new_sol[day][zone][i1] = (desk1, emp2)
                new_sol[day][zone][i2] = (desk2, emp1)

    # --- 2) Swap entre zonas del mismo día
    elif move_type == "zone":
        day = random.choice(list(new_sol.keys()))
        zones = list(new_sol[day].keys())
        if len(zones) >= 2:
            z1, z2 = random.sample(zones, 2)
            if new_sol[day][z1] and new_sol[day][z2]:
                i1 = random.randrange(len(new_sol[day][z1]))
                i2 = random.randrange(len(new_sol[day][z2]))
                desk1, emp1 = new_sol[day][z1][i1]
                desk2, emp2 = new_sol[day][z2][i2]

                g1, g2 = get_group(emp1), get_group(emp2)
                if day not in (group_meeting_days.get(g1), group_meeting_days.get(g2)):
                    new_sol[day][z1][i1] = (desk1, emp2)
                    new_sol[day][z2][i2] = (desk2, emp1)

    # --- 3) Swap entre días distintos
    elif move_type == "day":
        d1, d2 = random.sample(list(new_sol.keys()), 2)
        z1 = random.choice(list(new_sol[d1].keys()))
        z2 = random.choice(list(new_sol[d2].keys()))
        if new_sol[d1][z1] and new_sol[d2][z2]:
            i1 = random.randrange(len(new_sol[d1][z1]))
            i2 = random.randrange(len(new_sol[d2][z2]))
            desk1, emp1 = new_sol[d1][z1][i1]
            desk2, emp2 = new_sol[d2][z2][i2]

            g1, g2 = get_group(emp1), get_group(emp2)
            # si alguno de los días es reunión de alguno de los dos grupos → cancelar
            if d1 not in (group_meeting_days.get(g1), group_meeting_days.get(g2)) and \
               d2 not in (group_meeting_days.get(g1), group_meeting_days.get(g2)):
                # además, que no genere duplicados en los días del empleado
                if d2 not in days_e[emp1] and d1 not in days_e[emp2]:
                    new_sol[d1][z1][i1] = (desk1, emp2)
                    new_sol[d2][z2][i2] = (desk2, emp1)

    return new_sol

def lexicographic_delta(score_new, score_old):
    # score = (asignaciones, preferencias, aislados)
    w = [10*6, 10*3, 1]  # pesos grandes para mantener la prioridad
    val_new = sum(s * w[i] for i, s in enumerate(score_new))
    val_old = sum(s * w[i] for i, s in enumerate(score_old))
    return val_new - val_old

def simulated_annealing_assignments(initial_solution, group_meeting_days, path_json, iterations=1000, T_init=1.0, cooling_rate=0.99):
    with open(path_json, "r", encoding="utf-8") as f:
        instance = json.load(f)

    days_e      = instance["Days_E"]
    employees_g = instance["Employees_G"]

    current_solution = copy.deepcopy(initial_solution)
    best_solution = current_solution

    current_score = evaluate_solution(current_solution, path_json)
    best_score = current_score

    trace = [current_score]
    T = T_init

    for _ in range(iterations):
        # 1. Mutar la solución actual
        mutated_solution = mutate_solution(current_solution, days_e, employees_g, group_meeting_days)
        mutated_score = evaluate_solution(mutated_solution, path_json)

        # 2. Diferencia (usamos comparaciones lexicográficas)
        delta = lexicographic_delta(mutated_score, current_score)

        # 3. Aceptación
        if mutated_score < current_score:  # mejora lexicográfica
            current_solution = mutated_solution
            current_score = mutated_score
            if current_score < best_score:
                best_solution = copy.deepcopy(current_solution)
                best_score = current_score
            trace.append(current_score)
        elif random.random() < math.exp(-delta / T):
            current_solution = mutated_solution
            current_score = mutated_score
            trace.append(current_score)

        # 4. Enfriar temperatura
        T *= cooling_rate

    return best_solution, best_score, trace

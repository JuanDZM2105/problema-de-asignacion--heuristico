import copy, random, json
from score import evaluate_solution

# =============================
# FUNCIONES AUXILIARES
# =============================

def mutate_solution_vns(sol, days_e, employees_g, group_meeting_days, neighborhood_type):
    """
    Muta la solución según el tipo de vecindario.
    - neighborhood_type = 1 → swap dentro de zona
    - neighborhood_type = 2 → swap entre zonas del mismo día
    - neighborhood_type = 3 → swap entre días distintos
    """
    new_sol = copy.deepcopy(sol)

    def get_group(emp):
        for g, emps in employees_g.items():
            if emp in emps:
                return g
        return None

    # Vecindario 1: swap dentro de una zona
    if neighborhood_type == 1:
        day = random.choice(list(new_sol.keys()))
        zone = random.choice(list(new_sol[day].keys()))
        if len(new_sol[day][zone]) >= 2:
            i1, i2 = random.sample(range(len(new_sol[day][zone])), 2)
            (desk1, emp1), (desk2, emp2) = new_sol[day][zone][i1], new_sol[day][zone][i2]
            g1, g2 = get_group(emp1), get_group(emp2)
            if day not in (group_meeting_days.get(g1), group_meeting_days.get(g2)):
                new_sol[day][zone][i1] = (desk1, emp2)
                new_sol[day][zone][i2] = (desk2, emp1)

    # Vecindario 2: swap entre zonas del mismo día
    elif neighborhood_type == 2:
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

    # Vecindario 3: swap entre días distintos
    elif neighborhood_type == 3:
        d1, d2 = random.sample(list(new_sol.keys()), 2)
        z1 = random.choice(list(new_sol[d1].keys()))
        z2 = random.choice(list(new_sol[d2].keys()))
        if new_sol[d1][z1] and new_sol[d2][z2]:
            i1 = random.randrange(len(new_sol[d1][z1]))
            i2 = random.randrange(len(new_sol[d2][z2]))
            desk1, emp1 = new_sol[d1][z1][i1]
            desk2, emp2 = new_sol[d2][z2][i2]
            g1, g2 = get_group(emp1), get_group(emp2)
            if d1 not in (group_meeting_days.get(g1), group_meeting_days.get(g2)) and \
               d2 not in (group_meeting_days.get(g1), group_meeting_days.get(g2)):
                if d2 not in days_e[emp1] and d1 not in days_e[emp2]:
                    new_sol[d1][z1][i1] = (desk1, emp2)
                    new_sol[d2][z2][i2] = (desk2, emp1)

    return new_sol


def lexicographic_delta(score_new, score_old):
    w = [10*6, 10*3, 1]
    val_new = sum(s * w[i] for i, s in enumerate(score_new))
    val_old = sum(s * w[i] for i, s in enumerate(score_old))
    return val_new - val_old


# =============================
# ALGORITMO VNS
# =============================

def vns_assignments(initial_solution, group_meeting_days, path_json, max_iter=1000, sin_mejora_max=100):
    with open(path_json, "r", encoding="utf-8") as f:
        instance = json.load(f)

    days_e = instance["Days_E"]
    employees_g = instance["Employees_G"]

    current_solution = copy.deepcopy(initial_solution)
    best_solution = copy.deepcopy(initial_solution)

    current_score = evaluate_solution(current_solution, path_json)
    best_score = current_score

    vecindarios = [1, 2, 3]  # tipos de vecindarios
    sin_mejora = 0
    trace = [current_score]

    iter_count = 0
    while iter_count < max_iter and sin_mejora < sin_mejora_max:
        for k in vecindarios:
            iter_count += 1
            # 1. Generar vecino con vecindario k
            neighbor = mutate_solution_vns(current_solution, days_e, employees_g, group_meeting_days, k)
            neighbor_score = evaluate_solution(neighbor, path_json)

            # 2. Comparar lexicográficamente
            delta = lexicographic_delta(neighbor_score, current_score)

            # 3. Aceptar si mejora
            if neighbor_score < current_score:
                current_solution = neighbor
                current_score = neighbor_score
                sin_mejora = 0  # reiniciar contador
                # Si mejora global, guardar
                if neighbor_score < best_score:
                    best_solution = copy.deepcopy(neighbor)
                    best_score = neighbor_score
                trace.append(best_score)
                break  # volver al primer vecindario
            else:
                sin_mejora += 1
        # Si no hubo mejora en ninguno de los vecindarios → continuar loop

    return best_solution, best_score, trace

import copy, random, json
from score import evaluate_solution

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def mutate_solution_vns(sol, days_e, employees_g, group_meeting_days, neighborhood_type, desks_z):
    """
    Muta la solución según el tipo de vecindario.
    - neighborhood_type = 1 → swap dentro de zona
    - neighborhood_type = 2 → swap entre zonas del mismo día
    - neighborhood_type = 3 → mover día libre
    - neighborhood_type = 4 → reubicar aislado
    - neighborhood_type = 5 → reasignar zona completa (nuevo)
    """
    new_sol = copy.deepcopy(sol)
 
    def get_group(emp):
        for g, emps in employees_g.items():
            if emp in emps:
                return g
        return None
 
    # =====================================================
    # Vecindario 1: SWAP DENTRO DE LA MISMA ZONA
    # =====================================================
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
 
    # =====================================================
    # Vecindario 2: SWAP ENTRE ZONAS DEL MISMO DÍA
    # =====================================================
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
 
    # =====================================================
    # Vecindario 3: MOVER DÍA LIBRE (temporal)
    # =====================================================
    elif neighborhood_type == 3:
        all_emps = list(days_e.keys())
        emp = random.choice(all_emps)
        g = get_group(emp)
        meeting_day = group_meeting_days.get(g)
 
        current_days = [
            d for d in new_sol.keys()
            if d != meeting_day and any(emp == e for z in new_sol[d].values() for _, e in z)
        ]
        if not current_days:
            return new_sol
 
        day_from = random.choice(current_days)
        available_days = [
            d for d in days_e[emp]
            if d not in current_days and d != meeting_day
        ]
        if not available_days:
            return new_sol
 
        day_to = random.choice(available_days)
        zones = list(new_sol[day_to].keys())
        if not zones:
            return new_sol
        target_zone = random.choice(zones)
        if not new_sol[day_to][target_zone]:
            return new_sol
 
        i_target = random.randrange(len(new_sol[day_to][target_zone]))
        desk_target, emp_target = new_sol[day_to][target_zone][i_target]
        for z_name, z_data in new_sol[day_from].items():
            for idx, (desk, e) in enumerate(z_data):
                if e == emp:
                    g2 = get_group(emp_target)
                    if day_to not in (group_meeting_days.get(g), group_meeting_days.get(g2)):
                        new_sol[day_from][z_name][idx] = (desk, emp_target)
                        new_sol[day_to][target_zone][i_target] = (desk_target, emp)
                    return new_sol
 
    # =====================================================
    # Vecindario 4: REUBICAR AISLADO
    # =====================================================
    elif neighborhood_type == 4:
        day = random.choice(list(new_sol.keys()))
        zones = list(new_sol[day].keys())
        if not zones:
            return new_sol
 
        # Detectar empleados aislados
        isolated_emps = []
        for zone in zones:
            for _, emp in new_sol[day][zone]:
                g = get_group(emp)
                if not g:
                    continue
                same_group = [e for _, e in new_sol[day][zone] if get_group(e) == g and e != emp]
                if not same_group:
                    isolated_emps.append((day, zone, emp))
 
        if not isolated_emps:
            return new_sol
 
        day, zone_from, emp_iso = random.choice(isolated_emps)
        g = get_group(emp_iso)
 
        # Buscar la zona con más miembros del mismo grupo
        best_zone = None
        best_count = 0
        for z in zones:
            count = sum(1 for _, e in new_sol[day][z] if get_group(e) == g)
            if count > best_count and z != zone_from:
                best_zone = z
                best_count = count
 
        if best_zone:
            for i, (desk, e) in enumerate(new_sol[day][zone_from]):
                if e == emp_iso:
                    desk_from = desk
                    del new_sol[day][zone_from][i]
                    break
            if new_sol[day][best_zone]:
                i_target = random.randrange(len(new_sol[day][best_zone]))
                desk_target, emp_target = new_sol[day][best_zone][i_target]
                g2 = get_group(emp_target)
                if day not in (group_meeting_days.get(g), group_meeting_days.get(g2)):
                    new_sol[day][best_zone].insert(i_target, (desk_target, emp_iso))
            else:
                new_sol[day][best_zone].append((desk_from, emp_iso))
 
    # =====================================================
    # Vecindario 5: REASIGNAR ZONA COMPLETA (NUEVO)
    # =====================================================
    elif neighborhood_type == 5:
        if desks_z is None:
            return new_sol  # se requiere información de escritorios por zona
 
        day = random.choice(list(new_sol.keys()))
        zones = list(new_sol[day].keys())
        groups = list(employees_g.keys())
        if not zones or not groups:
            return new_sol
 
        # Escoger grupo al azar
        g = random.choice(groups)
 
        # Obtener empleados del grupo en ese día
        emps_grupo = [
            emp for z in zones for _, emp in new_sol[day][z]
            if get_group(emp) == g
        ]
        if not emps_grupo:
            return new_sol  # el grupo no está presente este día
 
        # Calcular escritorios ocupados
        ocupados = [desk for zonas in new_sol[day].values() for desk, _ in zonas]
        tamaño_grupo = len(emps_grupo)
 
        # Buscar una zona destino con capacidad suficiente
        zonas_posibles = [z for z in zones if len([d for d in desks_z[z] if d not in ocupados]) >= tamaño_grupo]
        if not zonas_posibles:
            return new_sol
 
        zone_dest = random.choice(zonas_posibles)
        # Quitar grupo de su(s) zona(s)
        for z in zones:
            new_sol[day][z] = [(desk, emp) for desk, emp in new_sol[day][z] if get_group(emp) != g]
 
        # Asignar nuevos escritorios en la zona destino
        libres = [d for d in desks_z[zone_dest] if d not in ocupados][:tamaño_grupo]
        for d, emp in zip(libres, emps_grupo):
            new_sol[day][zone_dest].append((d, emp))

    # =====================================================
    # Vecindario 6: REASIGNAR SEGÚN PREFERENCIAS
    # =====================================================
    elif neighborhood_type == 6:
        if desks_z is None:
            return new_sol
 
        # Escoger empleado aleatoriamente
        all_emps = list(days_e.keys())
        emp = random.choice(all_emps)
        g = get_group(emp)
        if not g:
            return new_sol
        meeting_day = group_meeting_days.get(g)
 
        # Encontrar el día actual donde está asignado
        current_day = None
        current_zone = None
        for d, zonas in new_sol.items():
            for z_name, z_data in zonas.items():
                for i, (desk, e) in enumerate(z_data):
                    if e == emp:
                        current_day = d
                        current_zone = z_name
                        idx_emp = i
                        break
                if current_day:
                    break
            if current_day:
                break
 
        if not current_day:
            return new_sol  # no encontrado
 
        # Si ya está en un día de su preferencia, no hacemos nada
        if current_day in days_e.get(emp, []):
            return new_sol
 
        # Buscar un día alternativo que esté en sus preferencias
        preferidos = [d for d in days_e.get(emp, []) if d != meeting_day]
        if not preferidos:
            return new_sol
 
        day_to = random.choice(preferidos)
 
        # Buscar zona destino con cupo
        zonas_dest = list(new_sol[day_to].keys())
        ocupados = [desk for zonas in new_sol[day_to].values() for desk, _ in zonas]
        zonas_libres = [
            z for z in zonas_dest if any(d not in ocupados for d in desks_z[z])
        ]
        if not zonas_libres:
            return new_sol
 
        zone_to = random.choice(zonas_libres)
        libres = [d for d in desks_z[zone_to] if d not in ocupados]
        if not libres:
            return new_sol
 
        nuevo_desk = random.choice(libres)
 
        # Eliminar del día actual
        del new_sol[current_day][current_zone][idx_emp]
 
        # Insertar en el nuevo día / zona
        new_sol[day_to][zone_to].append((nuevo_desk, emp))
 
        return new_sol
    return new_sol

# ==============================================================
# BUSQUEDA LOCAL
# ==============================================================

def local_search_vns(sol_inicial, days_e, employees_g, group_meeting_days, k, desk_z, path_json, max_intentos=1000):
    """
    Realiza búsqueda local en el vecindario k.
    Genera múltiples mutaciones del mismo tipo (vecindario k)
    hasta que no encuentre mejoras.
    """
    sol_actual = copy.deepcopy(sol_inicial)
    score_actual = evaluate_solution(sol_actual, path_json)

    mejora = True
    while mejora:
        mejora = False
        for _ in range(max_intentos):
            vecino = mutate_solution_vns(sol_actual, days_e, employees_g, group_meeting_days, k, desk_z)
            score_vecino = evaluate_solution(vecino, path_json)

            # Mejora lexicográfica o directa
            if score_vecino < score_actual:
                sol_actual = vecino
                score_actual = score_vecino
                mejora = True
                break  # usamos first-improvement (más eficiente)

    return sol_actual, score_actual


# ==============================================================
# ALGORITMO VNS (con búsqueda local dentro de cada vecindario)
# ==============================================================

def vns_assignments(initial_solution, group_meeting_days, path_json, max_iter=100000, sin_mejora_max=1000):
    """
    Variable Neighborhood Search (VNS) con búsqueda local en cada vecindario.

    Vecindarios:
      N1: swap dentro de zona
      N2: swap entre zonas del mismo día
      N3: mover día libre
    """
    with open(path_json, "r", encoding="utf-8") as f:
        instance = json.load(f)

    days_e = instance["Days_E"]
    employees_g = instance["Employees_G"]
    desks_z = instance["Desks_Z"]

    current_solution = copy.deepcopy(initial_solution)
    best_solution = copy.deepcopy(initial_solution)

    current_score = evaluate_solution(current_solution, path_json)
    best_score = current_score

    vecindarios = [1, 2, 3, 4, 5, 6]
    sin_mejora = 0
    trace = [current_score]
    iter_count = 0

    while iter_count < max_iter and sin_mejora < sin_mejora_max:
        for k in vecindarios:
            iter_count += 1
            print(iter_count)

            # 1️⃣ SHAKING — muta solución actual para escapar de óptimos
            neighbor = mutate_solution_vns(current_solution, days_e, employees_g, group_meeting_days, k, desks_z)

            # 2️⃣ BÚSQUEDA LOCAL — mejora dentro del mismo vecindario
            neighbor, neighbor_score = local_search_vns(
                neighbor, days_e, employees_g, group_meeting_days, k, desks_z, path_json
            )

            # 3️⃣ EVALUACIÓN Y ACTUALIZACIÓN
            if neighbor_score < current_score:
                print(f"Iter {iter_count}: Mejora en vecindario {k} de {current_score} a {neighbor_score}")
                current_solution = neighbor
                current_score = neighbor_score
                sin_mejora = 0  # reiniciar contador

                # Mejor global
                if neighbor_score < best_score:
                    best_solution = copy.deepcopy(neighbor)
                    best_score = neighbor_score

                trace.append(best_score)
                break  # volver al primer vecindario
            else:
                sin_mejora += 1

    return best_solution, best_score, trace

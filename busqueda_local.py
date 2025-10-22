import copy
from score import evaluate_solution
from metodo_constructivo import generar_solucion_desde_archivo as generar_solucion
from metodo_constructivo_aleatorio import randomized_solution_desde_archivo as generar_solucion_aleatoria
from metodo_constructivo import build_employee_to_group

def evaluar(sol, instance_path):
    v1, v2, v3 = evaluate_solution(sol, instance_path)
    return v1 * 100 + v2 * 10 + v3

def intercambiar_escritorios(sol, day, zone, i, j):
    """Intercambia escritorios entre dos empleados del mismo día y zona."""
    desk_i, emp_i = sol[day][zone][i]
    desk_j, emp_j = sol[day][zone][j]
    sol[day][zone][i] = (desk_j, emp_i)
    sol[day][zone][j] = (desk_i, emp_j)

def intercambiar_entre_zonas_mismo_grupo(sol, day, zone_a, zone_b, idx_a, idx_b, employee_group):
    """
    Intercambia dos empleados del mismo grupo que están en zonas distintas.
    Mantiene el día, respeta la reunión grupal y las demás restricciones.
    """
    desk_a, emp_a = sol[day][zone_a][idx_a]
    desk_b, emp_b = sol[day][zone_b][idx_b]

    # Solo intercambia si pertenecen al mismo grupo
    if employee_group.get(emp_a) == employee_group.get(emp_b):
        sol[day][zone_a][idx_a] = (desk_b, emp_a)
        sol[day][zone_b][idx_b] = (desk_a, emp_b)
        return True
    return False

def intercambiar_empleados_mismo_dia(sol, day, zone_a, idx_a, zone_b, idx_b):
    """
    Intercambia dos empleados cualquiera del mismo día (pueden ser de distintas zonas o grupos).
    """
    desk_a, emp_a = sol[day][zone_a][idx_a]
    desk_b, emp_b = sol[day][zone_b][idx_b]

    # Intercambiar escritorios y empleados
    sol[day][zone_a][idx_a] = (desk_b, emp_a)
    sol[day][zone_b][idx_b] = (desk_a, emp_b)


def mover_empleado_de_dia(sol, day_from, zone_from, idx_emp, day_to, desks_z, employee_group, groups_days):
    """
    Mueve un empleado de un día a otro (vecindario general).
    ✅ No se permite mover a alguien fuera del día de su grupo.
    ✅ Se requiere capacidad en el nuevo día.
    """
    desk_from, emp = sol[day_from][zone_from][idx_emp]
    grupo = employee_group[emp]

    # 🚫 No mover si está en su día de grupo
    if day_from == groups_days.get(grupo):
        return False

    # Buscar escritorio libre en el día destino
    ocupados = [desk for zonas in sol[day_to].values() for desk, _ in zonas]
    for zone_dest, desks in desks_z.items():
        libres = [d for d in desks if d not in ocupados]
        if libres:
            nuevo_desk = libres[0]
            sol[day_from][zone_from].pop(idx_emp)
            sol[day_to][zone_dest].append((nuevo_desk, emp))
            return True
    return False

def local_search(instance_path, instance, tipo="best"):
    """
    Búsqueda local con vecindario general:
    🔹 Permite mover empleados entre días (excepto su día de grupo).
    🔹 Cumple todas las restricciones.
    """
    sol_actual, groups_days = generar_solucion(instance_path)
    employee_group = build_employee_to_group(instance["Employees_G"])
    desks_z = instance["Desks_Z"]

    valor_actual = evaluar(sol_actual, instance_path)
    mejora = True
    iteracion = 0

    while mejora:
        mejora = False
        mejor_sol = copy.deepcopy(sol_actual)
        mejor_valor = valor_actual

        days = list(sol_actual.keys())

        for d_from in days:
            for z_from in sol_actual[d_from]:
                lista = sol_actual[d_from][z_from]

                for idx in range(len(lista)):
                    for d_to in days:
                        if d_to == d_from:
                            continue
                        vecina = copy.deepcopy(sol_actual)
                        ok = mover_empleado_de_dia(
                            vecina, d_from, z_from, idx, d_to, desks_z, employee_group, groups_days
                        )
                        if not ok:
                            continue

                        val_vecina = evaluar(vecina, instance_path)

                        if val_vecina < mejor_valor:
                            mejor_valor = val_vecina
                            mejor_sol = vecina
                            mejora = True
                            if tipo == "first":
                                break
                    if mejora and tipo == "first": break
                if mejora and tipo == "first": break
            if mejora and tipo == "first": break
        if mejora:
            sol_actual = mejor_sol
            valor_actual = mejor_valor
            iteracion += 1
            print(f"[{tipo}] Iter {iteracion}: mejora encontrada → {valor_actual}")

    print(f"[{tipo}] Resultado final: {valor_actual}")
    return sol_actual, valor_actual

import json

archivo = "instances/instance10.json"

with open(archivo, "r", encoding="utf-8") as f:
    instance = json.load(f)


sol_best, val_best = local_search(archivo, instance,tipo="best")
sol_first, val_first = local_search(archivo, instance, tipo="first")

print("Best improvement:", val_best)
print("First improvement:", val_first)
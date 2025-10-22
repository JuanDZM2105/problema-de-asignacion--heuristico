import copy
from score import evaluate_solution
from metodo_constructivo import generar_solucion_desde_archivo as generar_solucion
from metodo_constructivo_aleatorio import randomized_solution_desde_archivo as generar_solucion_aleatoria
from metodo_constructivo import build_employee_to_group
import json


def mover_empleado_de_dia(sol, day_from, zone_from, idx_emp, day_to, desks_z, employee_group, groups_days):
    """
    Mueve un empleado de un día a otro (vecindario general).
        No se permite mover a alguien fuera del día de su grupo.
        Se requiere capacidad en el nuevo día.
        Se conserva el requisito de al menos dos días por empleado (después del movimiento).
    """
    desk_from, emp = sol[day_from][zone_from][idx_emp]
    grupo = employee_group[emp]

    if day_from == groups_days.get(grupo):
        return False

    # Contar los días actuales del empleado
    days_assigned = [d for d in sol if any(emp == e for zonas in sol[d].values() for _, e in zonas)]

    if len(days_assigned) <= 1:
        return False

    if day_to in days_assigned:
        return False

    # Buscar escritorio libre en el día destino
    ocupados = [desk for zonas in sol[day_to].values() for desk, _ in zonas]
    for zone_dest, desks in desks_z.items():
        libres = [d for d in desks if d not in ocupados]
        if not libres:
            continue

        # Simular movimiento
        nueva_sol = copy.deepcopy(sol)
        nueva_sol[day_from][zone_from].pop(idx_emp)
        nueva_sol[day_to][zone_dest].append((libres[0], emp))

        # Verificar que el empleado siga teniendo ≥ 2 días después del movimiento
        new_days = [
            d for d in nueva_sol if any(emp == e for zonas in nueva_sol[d].values() for _, e in zonas)
        ]
        if len(new_days) == 2:
            # Movimiento válido
            sol[day_from][zone_from].pop(idx_emp)
            sol[day_to][zone_dest].append((libres[0], emp))
            return True

    return False


def local_search(instance_path, instance, tipo="best"):
    """
    Búsqueda local con vecindario general:
        Permite mover empleados entre días (excepto su día de grupo).
        Conserva mínimo dos días por empleado.
        Cumple las restricciones estructurales.
    """
    sol_actual, groups_days = generar_solucion(instance_path)
    employee_group = build_employee_to_group(instance["Employees_G"])
    desks_z = instance["Desks_Z"]

    valor_actual = evaluate_solution(sol_actual, instance_path)
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

                        val_vecina = evaluate_solution(vecina, instance_path)

                        if val_vecina < mejor_valor:
                            mejor_valor = val_vecina
                            mejor_sol = vecina
                            mejora = True

                            if tipo == "first":
                                break
                    if mejora and tipo == "first":
                        break
                if mejora and tipo == "first":
                    break
            if mejora and tipo == "first":
                break

        if mejora:
            sol_actual = mejor_sol
            valor_actual = mejor_valor
            iteracion += 1
            print(f"[{tipo}] Iter {iteracion}: mejora encontrada → {valor_actual}")

    print(f"[{tipo}] Resultado final: {valor_actual}")
    return sol_actual, valor_actual


# =====================================================
# Ejemplo de ejecución
# =====================================================
archivo = "instances/instance10.json"

with open(archivo, "r", encoding="utf-8") as f:
    instance = json.load(f)

sol_best, val_best = local_search(archivo, instance, tipo="best")
sol_first, val_first = local_search(archivo, instance, tipo="first")

print("Best improvement:", val_best)
print("First improvement:", val_first)
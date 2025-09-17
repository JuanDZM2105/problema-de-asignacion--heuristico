import json

def _emp_to_group(employees_g):
    return {e: g for g, es in employees_g.items() for e in es}

def calculate_valid_assignments(sol, desks_e):
    violations = 0
    for _, zones in sol.items():
        for _, assignments in zones.items():
            for desk, employee in assignments:
                if desk not in (desks_e.get(employee, []) or []):
                    violations += 1
    return violations

def calculate_employee_preferences(sol, days_e):
    violations = 0
    for day, zones in sol.items():
        for _, assignments in zones.items():
            for _, employee in assignments:
                if day not in (days_e.get(employee, []) or []):
                    violations += 1
    return violations

def calculate_isolated_employee(sol, employees_g):
    emp_to_group = _emp_to_group(employees_g)
    violations = 0
    for _, zones in sol.items():
        for _, assignments in zones.items():
            empleados = [emp for _, emp in assignments]
            for emp in empleados:
                g = emp_to_group.get(emp)
                if g is None:   # robustez: ignora empleados sin grupo
                    continue
                count_same = sum(1 for ee in empleados if emp_to_group.get(ee) == g)
                if count_same == 1:
                    violations += 1
    return violations

def evaluate_solution(sol, archivo_json: str):
    """Evalúa la solución cargando la instancia directamente desde archivo."""
    with open(archivo_json, "r", encoding="utf-8") as f:
        instance = json.load(f)

    desks_e = instance["Desks_E"]
    days_e = instance["Days_E"]
    employees_g = instance["Employees_G"]

    return (
        calculate_valid_assignments(sol, desks_e),     # prioridad 1
        calculate_employee_preferences(sol, days_e),   # prioridad 2
        calculate_isolated_employee(sol, employees_g)  # prioridad 3
    )

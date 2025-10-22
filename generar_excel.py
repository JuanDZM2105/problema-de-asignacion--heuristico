import os
import pandas as pd
import json
from metodo_constructivo import generar_solucion_desde_archivo
from metodo_constructivo_aleatorio import randomized_solution_desde_archivo
from metodo_aleatorio import simulated_annealing_assignments
from metodo_vns import vns_assignments
from busqueda_local import local_search  # 🧩 Nuevo import
from score import evaluate_solution


# ======================================================
# FUNCIONES AUXILIARES
# ======================================================

def solution_to_employee_table(sol, days=("L", "Ma", "Mi", "J", "V")) -> pd.DataFrame:
    """Convierte una solución en una tabla por empleado, usando 'None' donde no hay asignación."""
    employees = set()
    for d in sol.values():
        for assigns in d.values():
            for desk, emp in assigns:
                employees.add(emp)

    table = {emp: {day: "None" for day in days} for emp in employees}

    for day, zones in sol.items():
        if day not in days:
            continue
        for _, assignments in zones.items():
            for desk, emp in assignments:
                table[emp][day] = desk if desk is not None else "None"

    def emp_key(e):
        try:
            return int(e[1:]) if e and e[0] in ("E", "e") else e
        except Exception:
            return e

    employees_sorted = sorted(table.keys(), key=emp_key)
    df = pd.DataFrame([{**{"Employees": emp}, **table[emp]} for emp in employees_sorted])
    return df


# ======================================================
# NUEVA FUNCIÓN: CALCULAR RESUMEN DE MÉTRICAS
# ======================================================

def calcular_resumen(sol, instance):
    """Calcula las tres métricas pedidas a partir de la solución y la instancia JSON."""
    desks_e = instance["Desks_E"]
    days_e = instance["Days_E"]
    employees_g = instance["Employees_G"]

    # Crear un mapa inverso empleado→grupo
    emp_to_group = {emp: g for g, emps in employees_g.items() for emp in emps}

    valid_assignments = 0
    pref_assignments = 0
    non_isolated_emps = set()

    # Recorremos todos los días y zonas
    for day, zonas in sol.items():
        for z_name, assignments in zonas.items():
            # Agrupar por grupo para detectar aislamiento
            grupo_por_emp = {}
            for desk, emp in assignments:
                g = emp_to_group.get(emp)
                if not g:
                    continue
                grupo_por_emp.setdefault(g, []).append(emp)

                # Escritorio válido
                if desk in desks_e.get(emp, []):
                    valid_assignments += 1

                # Día preferido
                if day in days_e.get(emp, []):
                    pref_assignments += 1

            # Verificar empleados aislados en esta zona
            for g, emps in grupo_por_emp.items():
                if len(emps) >= 2:
                    non_isolated_emps.update(emps)

    total_isolated = len(non_isolated_emps)

    data = [
        ["Valid assignments", valid_assignments],
        ["Employee preferences", pref_assignments],
        ["Isolated employees", total_isolated],
    ]

    df_summary = pd.DataFrame(data, columns=["Metric", "Value"])
    return df_summary


# ======================================================
# PROCESADOR DE INSTANCIAS
# ======================================================

def procesar_instancia(path_json: str):
    """Dada una instancia (archivo JSON), genera todas las soluciones y devuelve los DataFrames listos para exportar."""
    print(f"\n🔹 Procesando instancia: {path_json}")

    with open(path_json, "r", encoding="utf-8") as f:
        instance = json.load(f)

    days_e = instance["Days_E"]
    employees_g = instance["Employees_G"]
    groups = list(employees_g.keys())

    # =====================================================
    # MÉTODOS HEURÍSTICOS
    # =====================================================
    constructive_solution, constructive_groups = generar_solucion_desde_archivo(path_json)
    randomized_solution, randomized_groups = randomized_solution_desde_archivo(path_json)
    annealing_solution, _, _ = simulated_annealing_assignments(constructive_solution, constructive_groups, path_json)
    vns_solution, _, _ = vns_assignments(constructive_solution, constructive_groups, path_json)

    # =====================================================
    # BÚSQUEDA LOCAL (nuevo)
    # =====================================================
    print("⚙️ Ejecutando búsqueda local (mejor mejora)...")
    local_solution, _ = local_search(path_json, instance, tipo="best")

    # =====================================================
    # CREAR DATAFRAMES DE ASIGNACIÓN
    # =====================================================
    df_constructive = solution_to_employee_table(constructive_solution)
    df_randomized = solution_to_employee_table(randomized_solution)
    df_annealing = solution_to_employee_table(annealing_solution)
    df_vns = solution_to_employee_table(vns_solution)
    df_local = solution_to_employee_table(local_solution)

    # Crear DataFrame de grupos sin encabezado
    df_group_days = pd.DataFrame([[g, constructive_groups.get(g, "None")] for g in groups])

    # =====================================================
    # CREAR DATAFRAMES DE RESUMEN
    # =====================================================
    df_summary_constructive = calcular_resumen(constructive_solution, instance)
    df_summary_randomized = calcular_resumen(randomized_solution, instance)
    df_summary_annealing = calcular_resumen(annealing_solution, instance)
    df_summary_vns = calcular_resumen(vns_solution, instance)
    df_summary_local = calcular_resumen(local_solution, instance)

    resultados = {
        "constructive": {"solution": df_constructive, "summary": df_summary_constructive},
        "randomized": {"solution": df_randomized, "summary": df_summary_randomized},
        "annealing": {"solution": df_annealing, "summary": df_summary_annealing},
        "vns": {"solution": df_vns, "summary": df_summary_vns},
        "local_search": {"solution": df_local, "summary": df_summary_local},
        "group_days": df_group_days,
    }

    return resultados


# ======================================================
# PROCESAR TODAS LAS INSTANCIAS
# ======================================================

def procesar_todas_las_instancias(instances_folder="instances"):
    resultados_globales = {}
    for i in range(1, 11):
        file_path = os.path.join(instances_folder, f"instance{i}.json")
        if not os.path.exists(file_path):
            print(f"⚠️ No se encontró {file_path}")
            continue
        resultados_globales[f"instance{i}"] = procesar_instancia(file_path)
    return resultados_globales


# ======================================================
# GUARDAR EN EXCEL
# ======================================================

def guardar_resultados_en_excel(resultados, output_folder="resultados"):
    os.makedirs(output_folder, exist_ok=True)
    metodos = ["constructive", "randomized", "annealing", "vns", "local_search"]

    for metodo in metodos:
        metodo_dir = os.path.join(output_folder, metodo)
        os.makedirs(metodo_dir, exist_ok=True)

        for instancia, datos in resultados.items():
            if metodo not in datos:
                continue

            df_sol = datos[metodo]["solution"]
            df_summary = datos[metodo]["summary"]
            df_grupos = datos["group_days"]

            file_path = os.path.join(metodo_dir, f"{instancia}.xlsx")
            with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
                df_sol.to_excel(writer, sheet_name="EmployeeAssignment", index=False)
                df_grupos.to_excel(writer, sheet_name="Groups Meeting day", header=False, index=False)
                df_summary.to_excel(writer, sheet_name="Summary", index=False)

            print(f"✅ Guardado: {file_path}")


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":
    print("🚀 Iniciando procesamiento de instancias...\n")
    resultados = procesar_todas_las_instancias()
    print("\n📊 Generando archivos Excel...")
    guardar_resultados_en_excel(resultados)
    print("\n✅ Proceso completado correctamente. Archivos disponibles en la carpeta 'resultados/'.")

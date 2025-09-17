# combined_single_file.py

# =========================
# Imports
# =========================
import json
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
from score import evaluate_solution


# =========================
# segmentar_grupos.py
# =========================
def build_employee_to_group(employees_g: Dict[str, List[str]]) -> Dict[str, str]:
    """Devuelve emp->grupo."""
    return {emp: grp for grp, emps in employees_g.items() for emp in emps}

def count_group_day_prefs(days_e: Dict[str, List[str]],
                          employees_g: Dict[str, List[str]],
                          days: List[str]) -> Dict[str, Dict[str, int]]:
    """Conteo de gustos por grupo y día."""
    gdp = {g: {d: 0 for d in days} for g in employees_g}
    for g, emps in employees_g.items():
        for e in emps:
            for d in days_e.get(e, []):
                if d in gdp[g]:
                    gdp[g][d] += 1
    return gdp

def order_groups_by_peak(gdp: Dict[str, Dict[str, int]]) -> List[str]:
    """Ordena grupos por su pico de demanda (desc)."""
    return sorted(gdp, key=lambda g: max(gdp[g].values()), reverse=True)

def group_size(employees_g: Dict[str, List[str]], g: str) -> int:
    return len(employees_g.get(g, []))


# =========================
# asignar_dias.py
# =========================
def total_desks(desks_z: Dict[str, List[str]]) -> int:
    return sum(len(ds) for ds in desks_z.values())

def assign_group_meeting_days(days: List[str],
                              employees_g: Dict[str, List[str]],
                              days_e: Dict[str, List[str]],
                              desks_z: Dict[str, List[str]]) -> Dict[str, str]:
    """
    Asigna el día de reunión por grupo (greedy determinista).
    Nunca falla: si no cabe en su mejor día, lo pone donde más cupo quede.
    """
    gdp = count_group_day_prefs(days_e, employees_g, days)
    groups_sorted = order_groups_by_peak(gdp)
    day_groups: Dict[str, List[str]] = {d: [] for d in days}
    groups_days: Dict[str, str] = {}
    cap_total = total_desks(desks_z)

    def total_on_day(d: str) -> int:
        return sum(group_size(employees_g, g) for g in day_groups[d])

    for g in groups_sorted:
        pref_days = sorted(days, key=lambda d: gdp[g][d], reverse=True)
        placed = False
        for d in pref_days:
            if total_on_day(d) + group_size(employees_g, g) <= cap_total:
                day_groups[d].append(g)
                groups_days[g] = d
                placed = True
                break
        if not placed:
            # fallback: día con mayor capacidad remanente
            d_best = max(days, key=lambda d: cap_total - total_on_day(d))
            day_groups[d_best].append(g)
            groups_days[g] = d_best

    return groups_days

def residual_capacity_by_day(days: List[str],
                             groups_days: Dict[str, str],
                             employees_g: Dict[str, List[str]],
                             desks_z: Dict[str, List[str]]) -> Dict[str, int]:
    cap_total = total_desks(desks_z)
    return {
        d: cap_total - sum(group_size(employees_g, g) for g, dd in groups_days.items() if dd == d)
        for d in days
    }

def assign_second_day_constructive(prefs: Dict[str, List[str]],
                                   groups_days: Dict[str, str],
                                   employee_group,  # dict o callable emp->grupo
                                   residual_capacity: Dict[str, int],
                                   days_order: Tuple[str, ...],
                                   allow_same_as_group: bool = False):
    """
    Asigna el 2º día por empleado (constructivo, determinista).
    Prioridad: gustos (en orden) -> primer día global con cupo.
    """
    cap = {d: int(residual_capacity.get(d, 0)) for d in days_order}

    def grp(e: str) -> str:
        return employee_group[e] if isinstance(employee_group, dict) else employee_group(e)

    second_day: Dict[str, str] = {}
    satisfechos = 0

    for e in prefs:  # orden de inserción del dict
        gday = groups_days[grp(e)]
        liked = [d for d in (prefs.get(e, []) or []) if allow_same_as_group or d != gday]

        asignado = next((d for d in liked if d in days_order and cap.get(d, 0) > 0), None)
        if asignado is None:
            asignado = next((d for d in days_order if (allow_same_as_group or d != gday) and cap.get(d, 0) > 0), None)

        if asignado is None:
            # si la capacidad residual total < empleados, no alcanzan sillas; de todas formas devolvemos parcial
            continue

        second_day[e] = asignado
        cap[asignado] -= 1
        if asignado in (prefs.get(e, []) or []):
            satisfechos += 1

    stats = {
        "satisfechos_segundo_dia": satisfechos,
        "ocupacion_segundo": dict(Counter(second_day.values())),
        "capacidad_restante": cap,
    }
    return second_day, stats

def build_schedule_by_day(prefs: Dict[str, List[str]],
                          groups_days: Dict[str, str],
                          employee_group,
                          second_day: Dict[str, str],
                          days: List[str]):
    """Devuelve (total, reunion, segundo) por día."""
    schedule_total   = {d: [] for d in days}
    schedule_reunion = {d: [] for d in days}
    schedule_second  = {d: [] for d in days}

    for e in prefs:
        g = employee_group[e] if isinstance(employee_group, dict) else employee_group(e)
        gday = groups_days[g]
        schedule_reunion[gday].append(e)
        schedule_total[gday].append(e)

        d2 = second_day.get(e)
        if d2 and d2 != gday:
            schedule_second[d2].append(e)
            schedule_total[d2].append(e)

    return schedule_total, schedule_reunion, schedule_second


# =========================
# asignar_puestos.py
# =========================
def build_zone_of(desks_z: Dict[str, List[str]]) -> Dict[str, str]:
    return {desk: z for z, ds in desks_z.items() for desk in ds}

def seat_day_constructive(employees_day: List[str],
                          desks_e: Dict[str, List[str]],
                          desks_z: Dict[str, List[str]],
                          employee_group,                 # dict o callable emp->grupo
                          zones_order: Tuple[str, ...],   # p.ej. ('Z0','Z1')
                          zone_of: Dict[str, str]) -> Dict[str, str]:
    """
    Sienta a todos si hay sillas suficientes globalmente.
    Prioriza: gusto en su zona -> gusto en otra zona -> cualquier en su zona -> cualquier en otra.
    Sin errores por “aislados”; tú lo puntúas después.
    """
    # Fase A: reparto deseado por grupo (evitando singletons cuando se pueda), sin abortar
    groups_today = defaultdict(list)
    for e in employees_day:
        g = employee_group[e] if isinstance(employee_group, dict) else employee_group(e)
        groups_today[g].append(e)

    cap_rem = {z: len(desks_z[z]) for z in zones_order}
    per_group_zone_count = {g: {z: 0 for z in zones_order} for g in groups_today}

    def best_zone():
        return max(zones_order, key=lambda z: (cap_rem[z], -int(z != zones_order[0])))

    for g in sorted(groups_today.keys()):
        k = len(groups_today[g])
        blocks = [1] if k == 1 else ([3] + [2]*((k-3)//2) if k % 2 else [2]*(k//2))
        for b in blocks:
            z = best_zone()
            zz = zones_order[1] if z == zones_order[0] else zones_order[0]
            if cap_rem[z] >= b:
                per_group_zone_count[g][z] += b; cap_rem[z] -= b
            elif cap_rem[zz] >= b:
                per_group_zone_count[g][zz] += b; cap_rem[zz] -= b
            else:
                # degradación suave (partir bloques sin abortar)
                need = b
                for ztry in (z, zz):
                    take = min(cap_rem[ztry], need)
                    if take:
                        per_group_zone_count[g][ztry] += take
                        cap_rem[ztry] -= take
                        need -= take

    # Fase B: elegir quién va a cada zona
    emp_zone_target = {}
    for g in sorted(groups_today.keys()):
        Es = groups_today[g]
        idx = 0
        for z in zones_order:
            cnt = per_group_zone_count[g][z]
            for _ in range(cnt):
                if idx < len(Es):
                    emp_zone_target[Es[idx]] = z
                    idx += 1
        while idx < len(Es):
            zf = best_zone()
            emp_zone_target[Es[idx]] = zf
            cap_rem[zf] = max(0, cap_rem[zf]-1)
            idx += 1

    # Fase C: asignar escritorios (gustos priorizados)
    desk_taken = set()
    assignment: Dict[str, str] = {}

    for z in zones_order:
        Ez = [e for e in employees_day if emp_zone_target.get(e) == z]
        for e in Ez:
            liked = desks_e.get(e, [])
            chosen = None
            # 1) gusto en su zona
            for d in liked:
                if d not in desk_taken and zone_of.get(d) == z:
                    chosen = d; break
            # 2) gusto en otra zona
            if chosen is None:
                for d in liked:
                    if d not in desk_taken and zone_of.get(d) in zones_order and zone_of.get(d) != z:
                        chosen = d; break
            # 3) cualquiera en su zona
            if chosen is None:
                for d in desks_z[z]:
                    if d not in desk_taken:
                        chosen = d; break
            # 4) cualquiera en otra zona
            if chosen is None:
                for zz in zones_order:
                    for d in desks_z[zz]:
                        if d not in desk_taken:
                            chosen = d; break
                    if chosen: break
            if chosen is None:
                # sin sillas globales; dejamos sin asignar (tú lo manejas fuera si quieres)
                continue
            assignment[e] = chosen
            desk_taken.add(chosen)

    return assignment


# =========================
# crear_solucion.py
# =========================
def crear_solucion(days: List[str],
                   schedule_total: Dict[str, List[str]],
                   desks_e: Dict[str, List[str]],
                   desks_z: Dict[str, List[str]],
                   employee_group,
                   zones_order: Tuple[str, ...]) -> Dict[str, Dict[str, List[Tuple[str, str]]]]:
    """
    Devuelve:
    { 'L': {'Z0': [(desk,emp),...], 'Z1': [...]}, 'MA': {...}, 'MI': {...}, 'J': {...}, 'V': {...} }
    """
    zone_of = build_zone_of(desks_z)
    solucion = {d: {z: [] for z in desks_z.keys()} for d in days}

    for d in days:
        empleados = list(schedule_total[d])  # conserva orden
        assignment = seat_day_constructive(
            employees_day=empleados,
            desks_e=desks_e,
            desks_z=desks_z,
            employee_group=employee_group,
            zones_order=zones_order,
            zone_of=zone_of
        )

        # Fallback: si faltó alguien, dale cualquier desk
        usados = set(assignment.values())
        for e in empleados:
            if e not in assignment:
                # gusto libre en cualquier zona
                pick = next((dd for dd in (desks_e.get(e, []) or []) if dd in zone_of and dd not in usados), None)
                if pick is None:
                    # cualquier libre
                    for z, ds in desks_z.items():
                        pick = next((dd for dd in ds if dd not in usados), None)
                        if pick: break
                if pick is None:
                    # sin sillas globales; continúa (quedará sin asignar)
                    continue
                assignment[e] = pick
                usados.add(pick)

        dkey = d
        for e in empleados:
            if e in assignment:
                desk = assignment[e]
                z = zone_of[desk]
                solucion[dkey][z].append((desk, e))

    return solucion


def generar_solucion(instance: Dict) -> Dict[str, Dict[str, List[Tuple[str, str]]]]:
    """
    Orquesta todo y devuelve 'solucion' lista para usar.
    """
    Days        = instance["Days"]
    Zones       = tuple(instance["Zones"])
    Desks_Z     = instance["Desks_Z"]
    Days_E      = instance["Days_E"]
    Desks_E     = instance["Desks_E"]
    Employees_G = instance["Employees_G"]

    EMP_TO_G = build_employee_to_group(Employees_G)

    groups_days = assign_group_meeting_days(Days, Employees_G, Days_E, Desks_Z)
    days_desks  = residual_capacity_by_day(Days, groups_days, Employees_G, Desks_Z)

    second_day, _ = assign_second_day_constructive(
        prefs=Days_E,
        groups_days=groups_days,
        employee_group=EMP_TO_G,
        residual_capacity=days_desks,
        days_order=tuple(Days),
        allow_same_as_group=False
    )

    schedule_total, _, _ = build_schedule_by_day(
        prefs=Days_E,
        groups_days=groups_days,
        employee_group=EMP_TO_G,
        second_day=second_day,
        days=Days
    )

    solucion = crear_solucion(
        days=Days,
        schedule_total=schedule_total,
        desks_e=Desks_E,
        desks_z=Desks_Z,
        employee_group=EMP_TO_G,
        zones_order=Zones
    )
    return solucion, groups_days

def generar_solucion_desde_archivo(path_json: str):
    with open(path_json, "r", encoding="utf-8") as f:
        inst = json.load(f)
    return generar_solucion(inst)
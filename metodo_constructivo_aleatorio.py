import random
from typing import Dict, List, Tuple
import json
import json, argparse, secrets
from score import evaluate_solution

# ---------------------------
# 1) Día de reunión por grupo
# ---------------------------
def rand_assign_group_meeting_days(
    days: List[str],
    employees_g: Dict[str, List[str]],
    days_e: Dict[str, List[str]],
    desks_z: Dict[str, List[str]],
    seed: int = 0,
) -> Dict[str, str]:
    rng = random.Random(seed)
    cap_total = sum(len(ds) for ds in desks_z.values())

    # gustos grupo-día
    gdp = {g: {d: 0 for d in days} for g in employees_g}
    for g, emps in employees_g.items():
        for e in emps:
            for d in days_e.get(e, []):
                if d in gdp[g]:
                    gdp[g][d] += 1

    # ordenar grupos por pico; empates aleatorios
    peak = {g: max(gdp[g].values()) for g in employees_g}
    groups = list(employees_g.keys())
    groups.sort(key=lambda g: peak[g], reverse=True)
    i = 0
    while i < len(groups):
        j = i
        while j < len(groups) and peak[groups[j]] == peak[groups[i]]:
            j += 1
        rng.shuffle(groups[i:j])
        i = j

    day_groups: Dict[str, List[str]] = {d: [] for d in days}
    groups_days: Dict[str, str] = {}

    def total_on_day(d: str) -> int:
        return sum(len(employees_g[g]) for g in day_groups[d])

    for g in groups:
        # ordenar días por gusto; empates aleatorios
        buckets = {}
        for d in days:
            buckets.setdefault(gdp[g][d], []).append(d)
        pref_days = []
        for val in sorted(buckets.keys(), reverse=True):
            dd = buckets[val]
            rng.shuffle(dd)
            pref_days.extend(dd)

        placed = False
        for d in pref_days:
            if total_on_day(d) + len(employees_g[g]) <= cap_total:
                day_groups[d].append(g)
                groups_days[g] = d
                placed = True
                break
        if not placed:
            # fallback: día con mayor remanente (empates aleatorios)
            best_cap = -1
            best_days = []
            for d in days:
                rem = cap_total - total_on_day(d)
                if rem > best_cap:
                    best_cap = rem; best_days = [d]
                elif rem == best_cap:
                    best_days.append(d)
            d_pick = rng.choice(best_days)
            day_groups[d_pick].append(g)
            groups_days[g] = d_pick

    return groups_days

# ------------------------------------
# 2) Segundo día por empleado (random)
# ------------------------------------
def rand_assign_second_day_constructive(
    prefs: Dict[str, List[str]],
    groups_days: Dict[str, str],
    employee_group,                  # dict o callable emp->grupo
    residual_capacity: Dict[str, int],
    days_order: Tuple[str, ...],
    allow_same_as_group: bool = False,
    seed: int = 0,
):
    rng = random.Random(seed)
    cap = {d: int(residual_capacity.get(d, 0)) for d in days_order}

    order = list(prefs.keys())
    rng.shuffle(order)

    def grp(e): return employee_group[e] if isinstance(employee_group, dict) else employee_group(e)

    second_day: Dict[str, str] = {}
    for e in order:
        gday = groups_days[grp(e)]
        liked = [d for d in (prefs.get(e, []) or []) if allow_same_as_group or d != gday]

        liked_ok = [d for d in liked if d in days_order and cap.get(d, 0) > 0]
        asignado = rng.choice(liked_ok) if liked_ok else None

        if asignado is None:
            cand = [d for d in days_order if (allow_same_as_group or d != gday) and cap.get(d, 0) > 0]
            asignado = rng.choice(cand) if cand else None

        if asignado is None:
            continue  # no hay cupo residual global suficiente

        second_day[e] = asignado
        cap[asignado] -= 1

    return second_day

# ---------------------------------------
# 3) Asignar escritorios por día (random)
# ---------------------------------------
def rand_seat_day_constructive(
    employees_day: List[str],
    desks_e: Dict[str, List[str]],
    desks_z: Dict[str, List[str]],
    employee_group,                 # dict o callable
    zones_order: Tuple[str, ...],   # ('Z0','Z1')
    seed: int = 0,
) -> Dict[str, str]:
    rng = random.Random(seed)
    zone_of = {desk: z for z, ds in desks_z.items() for desk in ds}

    # grupos presentes
    from collections import defaultdict
    groups_today = defaultdict(list)
    for e in employees_day:
        g = employee_group[e] if isinstance(employee_group, dict) else employee_group(e)
        groups_today[g].append(e)

    # reparto por grupo-zona (bloques) con empates aleatorios, sin abortar
    cap_rem = {z: len(desks_z[z]) for z in zones_order}
    per_group_zone_count = {g: {z: 0 for z in zones_order} for g in groups_today}

    def zones_by_cap_random():
        # zonas ordenadas desc por cap; empates al azar
        caps = {}
        for z in zones_order:
            caps.setdefault(cap_rem[z], []).append(z)
        res = []
        for c in sorted(caps.keys(), reverse=True):
            zz = caps[c]; rng.shuffle(zz); res.extend(zz)
        return res

    for g in sorted(groups_today.keys()):
        k = len(groups_today[g])
        blocks = [1] if k == 1 else ([3] + [2]*((k-3)//2) if k % 2 else [2]*(k//2))
        for b in blocks:
            placed = False
            for z in zones_by_cap_random():
                if cap_rem[z] >= b:
                    per_group_zone_count[g][z] += b; cap_rem[z] -= b
                    placed = True
                    break
            if not placed:
                need = b
                zz = list(zones_order); rng.shuffle(zz)
                for z in zz:
                    take = min(cap_rem[z], need)
                    if take:
                        per_group_zone_count[g][z] += take; cap_rem[z] -= take; need -= take
                    if need == 0:
                        break
                # si aún queda need>0, no hay sillas globales; se intentará en la fase final

    # quién va a cada zona (aleatorio dentro del grupo)
    emp_zone_target = {}
    for g in sorted(groups_today.keys()):
        Es = list(groups_today[g]); rng.shuffle(Es)
        idx = 0
        for z in zones_order:
            cnt = per_group_zone_count[g][z]
            for _ in range(cnt):
                if idx < len(Es):
                    emp_zone_target[Es[idx]] = z; idx += 1
        while idx < len(Es):
            zbest = zones_by_cap_random()[0]
            emp_zone_target[Es[idx]] = zbest
            cap_rem[zbest] = max(0, cap_rem[zbest]-1)
            idx += 1

    # asignar escritorios
    desk_taken = set()
    assignment: Dict[str, str] = {}

    for z in zones_order:
        Ez = [e for e in employees_day if emp_zone_target.get(e) == z]
        rng.shuffle(Ez)
        for e in Ez:
            liked = desks_e.get(e, []) or []
            # 1) gusto en su zona
            liked_in_zone = [d for d in liked if d not in desk_taken and zone_of.get(d) == z]
            rng.shuffle(liked_in_zone)
            chosen = liked_in_zone[0] if liked_in_zone else None
            # 2) gusto en otra zona
            if chosen is None:
                liked_any = [d for d in liked if d not in desk_taken and zone_of.get(d) in zones_order]
                rng.shuffle(liked_any)
                chosen = liked_any[0] if liked_any else None
            # 3) cualquiera en su zona
            if chosen is None:
                free_here = [d for d in desks_z[z] if d not in desk_taken]
                rng.shuffle(free_here)
                chosen = free_here[0] if free_here else None
            # 4) cualquiera en otra zona
            if chosen is None:
                all_free = [d for zz in zones_order for d in desks_z[zz] if d not in desk_taken]
                rng.shuffle(all_free)
                chosen = all_free[0] if all_free else None

            if chosen is None:
                continue  # sin sillas globales

            assignment[e] = chosen
            desk_taken.add(chosen)

    return assignment

# ----------------------------
# 4) Construir la SOLUCIÓN final
# ----------------------------
def crear_solucion_random(
    days: List[str],
    schedule_total: Dict[str, List[str]],
    desks_e: Dict[str, List[str]],
    desks_z: Dict[str, List[str]],
    employee_group,
    zones_order: Tuple[str, ...],
    seat_fn,                 # inyecta rand_seat_day_constructive
    seed: int = 0,
) -> Dict[str, Dict[str, List[Tuple[str, str]]]]:
    rng = random.Random(seed)
    zone_of = {desk: z for z, ds in desks_z.items() for desk in ds}
    solucion = {d: {z: [] for z in desks_z.keys()} for d in days}

    for d in days:
        empleados = list(schedule_total[d])
        assignment = seat_fn(
            employees_day=empleados,
            desks_e=desks_e,
            desks_z=desks_z,
            employee_group=employee_group,
            zones_order=zones_order,
            seed=rng.randrange(10**9),
        )

        # fallback: quien falte, gusto libre -> cualquiera libre
        usados = set(assignment.values())
        for e in empleados:
            if e not in assignment:
                pick = next((dd for dd in (desks_e.get(e, []) or []) if dd in zone_of and dd not in usados), None)
                if pick is None:
                    all_free = [dd for z, ds in desks_z.items() for dd in ds if dd not in usados]
                    rng.shuffle(all_free)
                    pick = all_free[0] if all_free else None
                if pick is None:
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

# -----------------------------------------
# Wrapper: obtener SOLO la 'solucion' final
# -----------------------------------------
def randomized_solution(instance: Dict, seed: int = 0) -> Dict[str, Dict[str, List[Tuple[str, str]]]]:
    rng = random.Random(seed)
    Days       = instance["Days"]           # ['L','Ma','Mi','J','V']
    Zones      = tuple(instance["Zones"])   # ('Z0','Z1')
    Desks_Z    = instance["Desks_Z"]
    Days_E     = instance["Days_E"]
    Desks_E    = instance["Desks_E"]
    Employees_G= instance["Employees_G"]
    EMP_TO_G   = {e: g for g, es in Employees_G.items() for e in es}

    # 1) día de reunión por grupo (random)
    groups_days = rand_assign_group_meeting_days(Days, Employees_G, Days_E, Desks_Z, seed=rng.randrange(10**9))

    # 2) capacidad residual por día
    TOTAL = sum(len(ds) for ds in Desks_Z.values())
    days_desks = {d: TOTAL for d in Days}
    for g, d in groups_days.items():
        days_desks[d] -= len(Employees_G[g])

    # 3) segundo día (random)
    second_day = rand_assign_second_day_constructive(
        prefs=Days_E,
        groups_days=groups_days,
        employee_group=EMP_TO_G,
        residual_capacity=days_desks,
        days_order=tuple(Days),
        allow_same_as_group=False,
        seed=rng.randrange(10**9),
    )

    # 4) calendario total por día
    schedule_total = {d: [] for d in Days}
    for e in Days_E:
        g = EMP_TO_G[e]
        gday = groups_days[g]
        schedule_total[gday].append(e)
        d2 = second_day.get(e)
        if d2 and d2 != gday:
            schedule_total[d2].append(e)

    # 5) asientos por día + SOLUCIÓN final (random)
    solucion = crear_solucion_random(
        days=Days,
        schedule_total=schedule_total,
        desks_e=Desks_E,
        desks_z=Desks_Z,
        employee_group=EMP_TO_G,
        zones_order=Zones,
        seat_fn=rand_seat_day_constructive,
        seed=rng.randrange(10**9),
    )
    return solucion, groups_days

def randomized_solution_desde_archivo(
    path_json: str,
    seed: int | None = None
) -> Dict[str, Dict[str, List[Tuple[str, str]]]]:

    with open(path_json, "r", encoding="utf-8") as f:
        instance = json.load(f)

    if seed is None:
        seed = secrets.randbits(64)  # reproducible si lo guardas/loggeas

    # reutiliza tu función existente sin cambiar su lógica
    return randomized_solution(instance, seed=seed)



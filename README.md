# Proyecto – Heurísticas de Asignación

## 1. Método `generar_solucion`

### 📌 Flujograma detallado

```mermaid
flowchart TD
    A([Inicio]) --> B[Entrada: instance JSON<br/>Days, Zones, Desks_Z, Days_E, Desks_E, Employees_G]
    B --> C[Construcción de mapa<br/>Empleado → Grupo]
    C --> D[Asignación de día de reunión<br/>por grupo]
    D --> E[Cálculo de capacidad residual<br/>por día]
    E --> F[Asignación de segundo día<br/>por empleado]
    F --> G[Construcción del calendario<br/>por día]
    G --> H[Asignación de asientos<br/>(crear_solucion)]
    H --> I([Salida:<br/>solución detallada + groups_days])
```

---

## 2. Método `randomized_solution` vs `generar_solucion`

### Diferencias principales

1. **Día de reunión por grupo**  
   - *Constructivo:* determinista, siempre el mismo orden.  
   - *Random:* rompe empates al azar.  

2. **Segundo día por empleado**  
   - *Constructivo:* orden fijo de empleados.  
   - *Random:* baraja empleados y días posibles al azar.  

3. **Asignación de escritorios**  
   - *Constructivo:* prioridades fijas.  
   - *Random:* rompe empates y asigna dentro de cada regla al azar.  

4. **Construcción final**  
   - *Constructivo:* fallback determinista.  
   - *Random:* fallback aleatorio en búsqueda de escritorios libres.  

5. **Wrapper principal**  
   - *Constructivo:* salida única para misma entrada.  
   - *Random:* salida distinta en cada ejecución salvo que se fije `seed`.  

**Constructivo determinista = greedy.**  
**Random = genera múltiples soluciones posibles mediante estocasticidad.**

---

## 3. Método `simulated_annealing_assignments`

### Flujograma detallado

```mermaid
flowchart TD
    A([Inicio]) --> B[Leer instancia JSON<br/>(Days_E, Employees_G)]
    B --> C[Inicializar:<br/>current_solution, best_solution,<br/>current_score, best_score,<br/>trace, T]
    C --> D{{Iteraciones (loop)}}

    D --> E[Mutar solución actual<br/>(mutate_solution)]
    E --> F[Evaluar mutated_solution<br/>(evaluate_solution)]
    F --> G[Calcular delta<br/>(lexicographic_delta)]

    G --> H{¿mutated_score < current_score?}
    H -- Sí --> I[Aceptar siempre:<br/>actualizar current y best]
    H -- No --> J{¿exp(-delta/T) > random()?}
    J -- Sí --> K[Aceptar con probabilidad:<br/>actualizar current]
    J -- No --> L[Rechazar mutación]

    I --> M[Enfriar T = T * cooling_rate]
    K --> M
    L --> M

    M --> D
    D --> N([Salida:<br/>best_solution, best_score, trace])
```

---

## 4. Experimentos y análisis de resultados

El objetivo es minimizar lexicográficamente:

\[
(\text{valid}, \; \text{pref}, \; \text{isolated})
\]

- **valid:** asignaciones inválidas (prioridad máxima).  
- **pref:** violaciones de preferencias.  
- **isolated:** empleados aislados.  

### 4.1 Resultados numéricos

#### Instancia 1
| Método       | n_runs | mean_valid | mean_pref | mean_isolated | Best (v,p,i) | Tiempo (s) |
|--------------|--------|------------|------------|---------------|--------------|------------|
| Randomized   | 1000   | 2.891      | 6.974      | 9.364         | **(0,6,8)**  | 0.685      |
| Constructive | 1      | 3.000      | 9.000      | 7.000         | (3,9,7)      | 0.0005     |
| Annealing    | 1000   | 2.000      | 9.000      | 9.000         | (2,9,9)      | 0.282      |

**Mejor:** Randomized (único con 0 inválidos).

---

#### Instancia 2
| Método       | n_runs | mean_valid | mean_pref | mean_isolated | Best (v,p,i) | Tiempo (s) |
|--------------|--------|------------|------------|---------------|--------------|------------|
| Randomized   | 1000   | 1.698      | 5.454      | 10.497        | (0,4,6)      | 0.748      |
| Constructive | 1      | 0.000      | 4.000      | 5.000         | **(0,4,5)**  | 0.0005     |
| Annealing    | 1000   | 0.000      | 4.000      | 5.000         | **(0,4,5)**  | 0.305      |

**Mejor:** Constructive / Annealing.

---

#### Instancia 5
| Método       | n_runs | mean_valid | mean_pref | mean_isolated | Best (v,p,i) | Tiempo (s) |
|--------------|--------|------------|------------|---------------|--------------|------------|
| Randomized   | 1000   | 0.265      | 19.054     | 22.736        | **(0,19,8)** | 2.095      |
| Constructive | 1      | 3.000      | 20.000     | 22.000        | (3,20,22)    | 0.0012     |
| Annealing    | 1000   | 3.000      | 20.000     | 22.000        | (3,20,22)    | 0.611      |

**Mejor:** Randomized.

---

#### Instancia 8
| Método       | n_runs | mean_valid | mean_pref | mean_isolated | Best (v,p,i) | Tiempo (s) |
|--------------|--------|------------|------------|---------------|--------------|------------|
| Randomized   | 1000   | 1.271      | 20.755     | 60.965        | **(0,19,44)**| 2.583      |
| Constructive | 1      | 2.000      | 22.000     | 63.000        | (2,22,63)    | 0.0027     |
| Annealing    | 1000   | 2.000      | 22.000     | 59.000        | (2,22,59)    | 0.821      |

**Mejor:** Randomized.

---

#### Instancia 10
| Método       | n_runs | mean_valid | mean_pref | mean_isolated | Best (v,p,i) | Tiempo (s) |
|--------------|--------|------------|------------|---------------|--------------|------------|
| Randomized   | 1000   | 1.675      | 31.210     | 107.833       | **(0,27,98)**| 3.996      |
| Constructive | 1      | 2.000      | 34.000     | 91.000        | (2,34,91)    | 0.0022     |
| Annealing    | 1000   | 1.000      | 34.000     | 89.000        | (1,34,89)    | 1.049      |

**Mejor:** Randomized.

---

### 4.2 Conclusiones del análisis

- **Prioridad lexicográfica cumplida:** Randomized obtiene 0 inválidos en 4/5 instancias.  
- **Casos pequeños:** Constructive/Annealing dominan en la instancia 2.  
- **Casos medianos-grandes:** Randomized domina (instancias 5, 8, 10).  
- **Tiempo:** Constructive es el más rápido, pero menos competitivo. Annealing es intermedio.  
- **Trade-off:**
  - Velocidad → Constructive.  
  - Calidad lexicográfica → Randomized.  
  - Estabilidad → Annealing.  

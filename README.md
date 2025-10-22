
# Proyecto Heurística – Asignación de Escritorios

Este proyecto implementa distintos **métodos heurísticos y metaheurísticos** para resolver el problema de asignación de empleados a escritorios, considerando restricciones de grupos, preferencias y días de reunión.

---

# Índice
 
1. [Estructura del proyecto](#-estructura-del-proyecto)  
2. [Descripción de archivos principales](#-descripción-de-archivos-principales)  
3. [Resultados de Métodos de Asignación de Empleados](#resultados-de-métodos-de-asignación-de-empleados)  
   3.1. [Métodos incluidos](#métodos-incluidos)  
   3.2. [Archivos generados y estructura](#archivos-generados-y-estructura)  
4. [Entrega 2: Búsqueda Local y Metaheurístico VNS](#entrega-2-búsqueda-local)  
   4.2. [Vecindario utilizado](#vecindario-utilizado)  
   4.3. [Estrategias de mejora](#estrategias-de-mejora)  
   4.4. [Metaheurístico: Variable Neighborhood Search (VNS)](#metaheurístico-de-búsqueda-local-variable-neighborhood-search-vns)  
5. [Ejecución del programa](#-ejecución)  

---

## 📂 Estructura del proyecto

├── instances/ -> Conjunto de instancias en formato JSON (datos de entrada) <br>
├── resultados_excel/ -> Resultados exportados en archivos Excel (salida del programa)<br>
├── bsuqueda_local.py -> Método de búsqueda local<br>
├── README.md # Documentación del proyecto<br>
├── comparativa_soluciones.py -> Script principal: ejecuta los 3 métodos y compara resultados<br>
├── metodo_aleatorio.py -> Implementación de recocido simulado (simulated annealing)<br>
├── metodo_constructivo.py -> Método constructivo determinista)<br>
├── metodo_constructivo_aleatorio.py # Método constructivo aleatorio<br>
├── metodo_vns.py -> Metaheuristico de búsqueda local<br>
├── score.py -> Funciones de evaluación de soluciones<br>
├── poster.py -> poster en pdf<br>


---

## ⚙️ Descripción de archivos principales

- **`instances/`**  
  Contiene las instancias de prueba (archivos `.json`) con la definición de:
  - Empleados
  - Escritorios y zonas
  - Grupos de trabajo
  - Disponibilidad de días
  - Preferencias de escritorios

- **`resultados_excel/`**  
  Carpeta donde se guardan los resultados exportados a Excel. Dentro de esta carpeta podrá encontrar los resultados de cada método separados en carpetas. 
  Cada archivo generado contiene 3 hojas:
  1. `EmployeeAssignment` → Asignación de empleados a escritorios/días.  
  2. `Groups Meeting day` → Día de reunión elegido para cada grupo.  
  3. `Summary` → Métricas de desempeño (asignaciones válidas, preferencias satisfechas, empleados aislados).  

- **`comparativa_soluciones.py`**  
  Script principal que ejecuta:
  1. Método constructivo determinista.  
  2. Método constructivo aleatorio (varias corridas).  
  3. Recocido simulado con mutaciones.  
  Luego genera métricas comparativas y exporta resultados en Excel.  

- **`score.py`**  
  Funciones de evaluación de soluciones. Devuelve una tupla con:
  1. Asignaciones inválidas.  
  2. Preferencias no cumplidas.  
  3. Empleados aislados.  

---

# Resultados de Métodos de Asignación de Empleados

Este programa ejecuta y compara distintos **métodos heurísticos y metaheurísticos** para resolver el problema de asignación de empleados a escritorios en diferentes días y zonas, respetando preferencias, grupos y restricciones.

---

## Métodos incluidos

1. **Randomized** — genera muchas soluciones aleatorias y selecciona la mejor.  
2. **Constructive** — construye una solución determinista válida.  
3. **Simulated Annealing (Recocido Simulado)** — mejora la solución constructiva mediante pequeñas perturbaciones controladas por temperatura.  
4. **VNS (Variable Neighborhood Search)** — explora sistemáticamente vecindarios con distintas estructuras de movimiento.  
5. **Local Search (Búsqueda Local)** — explora el vecindario de la solución actual buscando mejoras:
   - `local_search_best`: aplica estrategia *best improvement* (busca la mejor mejora posible en cada iteración).
   - `local_search_first`: aplica estrategia *first improvement* (acepta la primera mejora que encuentre).

---

## Archivos generados y estructura

Al ejecutar el archivo principal (`comparativa_soluciones.py`), el script imprime y puede guardar los siguientes resultados:

### 1. **Resumen general de métodos (`summary`)**

Se muestra una tabla (DataFrame de Pandas) con los indicadores principales de desempeño de cada método:

| Columnas              | Descripción |
|-----------------------|-------------|
| `method`              | Nombre del método utilizado (`randomized`, `constructive`, `annealing`, `vns`, `local_search_best`, `local_search_first`). |
| `n_runs`              | Número de ejecuciones realizadas (por ejemplo, 1000 para el método aleatorio). |
| `mean_valid`          | Promedio de **validez de la solución** (cuántas restricciones se cumplen). Cuanto mayor, mejor. |
| `mean_pref`           | Promedio de **satisfacción de preferencias** de los empleados. |
| `mean_isolated`       | Promedio de **empleados aislados** (empleados sin compañeros de grupo). Cuanto menor, mejor. |
| `best_valid`          | Mejor valor alcanzado en validez. |
| `best_pref`           | Mejor valor de satisfacción de preferencias. |
| `best_isolated`       | Menor cantidad de empleados aislados encontrada. |
| `total_time_s`        | Tiempo total (en segundos) de ejecución del método. |

### 2. **Tablas de asignación por empleado**

Después del resumen, el script imprime una **tabla de asignaciones** para cada método, con el formato:

| Employees | L  | Ma | Mi | J  | V  |
|------------|----|----|----|----|----|
| E0         | D2 | D5 | D8 | D3 | D1 |
| E1         | D7 | D9 | D6 | D4 | D2 |
| E2         | D0 | D1 | D5 | D3 | D7 |
| ...        | ...| ...| ...| ...| ...|

- Cada **fila** representa un empleado (por ejemplo, `E0`, `E1`, `E2`).
- Cada **columna** representa un **día de la semana** (`L`, `Ma`, `Mi`, `J`, `V`).
- Las **celdas** muestran el **escritorio asignado** (`D0`, `D1`, …) donde trabajará ese día.
- Si una celda está vacía (`None`), significa que el empleado **no asiste ese día**.
  
Cada tabla se imprime con su **método correspondiente**:
- Mejor solución aleatoria  
- Constructivo  
- Recocido Simulado  
- VNS  
- Búsqueda Local (Best Improvement y First Improvement)

---

# Entrega 2: Búsqueda Local

---

## Descripción del método
El **método de búsqueda local** parte de una solución inicial generada con el método constructivo y busca **mejoras incrementales** explorando el vecindario de la solución actual.  
En cada iteración, se genera una nueva solución vecina aplicando un pequeño cambio (un *movimiento*).  
Si el cambio mejora el valor de la función objetivo, se actualiza la solución actual.  
El proceso termina cuando **no se encuentran más mejoras**, alcanzando un *óptimo local*.

---

### Vecindario utilizado
El **vecindario general** está definido por el movimiento:

> *Mover un empleado de un día a otro*, siempre que se cumplan las restricciones.

#### Detalles del movimiento:
- Solo se mueve un empleado a un día diferente.  
- **No se permite** moverlo fuera del día asignado a su grupo (`groups_days`).  
- El día destino debe tener **escritorios disponibles** (`Desks_Z`).  
- Al realizar el movimiento, se actualizan las asignaciones de días y zonas.

Este vecindario permite **pequeñas modificaciones controladas**, manteniendo la factibilidad de la solución en todo momento.

---

### Estrategias de mejora
El método implementa dos variantes clásicas de búsqueda local:

| Variante | Descripción |
|-----------|-------------|
| `best` | (*Best Improvement*) Recorre todo el vecindario y elige la mejor mejora posible antes de actualizar la solución. Mayor calidad pero más lento. |
| `first` | (*First Improvement*) Acepta la primera mejora que encuentra. Más rápido pero puede converger antes. |

Ambas estrategias repiten el proceso hasta que **no se encuentra ninguna mejora adicional**.

---
## Metaheurístico de búsqueda local: Variable Neighborhood Search (VNS)
Este metaheurístico implementa una versión extendida del algoritmo **VNS (Variable Neighborhood Search)**. El enfoque combina **mutaciones controladas** (vecindarios) con **búsqueda local** dentro de cada vecindario.

---

## Idea general

El algoritmo VNS parte de una **solución inicial válida** y explora una serie de **vecindarios de diferente naturaleza**.  
En cada uno:
1. Se **perturba (shaking)** la solución actual mediante una mutación específica.  
2. Se ejecuta una **búsqueda local** centrada en ese tipo de vecindario para mejorar la solución.  
3. Si se encuentra una mejora, el proceso vuelve al primer vecindario; si no, pasa al siguiente.

Este ciclo continúa hasta alcanzar el número máximo de iteraciones o hasta no encontrar mejoras después de varios intentos.

---

## Vecindarios implementados

Cada tipo de vecindario representa un patrón de cambio (*movimiento*) diferente sobre la solución actual:

| Vecindario | Descripción breve | Propósito |
|-------------|------------------|------------|
| **N1** | **Swap dentro de la misma zona** | Intercambia empleados que comparten zona y día. Pequeñas mejoras locales. |
| **N2** | **Swap entre zonas del mismo día** | Mueve empleados entre distintas zonas, manteniendo el día. Favorece el balance entre zonas. |
| **N3** | **Mover día libre** | Reasigna un empleado a un día alternativo de su preferencia (si tiene cupo). Mejora satisfacción individual. |
| **N4** | **Reubicar aislado** | Detecta empleados sin compañeros de grupo y los reubica con su equipo. Reduce aislamiento. |
| **N5** | **Reasignar zona completa** | Mueve todos los miembros de un grupo a otra zona con capacidad suficiente. Cambios estructurales más grandes. |
| **N6** | **Reasignar según preferencias** | Corrige asignaciones de empleados que trabajan en días no preferidos. Mejora satisfacción sin romper restricciones. |

Cada mutación garantiza que las restricciones de grupos, cupos y días de reunión se respeten.

---

## Búsqueda local dentro de cada vecindario

Después de aplicar una mutación (`shaking`), el algoritmo ejecuta una **búsqueda local** (`local_search_vns`):

- Explora el vecindario actual hasta que **no se encuentren más mejoras**.
- Usa estrategia *first-improvement*: acepta la primera mejora detectada (más rápida).
- La evaluación de cada solución se realiza con `evaluate_solution`, que devuelve una tupla con los indicadores:
---

## 🚀 Ejecución

Ejemplo de uso en terminal:

```bash
python comparativa_soluciones.py

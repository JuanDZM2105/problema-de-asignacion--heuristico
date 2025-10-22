
# Proyecto Heurística – Asignación de Escritorios

Este proyecto implementa distintos **métodos heurísticos y metaheurísticos** para resolver el problema de asignación de empleados a escritorios, considerando restricciones de grupos, preferencias y días de reunión.

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

- **`metodo_constructivo.py`**  
  Implementación del algoritmo determinista:
  - Asigna día de reunión por grupo.  
  - Asigna segundo día por empleado.  
  - Construye el calendario y la solución final.  

- **`metodo_constructivo_aleatorio.py`**  
  Variante aleatoria del método constructivo:
  - Introduce aleatoriedad al romper empates.  
  - Genera soluciones distintas en cada ejecución.  

- **`metodo_aleatorio.py`**  
  Implementa el **recocido simulado (Simulated Annealing)**:
  - Parte de una solución inicial (constructiva).  
  - Aplica mutaciones (swap de escritorios, zonas o días).  
  - Acepta o rechaza soluciones con probabilidad dependiente de la temperatura.  

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

## 🚀 Ejecución

Ejemplo de uso en terminal:

```bash
python comparativa_soluciones.py

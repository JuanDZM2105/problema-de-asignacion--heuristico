
# Proyecto Heurística – Asignación de Escritorios

Este proyecto implementa distintos **métodos heurísticos y metaheurísticos** para resolver el problema de asignación de empleados a escritorios, considerando restricciones de grupos, preferencias y días de reunión.

---

## 📂 Estructura del proyecto

├── instances/ # Conjunto de instancias en formato JSON (datos de entrada) <br>
├── resultados_excel/ # Resultados exportados en archivos Excel (salida del programa)<br>
├── README.md # Documentación del proyecto<br>
├── comparativa_soluciones.py # Script principal: ejecuta los 3 métodos y compara resultados<br>
├── metodo_aleatorio.py # Implementación de recocido simulado (simulated annealing)<br>
├── metodo_constructivo.py # Método constructivo determinista (greedy)<br>
├── metodo_constructivo_aleatorio.py # Método constructivo aleatorio<br>
├── score.py # Funciones de evaluación de soluciones<br>
├── poster.py # poster en pdf<br>


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
  Carpeta donde se guardan los resultados exportados a Excel.  
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

## 🚀 Ejecución

Ejemplo de uso en terminal:

```bash
python comparativa_soluciones.py




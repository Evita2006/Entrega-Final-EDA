Este proyecto es un simulador interactivo de estrategias de Fórmula 1. Permite seleccionar pilotos, circuitos y condiciones de carrera para analizar el impacto de diferentes estrategias de neumáticos y paradas en boxes.

Características:
- Selección de pilotos y circuitos desde archivos CSV.
- Configuración de condiciones climáticas y perfil de pista.
- Simulación de carrera considerando degradación de neumáticos, tráfico y paradas en boxes.
- Comparación de estrategias y evaluación de decisiones.
- Gráficas de ritmo por vuelta.
- Resultados detallados y análisis por piloto.

Archivos necesarios:

Coloca estos archivos CSV en el mismo directorio que el script:

- `circuitos_f1.csv` — Información de los circuitos.
- `pilotos_f1_2024.csv` — Datos de los pilotos en 2024
- `equipos_f1_2024.csv` — Datos de los equipos y tiempos de pit stop en 2024

Uso:
Tras correr el código, se le pedirá al usuario que añada información para poder hacer la simulación. 
Opciones del menú principal:
1. Simular carrera y mostrar tabla de resultados: Ejecuta la simulación y muestra la clasificación final. El usuario deberá rellenar los campos que se le vayan pidiendo. 
2. Graficar ritmo por vuelta: Muestra la evolución del tiempo por vuelta de los pilotos seleccionados. 
3. Comparar estrategias (tabla ordenada): Tabla ordenada por tiempo total de carrera.
4. Evaluar decisiones de estrategia: Análisis del impacto de las estrategias elegidas.
5. Salir: Termina el programa.

El simulador modela una carrera de Fórmula 1 considerando la estrategia de cada piloto (paradas y neumáticos), el circuito, el clima y el perfil de pista.

1. Selección de condiciones y pilotos: El usuario elige clima, perfil de pista, circuito y pilotos desde archivos CSV.
2. Configuración de pilotos: Para cada piloto, se define la estrategia (vueltas de parada y compuestos de neumáticos) y se calcula automáticamente la degradación por vuelta según condiciones.
3. Simulación de carrera:
   - Para cada vuelta y cada piloto:
     - Se determina el neumático actual según la estrategia.
     - Se calcula el tiempo de vuelta considerando:
       - Tiempo base del piloto.
       - Degradación acumulada del neumático.
       - Variación aleatoria para simular factores impredecibles.
       - Penalización por tráfico (si hay otros pilotos con tiempos similares en esa vuelta).
     - Si la vuelta coincide con una parada, se suma el tiempo de pit stop.
   - Se acumulan los tiempos por vuelta y el total de carrera para cada piloto.
4. Resultados y análisis:
   - Se ordenan los pilotos por tiempo total para mostrar la clasificación.
   - Se pueden graficar los ritmos por vuelta y comparar estrategias.
   - El simulador evalúa el impacto de las decisiones de estrategia (agresiva, conservadora, adaptada a lluvia, etc.).

- Clases principales:
  - Piloto: Guarda nombre, tiempos, degradación, estrategia y compuestos.
  - SimuladorF1: Gestiona la simulación de vueltas, cálculo de tráfico, degradación y resultados.
- Funciones:
  - Selección de clima, pista, pilotos y estrategias.
  - Cálculo automático de degradación y sugerencia de paradas.
  - Lectura de datos desde archivos CSV para circuitos, pilotos y equipos.
- Menú interactivo: Permite al usuario simular carreras, graficar ritmos, comparar estrategias y analizar decisiones.

Análisis de eficiencia
- Complejidad temporal:
  - La simulación principal recorre todas las vueltas para todos los pilotos:  
    O(V × P), donde V = número de vueltas y P = número de pilotos.
  - El cálculo de tráfico para cada piloto en cada vuelta es O(P), por lo que el peor caso es O(V × P²).
  - Para un uso típico (menos de 25 pilotos y 80 vueltas), el tiempo de ejecución es muy bajo y adecuado para uso interactivo.
- Complejidad espacial:
  - Se almacenan los tiempos de cada vuelta para cada piloto: O(V × P).
  - El resto de la información (estrategias, compuestos, resultados) es de tamaño pequeño comparado con los datos de vueltas.


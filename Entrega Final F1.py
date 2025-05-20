import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import os

TIPOS_NEUMATICO = ["blando", "medio", "duro", "intermedio", "lluvia"]

class Piloto:
    def __init__(self, nombre, tiempo_base, degradacion, tiempo_pit, posicion_salida, estrategia=None, compuestos=None):
        self.nombre = nombre
        self.tiempo_base = tiempo_base
        self.degradacion = degradacion  
        self.tiempo_pit = tiempo_pit
        self.posicion_salida = posicion_salida
        self.estrategia = estrategia if estrategia is not None else []
        self.compuestos = compuestos if compuestos is not None else ["blando"] * (len(self.estrategia)+1)
        self.tiempos = []  # tiempo por vuelta
        self.total = 0

# Simulador principal
class SimuladorF1:
    def __init__(self, vueltas, pilotos, clima="seco"):
        self.vueltas = vueltas
        self.pilotos = pilotos
        self.clima = clima

    def simular_vuelta(self, piloto, vuelta, trafico):
        tipo_neumatico = self.get_neumatico_actual(piloto, vuelta)
        degradacion = piloto.degradacion[tipo_neumatico] * vuelta
        variacion = random.uniform(-0.3, 0.3) + trafico
        return piloto.tiempo_base + degradacion + variacion

    def get_neumatico_actual(self, piloto, vuelta):
        if not piloto.estrategia or not piloto.compuestos:
            return "blando"
        paradas = piloto.estrategia
        compuestos = piloto.compuestos
        index = 0
        for i, parada in enumerate(paradas):
            if vuelta >= parada:
                index = i + 1
        if index >= len(compuestos):
            index = len(compuestos) - 1
        return compuestos[index]

    def calcular_trafico(self, tiempos_vuelta_actual, piloto_idx, ventana=2.0):
        """
        Calcula el tráfico para un piloto dado según cuántos pilotos están en una ventana de tiempo cercana.
        tiempos_vuelta_actual: lista de tiempos de todos los pilotos en la vuelta actual (sin tráfico)
        piloto_idx: índice del piloto a evaluar
        ventana: rango de segundos para considerar 'tráfico'
        """
        mi_tiempo = tiempos_vuelta_actual[piloto_idx]
        trafico = 0.0
        for idx, t in enumerate(tiempos_vuelta_actual):
            if idx != piloto_idx and abs(t - mi_tiempo) <= ventana:
                trafico += 0.05  # penalización
        return trafico

    def simular_carrera(self):
        resultados = {}
        n_pilotos = len(self.pilotos)
        tiempos_acumulados = [0.0 for _ in range(n_pilotos)]
        tiempos_por_piloto = [[] for _ in range(n_pilotos)]

        for vuelta in range(1, self.vueltas + 1):
            # calcula el tiempo base de vuelta de cada piloto (sin tráfico)
            tiempos_vuelta_sin_trafico = []
            for idx, piloto in enumerate(self.pilotos):
                tipo_neumatico = self.get_neumatico_actual(piloto, vuelta)
                degradacion = piloto.degradacion[tipo_neumatico] * vuelta
                variacion = random.uniform(-0.3, 0.3)
                tiempo_base = piloto.tiempo_base + degradacion + variacion
                if vuelta in piloto.estrategia:
                    tiempos_acumulados[idx] += piloto.tiempo_pit
                tiempos_vuelta_sin_trafico.append(tiempo_base)

            # calcula el tráfico para cada piloto y suma al tiempo de vuelta
            for idx, piloto in enumerate(self.pilotos):
                trafico = self.calcular_trafico(tiempos_vuelta_sin_trafico, idx)
                tiempo_vuelta = tiempos_vuelta_sin_trafico[idx] + trafico
                tiempos_por_piloto[idx].append(tiempo_vuelta)
                tiempos_acumulados[idx] += tiempo_vuelta

        # Asigna resultados a cada piloto
        for idx, piloto in enumerate(self.pilotos):
            piloto.tiempos = tiempos_por_piloto[idx]
            piloto.total = tiempos_acumulados[idx]
            resultados[piloto.nombre] = piloto.total
        return resultados

    def comparar_estrategias(self):
        resultados = self.simular_carrera()
        orden = sorted(resultados.items(), key=lambda x: x[1])
        return pd.DataFrame(orden, columns=["Piloto", "Tiempo Total"])

    def graficar_ritmo(self):
        # Asegura que los tiempos por vuelta estén calculados
        if not self.pilotos or not self.pilotos[0].tiempos or len(self.pilotos[0].tiempos) != self.vueltas:
            self.simular_carrera()

        print("\nPilotos disponibles para graficar:")
        for idx, piloto in enumerate(self.pilotos):
            print(f"{idx+1}. {piloto.nombre}")
        seleccion = input("Introduce los números de los pilotos a graficar separados por coma (deja vacío para todos): ").strip()
        if seleccion:
            indices = [int(i)-1 for i in seleccion.split(",") if i.strip().isdigit() and 1 <= int(i) <= len(self.pilotos)]
            pilotos_a_graficar = [self.pilotos[i] for i in indices]
        else:
            pilotos_a_graficar = self.pilotos

        plt.figure(figsize=(14, 7))
        colores = plt.cm.get_cmap('tab10', len(pilotos_a_graficar))
        for idx, piloto in enumerate(pilotos_a_graficar):
            if piloto.tiempos and len(piloto.tiempos) == self.vueltas:
                x = list(range(1, len(piloto.tiempos) + 1))
                y = piloto.tiempos
                plt.plot(x, y, label=piloto.nombre, color=colores(idx), marker='o', markersize=3, linewidth=2, alpha=0.85)
            else:
                print(f"Advertencia: {piloto.nombre} no tiene datos completos de vueltas.")
        plt.xlabel("Vuelta")
        plt.ylabel("Tiempo por vuelta (s)")
        plt.title("Evolución del ritmo por vuelta durante la carrera")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.xlim(1, self.vueltas)
        plt.show()
        

    def evaluar_decisiones(self):
        """
        Evalúa el efecto de las decisiones de estrategia (neumáticos y paradas) en el rendimiento y posición final.
        Muestra un resumen por piloto.
        """
        resultados = self.simular_carrera()
        orden = sorted(resultados.items(), key=lambda x: x[1])
        posiciones = {nombre: idx+1 for idx, (nombre, _) in enumerate(orden)}
        print("\nEvaluación de decisiones de estrategia:")
        for piloto in self.pilotos:
            print(f"\nPiloto: {piloto.nombre}")
            print(f"  Estrategia de paradas: {piloto.estrategia if piloto.estrategia else 'Sin paradas'}")
            print(f"  Compuestos usados: {piloto.compuestos}")
            print(f"  Tiempo total: {piloto.total:.2f} s")
            print(f"  Posición final: {posiciones[piloto.nombre]}")
            # Análisis simple del efecto de la estrategia:
            if len(piloto.estrategia) == 0:
                print("  Estrategia conservadora (sin paradas).")
            elif "lluvia" in piloto.compuestos or "intermedio" in piloto.compuestos:
                print("  Estrategia adaptada a condiciones de lluvia.")
            elif piloto.compuestos.count("blando") > piloto.compuestos.count("duro"):
                print("  Estrategia agresiva (más blandos).")
            else:
                print("  Estrategia equilibrada o conservadora.")

def pedir_compuestos(estrategia):
    compuestos = []
    print("Elige el tipo de neumático para cada stint:")
    for i in range(len(estrategia)+1):
        while True:
            print(f"Stint {i+1} (opciones: {', '.join(TIPOS_NEUMATICO)}): ", end="")
            tipo = input().strip().lower()
            if tipo in TIPOS_NEUMATICO:
                compuestos.append(tipo)
                break
            else:
                print("Tipo de neumático no válido. Intenta de nuevo.")
    return compuestos

def sugerir_paradas(vueltas, num_paradas):
    """
    Devuelve una lista de vueltas sugeridas para parar, dividiendo la carrera en stints iguales.
    """
    if num_paradas == 0:
        return []
    stints = num_paradas + 1
    paradas = []
    for i in range(1, num_paradas + 1):
        parada = int(round(i * vueltas / stints))
        paradas.append(parada)
    return paradas

def estimar_tiempo_total(tiempo_base, degradacion, compuestos, estrategia, tiempo_pit, vueltas):
    """
    Estima el tiempo total de carrera para una estrategia dada.
    """
    total = 0
    stint_inicial = 1
    paradas = estrategia + [vueltas + 1]
    for i, parada in enumerate(paradas):
        stint_vueltas = parada - stint_inicial
        tipo = compuestos[i]
        # Suma tiempo de cada vuelta en el stint considerando degradación acumulada
        for v in range(stint_vueltas):
            total += tiempo_base + degradacion[tipo] * (stint_inicial + v)
        if parada <= vueltas:
            total += tiempo_pit
        stint_inicial = parada
    return total

def definir_estrategia(vueltas, tiempo_base=None, degradacion=None, tiempo_pit=None):
    print("\nElige un plan de carrera:")
    print("1. Sin paradas")
    print("2. Una parada (el programa decide la vuelta)")
    print("3. Dos paradas (el programa decide las vueltas)")
    while True:
        opcion = input("Opción (1/2/3): ").strip()
        if opcion in ("1", "2", "3"):
            num_paradas = int(opcion) - 1
            estrategia = sugerir_paradas(vueltas, num_paradas)
            print(f"Paradas sugeridas en las vueltas: {estrategia if estrategia else 'Sin paradas'}")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")
    # Si se tienen datos, estimar el impacto en el tiempo total
    if tiempo_base is not None and degradacion is not None and tiempo_pit is not None:
        print("Ahora elige los compuestos para estimar el impacto en el tiempo total.")
        compuestos = pedir_compuestos(estrategia)
        tiempo_estimado = estimar_tiempo_total(tiempo_base, degradacion, compuestos, estrategia, tiempo_pit, vueltas)
        print(f"Tiempo total estimado para esta estrategia: {tiempo_estimado:.2f} s")
    else:
        compuestos = pedir_compuestos(estrategia)
    return estrategia, compuestos

def seleccionar_clima():
    print("\nSelecciona las condiciones climáticas:")
    print("1. Seco")
    print("2. Lluvia")
    while True:
        opcion = input("Opción (1/2): ").strip()
        if opcion == "1":
            return "seco"
        elif opcion == "2":
            return "lluvia"
        else:
            print("Opción no válida. Intenta de nuevo.")

def seleccionar_perfil_pista():
    print("\nSelecciona el perfil de pista:")
    print("1. Rápida (menos degradación)")
    print("2. Técnica (más degradación)")
    while True:
        opcion = input("Opción (1/2): ").strip()
        if opcion == "1":
            return 0.8  # factor degradación
        elif opcion == "2":
            return 1.2
        else:
            print("Opción no válida. Intenta de nuevo.")

def ajustar_degradacion(degradacion, factor):
    return {k: v * factor for k, v in degradacion.items()}

def formatear_tiempo(segundos):
    """
    Convierte segundos a formato hh:mm:ss.sss
    """
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = segundos % 60
    return f"{horas:02d}:{minutos:02d}:{segs:06.3f}"

def mostrar_tabla_resultados(df):
    print("\nResultados finales de la carrera:")
    if "Piloto" in df.columns and "Tiempo Total" in df.columns:
        columnas = ["Piloto", "Tiempo Total"]
        if "Posición" in df.columns:
            columnas = ["Posición"] + columnas
        df = df.copy()
        df["Tiempo Total"] = df["Tiempo Total"].apply(formatear_tiempo)
        print(df[columnas].to_string(index=False))
    else:
        print(df.to_string(index=False))

def seleccionar_circuito():
    base_path = os.path.dirname(os.path.abspath(__file__))
    circuitos_path = os.path.join(base_path, "circuitos_f1.csv")
    circuitos_df = pd.read_csv(circuitos_path)
    print("\nCircuitos disponibles:")
    for idx, row in circuitos_df.iterrows():
        print(f"{idx+1}. {row['NombreCircuito']}")
    while True:
        seleccion = input("Selecciona el número del circuito: ").strip()
        if seleccion.isdigit() and 1 <= int(seleccion) <= len(circuitos_df):
            circuito = circuitos_df.iloc[int(seleccion)-1]
            print(f"Seleccionado: {circuito['NombreCircuito']} - Vueltas: {circuito['Vueltas']}, Km: {circuito['KilometrosCircuito']}, Curvas: {circuito['Curvas']}")
            return circuito
        else:
            print("Opción no válida. Intenta de nuevo.")

def seleccionar_pilotos():
    base_path = os.path.dirname(os.path.abspath(__file__))
    pilotos_path = os.path.join(base_path, "pilotos_f1_2024.csv")
    pilotos_df = pd.read_csv(pilotos_path)
    print("\nPilotos disponibles:")
    for idx, row in pilotos_df.iterrows():
        print(f"{idx+1}. {row['Nombre']} ({row['Equipo']})")
    seleccionados = []
    indices = input("Introduce los números de los pilotos separados por coma (ej: 1,3,5): ").split(",")
    for idx in indices:
        idx = idx.strip()
        if idx.isdigit() and 1 <= int(idx) <= len(pilotos_df):
            seleccionados.append(pilotos_df.iloc[int(idx)-1])
        else:
            print(f"Índice {idx} no válido, se omite.")
    return seleccionados

def calcular_degradacion_base(circuito, clima, perfil_pista):
    """
    Calcula una degradación base para cada tipo de neumático en función del circuito, clima y perfil de pista.
    """
    degradacion_base = {
        "blando": 0.18,
        "medio": 0.13,
        "duro": 0.09,
        "intermedio": 0.22,
        "lluvia": 0.28 #degradación en segundos por vuelta
    }
    if clima == "lluvia":
        degradacion_base["intermedio"] *= 1.1
        degradacion_base["lluvia"] *= 1.15
        degradacion_base["blando"] *= 1.3
        degradacion_base["medio"] *= 1.2
        degradacion_base["duro"] *= 1.15
        
    for k in degradacion_base:
        degradacion_base[k] *= perfil_pista
    # Ajuste por curvas del circuito -> más curvas, más degradación
    curvas = int(circuito["Curvas"])
    factor_curvas = 1 + (curvas - 15) * 0.01  # 1% más por cada curva sobre 15
    for k in degradacion_base:
        degradacion_base[k] *= factor_curvas
    return degradacion_base

def obtener_tiempo_pit_equipo(equipo):
    base_path = os.path.dirname(os.path.abspath(__file__))
    equipos_path = os.path.join(base_path, "equipos_f1_2024.csv")
    equipos_df = pd.read_csv(equipos_path)
    fila = equipos_df[equipos_df["Equipo"] == equipo]
    if not fila.empty:
        return float(fila.iloc[0]["TiempoMedioPitStop2024"])
    else:
        return 2.5

def crear_pilotos(vueltas, circuito, clima, perfil_pista):
    """
    Permite seleccionar pilotos del CSV y calcula automáticamente la degradación por vuelta según condiciones.
    El tiempo de parada en boxes se toma automáticamente del CSV de equipos.
    """
    pilotos_info = seleccionar_pilotos()
    pilotos = []
    degradacion_auto = calcular_degradacion_base(circuito, clima, perfil_pista)
    for i, info in enumerate(pilotos_info):
        print(f"\nConfigurando a {info['Nombre']} ({info['Equipo']})")
        tiempo_base = float(info['TiempoBase2024'])
        print(f"Tiempo base por vuelta (s) para {info['Nombre']}: {tiempo_base}")
        print("Degradación por vuelta estimada automáticamente según condiciones:")
        for tipo in TIPOS_NEUMATICO:
            print(f"  {tipo}: {degradacion_auto[tipo]:.3f} s/vuelta")
        degradacion = degradacion_auto.copy()
        tiempo_pit = obtener_tiempo_pit_equipo(info['Equipo'])
        print(f"Tiempo de parada en boxes para {info['Equipo']}: {tiempo_pit:.2f} s")
        try:
            posicion_salida = int(input(f"Posición de salida (por defecto {i+1}): ") or (i+1))
        except ValueError:
            posicion_salida = i+1
        estrategia, compuestos = definir_estrategia(vueltas, tiempo_base, degradacion, tiempo_pit)
        piloto = Piloto(info['Nombre'], tiempo_base, degradacion, tiempo_pit, posicion_salida, estrategia, compuestos)
        pilotos.append(piloto)
    return pilotos

def main():
    print("=== Simulador de Estrategias F1 ===")
    clima = seleccionar_clima()
    perfil_pista = seleccionar_perfil_pista()
    circuito = seleccionar_circuito()
    vueltas = int(circuito['Vueltas'])
    print(f"\nEl circuito seleccionado tiene {vueltas} vueltas, {circuito['KilometrosCircuito']} km y {circuito['Curvas']} curvas.")
    pilotos = crear_pilotos(vueltas, circuito, clima, perfil_pista)
    sim = SimuladorF1(vueltas=vueltas, pilotos=pilotos, clima=clima)
    while True:
        print("\nOpciones:")
        print("1. Simular carrera y mostrar tabla de resultados")
        print("2. Graficar ritmo por vuelta")
        print("3. Comparar estrategias (tabla ordenada)")
        print("4. Evaluar decisiones de estrategia")
        print("5. Salir")
        opcion = input("Selecciona una opción: ").strip()
        if opcion == "1":
            resultados = sim.simular_carrera()
            ordenados = sorted(resultados.items(), key=lambda x: x[1])
            df = pd.DataFrame(ordenados, columns=["Piloto", "Tiempo Total"])
            df.insert(0, "Posición", range(1, len(df) + 1))
            mostrar_tabla_resultados(df)
        elif opcion == "2":
            sim.graficar_ritmo()
        elif opcion == "3":
            df = sim.comparar_estrategias()
            df.insert(0, "Posición", range(1, len(df) + 1))
            mostrar_tabla_resultados(df)
        elif opcion == "4":
            sim.evaluar_decisiones()
        elif opcion == "5":
            print("¡Hasta la próxima!")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()


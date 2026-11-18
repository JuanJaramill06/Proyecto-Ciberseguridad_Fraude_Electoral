"""
Proyecto Final 1 - Deteccion de fraude en procesos electorales
Paso 2: Analisis exploratorio + Deteccion de anomalias

Tecnicas implementadas (2, segun lo permitido por el enunciado):
  1. Reglas simples (umbrales de sentido comun / reglas de negocio)
  2. Estadistica (z-score sobre variables clave)

Genera un dataset final con las banderas de cada tecnica y un score combinado.
"""

import numpy as np
import pandas as pd

import os
df = pd.read_csv("../data/dataset_votacion.csv")

# =========================================================
# TECNICA 1: REGLAS SIMPLES
# =========================================================
# Regla A: votos emitidos no pueden superar a los habilitados
df["regla_sobrevoto"] = df["votos_emitidos"] > df["habilitados"]

# Regla B: participacion sospechosamente alta (>95%) -- poco realista en la practica
df["regla_participacion_alta"] = df["participacion_pct"] > 95

# Regla C: un candidato concentra mas del 90% de los votos en la mesa
df["regla_candidato_extremo"] = df[["pct_A", "pct_B", "pct_C"]].max(axis=1) > 90

# Regla D: el resultado se reporto en menos de 5 minutos tras el cierre (muy rapido)
df["regla_reporte_rapido"] = df["tiempo_reporte_min"] < 5

df["flag_reglas"] = (
    df["regla_sobrevoto"]
    | df["regla_participacion_alta"]
    | df["regla_candidato_extremo"]
    | df["regla_reporte_rapido"]
)

# =========================================================
# TECNICA 2: ESTADISTICA (Z-SCORE)
# =========================================================
# Calculamos z-score de variables clave POR MUNICIPIO (cada municipio tiene
# su propia distribucion "normal" de comportamiento electoral)
def zscore_por_grupo(serie, grupo):
    return serie.groupby(grupo).transform(lambda x: (x - x.mean()) / x.std(ddof=0))

df["z_participacion"] = zscore_por_grupo(df["participacion_pct"], df["municipio"])
df["z_tiempo_reporte"] = zscore_por_grupo(df["tiempo_reporte_min"], df["municipio"])
df["z_pct_max_candidato"] = zscore_por_grupo(
    df[["pct_A", "pct_B", "pct_C"]].max(axis=1), df["municipio"]
)

UMBRAL_Z = 3  # criterio estandar: |z| > 3 se considera outlier estadistico

df["flag_estadistica"] = (
    (df["z_participacion"].abs() > UMBRAL_Z)
    | (df["z_tiempo_reporte"].abs() > UMBRAL_Z)
    | (df["z_pct_max_candidato"].abs() > UMBRAL_Z)
)

# =========================================================
# SCORE COMBINADO
# =========================================================
df["flag_combinado"] = df["flag_reglas"] | df["flag_estadistica"]
df["n_tecnicas_que_detectan"] = df["flag_reglas"].astype(int) + df["flag_estadistica"].astype(int)

os.makedirs("../resultados", exist_ok=True)
df.to_csv("../resultados/dataset_con_deteccion.csv", index=False)

# =========================================================
# EVALUACION CONTRA GROUND TRUTH (solo posible porque el dato es simulado)
# =========================================================
def evaluar(col_pred, nombre):
    tp = ((df[col_pred]) & (df["es_anomalia_real"] == 1)).sum()
    fp = ((df[col_pred]) & (df["es_anomalia_real"] == 0)).sum()
    fn = ((~df[col_pred]) & (df["es_anomalia_real"] == 1)).sum()
    tn = ((~df[col_pred]) & (df["es_anomalia_real"] == 0)).sum()
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    print(f"\n--- {nombre} ---")
    print(f"Detectadas: {df[col_pred].sum()} | TP={tp} FP={fp} FN={fn} TN={tn}")
    print(f"Precision={precision:.2f}  Recall={recall:.2f}")

print("=" * 55)
print("RESULTADOS DE DETECCION")
print("=" * 55)
evaluar("flag_reglas", "Tecnica 1: Reglas simples")
evaluar("flag_estadistica", "Tecnica 2: Estadistica (z-score)")
evaluar("flag_combinado", "Combinado (reglas OR estadistica)")

print("\nTotal mesas:", len(df))
print("Mesas marcadas por al menos una tecnica:", df["flag_combinado"].sum())
print("Mesas marcadas por AMBAS tecnicas (mayor confianza):", (df["n_tecnicas_que_detectan"] == 2).sum())
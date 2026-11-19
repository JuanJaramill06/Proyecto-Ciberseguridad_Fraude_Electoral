"""
Proyecto Final 1 - Deteccion de fraude en procesos electorales
Paso 1: Generacion del dataset simulado

Simula resultados de votacion por "mesa" (puesto de votacion) en varios
municipios ficticios, con 3 candidatos. Se siembran anomalias a proposito
para poder validar que las tecnicas de deteccion funcionen.

IMPORTANTE: Todos los datos son 100% simulados. No representan ningun
proceso electoral real.
"""

import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

N_MESAS_NORMALES = 450
N_ANOMALAS = 50  # ~10% de mesas con comportamiento sospechoso

municipios = ["San Rafael", "Puerto Alegre", "Villa Nueva", "El Mirador", "Santa Rosa"]

filas = []

# ---------- Mesas normales ----------
for i in range(N_MESAS_NORMALES):
    municipio = np.random.choice(municipios)
    habilitados = np.random.randint(200, 450)
    participacion = np.clip(np.random.normal(0.68, 0.08), 0.35, 0.92)
    emitidos = int(habilitados * participacion)

    # Reparto de votos entre 3 candidatos (con algo de variabilidad por municipio)
    base = np.random.dirichlet([4, 3.5, 2.5])
    votos_a = int(emitidos * base[0])
    votos_b = int(emitidos * base[1])
    votos_c = emitidos - votos_a - votos_b

    hora_cierre_min = np.random.randint(16 * 60, 18 * 60)  # entre 4pm y 6pm
    tiempo_reporte = np.random.randint(15, 90)  # minutos en reportar

    filas.append({
        "mesa_id": f"M{i+1:04d}",
        "municipio": municipio,
        "habilitados": habilitados,
        "votos_emitidos": emitidos,
        "votos_A": votos_a,
        "votos_B": votos_b,
        "votos_C": votos_c,
        "hora_cierre_min": hora_cierre_min,
        "tiempo_reporte_min": tiempo_reporte,
        "es_anomalia_real": 0,  # ground truth para validar (no usar en el modelo)
    })

# ---------- Mesas anomalas (varios tipos de anomalia) ----------
tipos_anomalia = np.random.choice(
    ["participacion_excesiva", "sobrevoto", "candidato_extremo", "reporte_rapido"],
    size=N_ANOMALAS,
)

for i, tipo in enumerate(tipos_anomalia):
    municipio = np.random.choice(municipios)
    habilitados = np.random.randint(200, 450)

    if tipo == "sobrevoto":
        # Mas votos emitidos que habilitados (imposible)
        emitidos = int(habilitados * np.random.uniform(1.02, 1.15))
    elif tipo == "participacion_excesiva":
        # Participacion sospechosamente alta (>97%)
        emitidos = int(habilitados * np.random.uniform(0.97, 1.0))
    else:
        participacion = np.clip(np.random.normal(0.68, 0.08), 0.4, 0.9)
        emitidos = int(habilitados * participacion)

    if tipo == "candidato_extremo":
        # Un candidato se lleva casi todo
        base = np.array([0.95, 0.03, 0.02])
    else:
        base = np.random.dirichlet([4, 3.5, 2.5])

    votos_a = int(emitidos * base[0])
    votos_b = int(emitidos * base[1])
    votos_c = max(emitidos - votos_a - votos_b, 0)

    if tipo == "reporte_rapido":
        tiempo_reporte = np.random.randint(1, 4)  # reporta en minutos
    else:
        tiempo_reporte = np.random.randint(15, 90)

    hora_cierre_min = np.random.randint(16 * 60, 18 * 60)

    filas.append({
        "mesa_id": f"M{N_MESAS_NORMALES + i + 1:04d}",
        "municipio": municipio,
        "habilitados": habilitados,
        "votos_emitidos": emitidos,
        "votos_A": votos_a,
        "votos_B": votos_b,
        "votos_C": votos_c,
        "hora_cierre_min": hora_cierre_min,
        "tiempo_reporte_min": tiempo_reporte,
        "es_anomalia_real": 1,
    })

df = pd.DataFrame(filas).sample(frac=1, random_state=42).reset_index(drop=True)

# Columnas derivadas utiles para el analisis
df["participacion_pct"] = (df["votos_emitidos"] / df["habilitados"]) * 100
df["pct_A"] = df["votos_A"] / df["votos_emitidos"].replace(0, np.nan) * 100
df["pct_B"] = df["votos_B"] / df["votos_emitidos"].replace(0, np.nan) * 100
df["pct_C"] = df["votos_C"] / df["votos_emitidos"].replace(0, np.nan) * 100

# Directorio principal del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Directorio donde se almacenará el dataset
DATA_DIR = BASE_DIR / "data"

# Crear directorio si no existe
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Guardar dataset
df.to_csv(DATA_DIR / "dataset_votacion.csv", index=False)

print("Dataset generado:", df.shape)
print(df.head())
print("\nTotal mesas:", len(df), "| Anomalas (ground truth):", df["es_anomalia_real"].sum())
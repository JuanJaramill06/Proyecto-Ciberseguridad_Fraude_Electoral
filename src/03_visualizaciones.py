"""
Proyecto Final 1 - Deteccion de fraude en procesos electorales
Paso 3: Visualizaciones (5 graficas)
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path

# Directorio principal del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Directorios de entrada y salida
RESULTADOS_DIR = BASE_DIR / "resultados"
FIGURAS_DIR = RESULTADOS_DIR / "figuras"

sns.set_theme(style="whitegrid")
df = pd.read_csv(RESULTADOS_DIR / "dataset_con_deteccion.csv")

# Crear directorio para almacenar las visualizaciones
FIGURAS_DIR.mkdir(parents=True, exist_ok=True)

# 1. Distribucion de participacion, normales vs anomalas
plt.figure(figsize=(8, 5))
sns.histplot(data=df, x="participacion_pct", hue="flag_combinado", bins=40,
             palette={True: "crimson", False: "steelblue"}, alpha=0.7)
plt.axvline(95, color="black", linestyle="--", label="Umbral regla (95%)")
plt.title("Distribución de participación electoral por mesa")
plt.xlabel("Participación (%)")
plt.ylabel("Número de mesas")
plt.legend(title="Marcada como anómala")
plt.tight_layout()
plt.savefig(FIGURAS_DIR / "fig1_distribucion_participacion.png", dpi=150)
plt.close()

# 2. Dispersion: participacion vs tiempo de reporte, coloreado por deteccion
plt.figure(figsize=(8, 5))
sns.scatterplot(data=df, x="tiempo_reporte_min", y="participacion_pct",
                 hue="flag_combinado", palette={True: "crimson", False: "steelblue"},
                 alpha=0.7)
plt.title("Participación vs. tiempo de reporte de resultados")
plt.xlabel("Tiempo de reporte (minutos tras el cierre)")
plt.ylabel("Participación (%)")
plt.legend(title="Marcada como anómala")
plt.tight_layout()
plt.savefig(FIGURAS_DIR / "fig2_participacion_vs_tiempo.png", dpi=150)
plt.close()

# 3. Boxplot de z-score de participacion por municipio
plt.figure(figsize=(9, 5))
sns.boxplot(data=df, x="municipio", y="z_participacion", color="lightgray")
sns.stripplot(data=df, x="municipio", y="z_participacion", hue="flag_estadistica",
              palette={True: "crimson", False: "steelblue"}, alpha=0.6, jitter=True)
plt.axhline(3, color="black", linestyle="--")
plt.axhline(-3, color="black", linestyle="--")
plt.title("Z-score de participación por municipio (umbral |z|>3)")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(FIGURAS_DIR / "fig3_zscore_por_municipio.png", dpi=150)
plt.close()

# 4. Porcentaje maximo de un solo candidato por mesa
plt.figure(figsize=(8, 5))
max_pct = df[["pct_A", "pct_B", "pct_C"]].max(axis=1)
sns.histplot(x=max_pct, hue=df["flag_combinado"], bins=40,
             palette={True: "crimson", False: "steelblue"}, alpha=0.7)
plt.axvline(90, color="black", linestyle="--", label="Umbral regla (90%)")
plt.title("Porcentaje del candidato más votado por mesa")
plt.xlabel("% de votos del candidato líder en la mesa")
plt.ylabel("Número de mesas")
plt.legend(title="Marcada como anómala")
plt.tight_layout()
plt.savefig(FIGURAS_DIR / "fig4_concentracion_candidato.png", dpi=150)
plt.close()

# 5. Comparacion de deteccion por tipo de anomalia
plt.figure(figsize=(10, 6))

df_anomalias = df[df["es_anomalia_real"] == 1]

resumen = df_anomalias.groupby("tipo_anomalia").agg(
    reglas=("flag_reglas", "sum"),
    estadistica=("flag_estadistica", "sum")
).reset_index()

resumen = resumen.melt(
    id_vars="tipo_anomalia",
    value_vars=["reglas", "estadistica"],
    var_name="tecnica",
    value_name="mesas_detectadas"
)

sns.barplot(
    data=resumen,
    x="tipo_anomalia",
    y="mesas_detectadas",
    hue="tecnica",
    palette="Set2"
)

plt.title("Deteccion de anomalias por tipo y tecnica")
plt.xlabel("Tipo de anomalia")
plt.ylabel("Mesas detectadas")
plt.xticks(rotation=15)
plt.legend(title="Tecnica")
plt.tight_layout()

plt.savefig(
    FIGURAS_DIR / "fig5_deteccion_por_tipo.png",
    dpi=150
)
plt.close()

print("5 visualizaciones generadas en", FIGURAS_DIR)
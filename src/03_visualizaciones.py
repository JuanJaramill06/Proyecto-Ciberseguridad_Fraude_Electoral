"""
Proyecto Final 1 - Deteccion de fraude en procesos electorales
Paso 3: Visualizaciones (5 graficas)
"""

import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")
df = pd.read_csv("../resultados/dataset_con_deteccion.csv")

OUT = "../resultados/figuras"
os.makedirs(OUT, exist_ok=True)

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
plt.savefig(f"{OUT}/fig1_distribucion_participacion.png", dpi=150)
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
plt.savefig(f"{OUT}/fig2_participacion_vs_tiempo.png", dpi=150)
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
plt.savefig(f"{OUT}/fig3_zscore_por_municipio.png", dpi=150)
plt.close()

# 4. Porcentaje maximo de un solo candidato por mesa
plt.figure(figsize=(8, 5))
max_pct = df[["pct_A", "pct_B", "pct_C"]].max(axis=1)
sns.histplot(x=max_pct, hue=df["flag_combinado"], bins=40,
             palette={True: "crimson", False: "steelblue"}, alpha=0.7)
plt.axvline(90, color="black", linestyle="--", label="Umbral regla (90%)")
plt.title("Porcentaje del candidato más votado por mesa")
plt.xlabel("% de votos del candidato líder en la mesa")
plt.legend(title="Marcada como anómala")
plt.tight_layout()
plt.savefig(f"{OUT}/fig4_concentracion_candidato.png", dpi=150)
plt.close()

# 5. Comparacion de tecnicas (barras): cuantas detecta cada una
plt.figure(figsize=(7, 5))
conteos = {
    "Reglas simples": df["flag_reglas"].sum(),
    "Estadística (z-score)": df["flag_estadistica"].sum(),
    "Combinado (OR)": df["flag_combinado"].sum(),
    "Detectado por ambas": (df["n_tecnicas_que_detectan"] == 2).sum(),
}
plt.bar(conteos.keys(), conteos.values(), color=["#4c72b0", "#dd8452", "#55a868", "#c44e52"])
plt.title("Mesas marcadas por cada técnica de detección")
plt.ylabel("Número de mesas")
plt.xticks(rotation=15)
for i, v in enumerate(conteos.values()):
    plt.text(i, v + 1, str(v), ha="center")
plt.tight_layout()
plt.savefig(f"{OUT}/fig5_comparacion_tecnicas.png", dpi=150)
plt.close()

print("5 visualizaciones generadas en", OUT)
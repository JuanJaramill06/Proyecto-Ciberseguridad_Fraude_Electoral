# Proyecto Final 1 — Detección de fraude en procesos electorales

Integrantes:

* Andrés Felipe Rivas
* Juan Fernando Jaramillo
* María Juliana Niño
* Manuela Marín

## Resumen de hallazgos (borrador para el informe)

### 1. Contexto
Se trabajó con un **dataset simulado** de 500 mesas de votación distribuidas en 5
municipios ficticios (San Rafael, Puerto Alegre, Villa Nueva, El Mirador, Santa Rosa),
con 3 candidatos (A, B, C). Se sembraron a propósito 50 mesas (10%) con comportamientos
anómalos de 4 tipos: sobrevoto, participación excesiva, concentración extrema en un
candidato, y reporte de resultados anormalmente rápido. Esto permite validar objetivamente
si las técnicas de detección funcionan (ground truth conocido).

**Aclaración ética:** todos los datos son simulados. No se hace ninguna afirmación sobre
procesos electorales reales.

### 2. Metodología
Se implementaron las 2 técnicas permitidas por el enunciado:

**Técnica 1 — Reglas simples**, basadas en criterios de sentido común:
- Votos emitidos > votantes habilitados (sobrevoto, matemáticamente imposible)
- Participación > 95% en la mesa
- Un candidato concentra > 90% de los votos de la mesa
- Resultado reportado en menos de 5 minutos tras el cierre

**Técnica 2 — Estadística (z-score)**, calculado *por municipio* (cada municipio tiene
su propia distribución de comportamiento "normal"):
- z-score de participación, tiempo de reporte y % del candidato líder
- Umbral: |z| > 3 (criterio estadístico estándar para outliers)

### 3. Resultados
| Técnica | Mesas detectadas | Precisión | Recall |
|---|---|---|---|
| Reglas simples | 50 | 1.00 | 1.00 |
| Estadística (z-score) | 24 | 1.00 | 0.48 |
| Combinado (OR) | 50 | 1.00 | 1.00 |

- Las **reglas simples** capturan el 100% de las anomalías sembradas porque los umbrales
  (ej. sobrevoto, reporte en <5 min) son condiciones "duras" que no dejan ambigüedad.
- La **estadística** detecta solo la mitad (recall 0.48) porque algunas anomalías
  sembradas (ej. candidato con 95% de votos) no siempre se alejan lo suficiente (>3
  desviaciones estándar) de la distribución del municipio — son más sutiles.
- 24 mesas fueron marcadas por **ambas técnicas simultáneamente**, lo que da mayor
  confianza: son los casos más claros de anomalía.
- Ninguna técnica generó falsos positivos sobre este dataset (precisión = 1.00), aunque
  esto es optimista por tratarse de datos simulados con anomalías bien diferenciadas;
  en datos reales se esperaría más solapamiento entre comportamiento legítimo y atípico.

### 4. Visualizaciones generadas
1. `fig1_distribucion_participacion.png` — Histograma de participación, normal vs anómala
2. `fig2_participacion_vs_tiempo.png` — Dispersión participación vs tiempo de reporte
3. `fig3_zscore_por_municipio.png` — Boxplot de z-score de participación por municipio
4. `fig4_concentracion_candidato.png` — Histograma de concentración de votos por candidato
5. `fig5_comparacion_tecnicas.png` — Barras comparando cuántas mesas detecta cada técnica

### 5. Conclusiones
- Las reglas simples son más efectivas para anomalías "evidentes" (imposibles o claramente
  fuera de rango), pero requieren conocer de antemano qué umbrales tienen sentido.
- La estadística es más flexible (se adapta a cada municipio) pero puede pasar por alto
  anomalías que, aunque sospechosas, no son estadísticamente extremas.
- Combinar ambas técnicas da cobertura completa en este caso, y el cruce entre las dos
  (detectado por ambas) es un buen indicador de "alta confianza" para priorizar revisión.

### 6. Riesgos y limitaciones
- El dataset es simulado y las anomalías fueron sembradas de forma controlada; en datos
  reales las señales son más ruidosas y los umbrales deben calibrarse con cuidado.
- Reglas fijas (ej. "95% de participación es sospechoso") pueden no generalizar a todos
  los contextos (hay zonas con alta participación legítima).
- El análisis no prueba fraude — solo señala *anomalías estadísticas o de reglas* que
  ameritan revisión manual adicional.

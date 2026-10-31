# Informe del torneo de modelos

> Resultado de `notebooks/05_torneo.ipynb` (ejecutado el 31 oct 2026; todas las cifras salen de su salida). El torneo
> **descarta**: elige 1–2 finalistas con evidencia, no un campeón definitivo. Guía:
> `material-del-curso/kit/guia-modelado-y-optimizacion.md`, sección 2.

## Reglas del torneo

- **Mismos datos y mismos pliegues para todos** (partidos por qué entidad): los 57.286 estudiantes de entrenamiento
  (la prueba no se abrió), en 5 pliegues `GroupKFold` por sede (`cole_cod_dane_sede`, `group_cv()` de
  `src/proyecto/data/split.py`), de 11.457–11.458 estudiantes de validación cada uno. El notebook comprueba que ninguna
  sede cae a los dos lados de un pliegue y que los pliegues no cambian entre candidatos.
- **Línea base** (qué es y cuánto da): `DummyRegressor(strategy="median")`, predecir siempre la mediana del entrenamiento
  de cada pliegue. MAE 42,83 ± 0,60, igual a la del caso de negocio (42,8).
- **Métrica principal** (la del negocio) y **métricas técnicas**: MAE en puntos, en positivo (los dos errores cuestan lo
  mismo). Técnicas de regresión: RMSE (errores grandes), R² (variación explicada), RMSE / MAE y error relativo (MAE ÷
  puntaje medio de entrenamiento, 246,4). Además, segundos de ajuste por pliegue. Todas calculadas por
  `evaluate_folds` / `regression_metrics` de `src/proyecto/models/train.py`.
- **Variables usadas** (las decididas en `reports/04_features.md`): variables base, sin las nuevas
  (`use_engineered=False`), umbral de poco frecuentes `min_frequency` = 1 %. Escalado solo para Ridge.
- **Meta** (`especificacion-proyecto.md`, sección 4): MAE ≤ 38 (mínima) y ≤ 35 (deseable) en validación agrupada por sede.
- **Candidatos (decisión del grupo, 31 oct 2026):** línea base (mediana), Ridge, Random Forest,
  `HistGradientBoostingRegressor` (en lugar de LightGBM) y XGBoost, con los parámetros de partida del ejemplo
  (`specs/003-model-training/research.md` §2), semilla 42. Los dos boosting con su pérdida por defecto (cuadrática).
  **LightGBM se reemplazó** porque no carga en Windows sin el Visual C++ Redistributable y el grupo no tiene permisos para
  instalarlo; HistGradientBoosting usa la misma técnica que LightGBM (boosting con histogramas), no requiere instalar nada
  adicional y funciona en el equipo de todos los integrantes, lo que cuida la reproducibilidad.

## Tabla comparativa

> Media ± desviación entre los 5 pliegues. Ordenada por MAE (menor es mejor).

| Modelo | MAE (± ruido) | Mejora vs línea base | Meta mínima (≤ 38) | Meta deseable (≤ 35) | Segundos de ajuste |
|---|---|---|---|---|---|
| HistGradientBoosting | 33,56 (± 0,24) | 9,26 puntos (21,6 %) | sí | sí | 7,8 |
| XGBoost | 33,66 (± 0,21) | 9,17 puntos (21,4 %) | sí | sí | 3,3 |
| Random Forest | 34,75 (± 0,30) | 8,08 puntos (18,9 %) | sí | sí | 53,1 |
| Ridge | 34,78 (± 0,21) | 8,05 puntos (18,8 %) | sí | sí | 1,4 |
| Línea base (mediana) | 42,83 (± 0,60) | — | no | no | 1,5 |

Los segundos son la media por pliegue e incluyen el ajuste del preprocesamiento (por eso la línea base no es ~0). Random
Forest y Ridge quedan bajo 35 por poco: en un pliegue cada uno supera 35 (35,17 y 35,03).

MAE por pliegue (los mismos 5 pliegues):

| Modelo | P0 | P1 | P2 | P3 | P4 |
|---|---|---|---|---|---|
| HistGradientBoosting | 33,61 | 33,64 | 33,90 | 33,40 | 33,26 |
| XGBoost | 33,66 | 33,67 | 33,94 | 33,67 | 33,35 |
| Random Forest | 34,88 | 34,74 | 35,17 | 34,43 | 34,51 |
| Ridge | 34,70 | 34,93 | 35,03 | 34,50 | 34,72 |
| Línea base | 43,19 | 43,05 | 42,85 | 43,26 | 41,79 |

## Métricas técnicas

> Media entre pliegues, con la misma validación. Las métricas de clasificación de la plantilla (AUC, PR-AUC, recall por
> clase, F1, log loss) no aplican: es regresión. Se reemplazan por las de la guía, sección 2.2.

| Modelo | MAE | RMSE (± ruido) | R² (± ruido) | RMSE / MAE | Error relativo |
|---|---|---|---|---|---|
| HistGradientBoosting | 33,56 | 41,50 (± 0,32) | 0,349 (± 0,017) | 1,236 | 13,6 % |
| XGBoost | 33,66 | 41,62 (± 0,24) | 0,345 (± 0,015) | 1,237 | 13,7 % |
| Random Forest | 34,75 | 43,03 (± 0,45) | 0,299 (± 0,023) | 1,239 | 14,1 % |
| Ridge | 34,78 | 42,82 (± 0,29) | 0,306 (± 0,021) | 1,231 | 14,1 % |
| Línea base | 42,83 | 51,71 (± 0,86) | −0,011 (± 0,017) | 1,208 | 17,4 % |

## ¿Coinciden los rankings de negocio y técnico?

> Posición de cada modelo (1 = mejor).

| Modelo | MAE (negocio) | RMSE | R² | Segundos de ajuste |
|---|---|---|---|---|
| HistGradientBoosting | 1 | 1 | 1 | 4 |
| XGBoost | 2 | 2 | 2 | 3 |
| Random Forest | 3 | 4 | 4 | 5 |
| Ridge | 4 | 3 | 3 | 1 |
| Línea base | 5 | 5 | 5 | 2 |

- **¿El mejor por MAE también es el mejor por RMSE y R²?** Sí: HistGradientBoosting es 1.º en las tres y XGBoost 2.º en
  las tres. El mejor en el error típico no lo logra a costa de más errores grandes.
- **¿Hay modelos con MAE casi igual pero RMSE distinto?** Random Forest y Ridge empatan en MAE (34,75 y 34,78), pero
  Random Forest tiene peor RMSE (43,03 frente a 42,82) y peor R² (0,299 frente a 0,306): comete algo más de errores
  grandes. RMSE / MAE es casi igual en los cuatro modelos (1,23–1,24): ninguno concentra errores extremos.
- **¿Algún modelo no explica nada (R² ≤ 0)?** Solo la línea base (−0,011). Los modelos explican entre el 30 % y el 35 %
  de la variación del puntaje.

## Comparación pareada de los mejores

> Todos se evaluaron en los mismos pliegues. Diferencia = MAE (o RMSE) del otro − el del mejor; positivo: gana el mejor.
> Ruido = desviación de esas diferencias entre pliegues.

| Mejor | Contra | Métrica | Diferencia media | Pliegues que gana | Diferencia / ruido |
|---|---|---|---|---|---|
| HistGradientBoosting | XGBoost | MAE | 0,095 | 5 de 5 | 0,95 |
| HistGradientBoosting | Random Forest | MAE | 1,182 | 5 de 5 | 10,57 |
| HistGradientBoosting | Ridge | MAE | 1,213 | 5 de 5 | 7,74 |
| HistGradientBoosting | Línea base | MAE | 9,263 | 5 de 5 | 17,58 |
| XGBoost | Random Forest | MAE | 1,088 | 5 de 5 | 5,61 |
| HistGradientBoosting | XGBoost | RMSE | 0,125 | 5 de 5 | 1,14 |
| HistGradientBoosting | Random Forest | RMSE | 1,539 | 5 de 5 | 8,69 |
| HistGradientBoosting | Ridge | RMSE | 1,324 | 5 de 5 | 5,74 |
| XGBoost | Random Forest | RMSE | 1,415 | 5 de 5 | 5,50 |

- Los dos boosting ganan a Random Forest y a Ridge en los 5 pliegues, con diferencias de 5,5 a 10,6 veces el ruido:
  ventaja consistente.
- HistGradientBoosting gana a XGBoost en los 5 pliegues, pero en MAE por 0,095 puntos y 0,95 veces el ruido (< 1):
  **empate práctico**. En RMSE la razón es 1,14, apenas sobre 1.

## ¿Cuánto vale la diferencia?

No hay dinero en juego: se traduce a puntos de error y estudiantes. La prueba es anual; el volumen es la cohorte de 2022
tras la limpieza (72.148 estudiantes de calendario A en Antioquia, notebook 03).

- **Decisiones estimadas:** una estimación por estudiante; 72.148 al año si se usara con toda la cohorte.
- **Ahorro frente a la línea base:** 9,26 puntos de error por estudiante con HistGradientBoosting (≈ 668.000 puntos en la
  cohorte) y 9,17 con XGBoost (≈ 661.000).
- **Diferencia entre el mejor y el siguiente:** 0,095 puntos por estudiante (HistGradientBoosting frente a XGBoost), menos
  de una décima de punto en un puntaje de 0 a 500: no cambia ninguna decisión de la app.

## Finalistas

| Finalista | Por qué (consistencia, métrica, tiempo, interpretabilidad) | Qué podría cambiar con la optimización |
|---|---|---|
| HistGradientBoosting | Mejor MAE (33,56 ± 0,24), RMSE y R²; gana a Random Forest y a Ridge en 5 de 5 pliegues (10,6 y 7,7 veces el ruido). Cumple la meta deseable en todos los pliegues | Pérdida de error absoluto (`loss="absolute_error"`), tasa de aprendizaje, hojas e iteraciones; probar `min_frequency` 0,1 % (candidato de la etapa 4) |
| XGBoost | Empate práctico con el mejor (0,095 puntos, 0,95 veces el ruido) y 2,4 veces más rápido (3,3 s frente a 7,8 s por ajuste), lo que abarata la búsqueda de la etapa 6. Gana a Random Forest en 5 de 5 (5,6 veces el ruido) y cumple la meta deseable en todos los pliegues | Pérdida `reg:absoluteerror`, profundidad, tasa de aprendizaje y regularización; probar `min_frequency` 0,1 % |

**Modelos descartados y por qué:** Random Forest: 1,18 puntos peor que el mejor en los 5 pliegues y el más lento (53 s por
ajuste, 16 veces XGBoost). Ridge: 1,21 puntos peor en los 5 pliegues; es el más rápido y el más interpretable, pero el
caso no exige interpretabilidad por regulación y la interpretación se cubrirá en la etapa 7. Si el grupo valorara más la
interpretabilidad, el costo de elegir Ridge sería ~1,2 puntos de MAE por estudiante. Línea base: no cumple la meta.

**Por qué el torneo no elige un campeón:** los dos boosting están empatados dentro del ruido, así que la optimización de
la etapa 6 (por ejemplo, entrenarlos con error absoluto) puede invertir el orden. Además, todas las cifras son de
validación cruzada con el entrenamiento: solo la prueba final (etapa 7), con sedes que el modelo nunca vio, dirá qué tan
bien funciona el modelo elegido.

## Efectos que la métrica principal no ve

- **Errores grandes:** RMSE / MAE es ~1,24 en todos los modelos; ningún candidato gana en MAE a costa de errores muy
  grandes. Aun así, un RMSE de ~41,5 indica que hay estudiantes con errores bastante mayores que el típico.
- **Variación no explicada:** con R² ≈ 0,35, el modelo explica alrededor de un tercio de la variación del puntaje; el
  resto depende de información que la app no pregunta. La estimación orienta, no etiqueta.
- **Equidad no medida aquí:** el MAE promedio puede esconder segmentos (estrato, zona, naturaleza del colegio) donde el
  modelo es peor que la línea base. La condición de equidad se revisa en la etapa 7.
- **Pérdida por defecto:** los boosting se entrenaron con error cuadrático y se evaluaron con MAE; entrenarlos con error
  absoluto queda para la etapa 6.

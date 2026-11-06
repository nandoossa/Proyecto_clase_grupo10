# Especificación · Etapa 7 · Validación e interpretación (la prueba se abre una sola vez)

> Se llena **antes** de abrir `data/processed/test.joblib`, a partir de `reports/06_optimizacion.md`,
> `reports/06_best_params.json` y `reports/00_caso.md`. Claude la lee y la implementa; ustedes revisan que el código haga
> **exactamente** esto (`material-del-curso/kit/checklist-revision-ia.md`). Guía:
> `material-del-curso/kit/guia-validacion-registro-y-app.md`, secciones 1 a 4.

**Grupo:** Predictor de resultados Pruebas Saber 11 en Antioquia   **Fecha:** 5 nov 2026   **Estado:** ☐ borrador  ☒ cerrada (falta la revisión del grupo con el checklist)

> Borrador preparado por Claude a partir del pedido del grupo del 5 nov 2026. **La prueba no se ha abierto.** Ninguna cifra
> de la prueba está escrita aquí; se llenan después de ejecutar el notebook 07.

## 1. Decisiones congeladas (antes de abrir la prueba)

| Decisión | Valor | Cómo se decidió |
|---|---|---|
| Modelo final | `HistGradientBoostingRegressor` | Etapa 6, regla 2: empate con XGBoost en las sedes reservadas (−0,048, IC [−0,222 ; +0,119]) → HGB por el desempate aprobado |
| Parámetros | Optimizados de `reports/06_best_params.json`: `min_frequency` 0,001, `loss="absolute_error"`, `learning_rate` 0,0301, `max_iter` 587, `max_leaf_nodes` 16, `min_samples_leaf` 82, `l2_regularization` 0,3657, `max_features` 0,6155; `early_stopping=False`, `random_state=42` | Etapa 6, regla 1: mejora en sedes reservadas con IC [−0,640 ; −0,118], completo bajo cero |
| Entrenamiento | **Todo** `train.joblib` (57.286 estudiantes, 1.155 sedes; búsqueda + sedes reservadas) | Las sedes reservadas ya cumplieron su papel |
| ¿Calibrar? | **No aplica**: es regresión, no hay probabilidades ni umbral | — |
| Métrica principal | MAE (puntos); controles RMSE y R² | `especificacion-proyecto.md` §4 |
| Regla de decisión | No hay: la app muestra el puntaje estimado | Regresión |
| Línea base | `DummyRegressor(strategy="median")` ajustado con todo el entrenamiento (predice siempre la mediana del entrenamiento) | La del torneo |
| Metas | Mínima MAE ≤ 38; deseable MAE ≤ 35 | `especificacion-proyecto.md` §4 |
| Regla de equidad | Un segmento **cumple** si el MAE del modelo es **estrictamente menor** que el de la línea base en ese segmento. Los que cumplen se clasifican con el intervalo del 95 % (por sedes) de la diferencia modelo − línea base: **«cumple con ventaja clara»** si el intervalo excluye el cero; **«cumple sin ventaja concluyente»** si lo incluye. El intervalo no cambia el veredicto. Cada segmento se reporta con su número de estudiantes y de sedes | `reports/00_caso.md`; clasificación aprobada por el grupo el 5 nov 2026 |

**Sección 1 aprobada por el grupo el 5 nov 2026, antes de abrir la prueba.**

Las decisiones se guardan con fecha y hora en `reports/07_decisiones_congeladas.json` **antes** de abrir la prueba.

## 2. Apertura única de la prueba

- El notebook escribe la marca `reports/prueba_abierta.txt` (fecha, hora, filas y sedes) la primera vez que abre la prueba.
- Las predicciones del modelo y de la línea base sobre la prueba, y la importancia por permutación, se guardan en
  `data/processed/prueba_resultados.joblib` (no se sube a Git). Si el notebook se vuelve a ejecutar, **reutiliza** esos
  resultados y no vuelve a evaluar el modelo con la prueba.
- **Nada se ajusta después de ver la prueba.** Si algo sale mal, se anota como límite del modelo.
- Nota de transparencia: `test.joblib` se regeneró el 5 nov 2026 al ejecutar el notebook 03 (misma partición, semilla 42),
  sin leerlo.

## 3. Métricas e intervalos

- Modelo y línea base: MAE, RMSE y R² en la prueba.
- Intervalo del 95 % con 1.000 remuestreos de **sedes completas** para cada métrica y para la **diferencia** modelo − línea
  base (MAE, RMSE y R²).
- **¿Mejora a la línea base con confianza?** Sí, si todo el intervalo de la diferencia de MAE está bajo cero.
- **Metas:** se informa si el MAE puntual cumple ≤ 38 y ≤ 35, y si el **límite superior** del intervalo también las cumple.

## 4. Condición de equidad (por segmento)

Segmentos (los de `reports/00_caso.md` más género, pedido del grupo):

| Variable | Segmentos |
|---|---|
| Estrato (`fami_estratovivienda` + `sin_estrato`) | Estrato 1 … 6; «Sin Estrato» (`sin_estrato` = 1); «Sin dato (vacío)» (vacío y `sin_estrato` = 0) |
| Zona (`cole_area_ubicacion`) | Urbano, Rural |
| Naturaleza (`cole_naturaleza`) | Oficial, No oficial |
| Género (`estu_genero`) | F, M (y vacío si existe) |

Por segmento: número de estudiantes, número de sedes, MAE del modelo, MAE de la línea base, diferencia e intervalo del 95 %
por sedes.

- **Regla (escrita antes de mirar, `reports/00_caso.md`):** la condición se **cumple** en un segmento si el MAE del modelo es
  **menor** que el de la línea base en ese segmento. Se informa en cuáles se cumple y en cuáles no, sin maquillar.
- El intervalo no cambia la regla, pero clasifica a los que cumplen: «cumple con ventaja clara» (el intervalo de la
  diferencia excluye el cero) o «cumple sin ventaja concluyente» (lo incluye).
- Si un segmento no cumple, se dice claramente y se anota como límite; no se cambia el modelo.

## 5. Interpretación

- Importancia por permutación (`sklearn.inspection.permutation_importance`) **sobre la prueba**, con el MAE como métrica
  (`neg_mean_absolute_error`), 5 repeticiones, semilla 42, permutando las **columnas originales** que usa el modelo (las 21
  del preprocesador; la sede no). Importancia = cuánto sube el MAE al desordenar esa columna.
- Explicación en lenguaje simple de los factores que más influyen, con sus límites: explica al modelo, no al mundo; las
  variables correlacionadas se reparten el crédito; importancia no es causa.
- Atributos sensibles entre las variables (género, estrato, zona, ubicación): se declaran y se dice qué peso tienen.

## 6. Entradas y salidas

| | Ruta |
|---|---|
| Entrada | `data/processed/train.joblib`, `data/processed/test.joblib` (una vez), `reports/06_best_params.json` |
| Código | `src/proyecto/models/evaluation.py`: segmentos de estrato, tabla de equidad, diferencia de métricas por sede, importancia por permutación |
| Pruebas | `tests/test_evaluation.py` |
| Notebook | `notebooks/07_validacion_interpretacion.ipynb` |
| Salidas | `reports/07_validacion.md`, `reports/07_decisiones_congeladas.json`, `reports/prueba_abierta.txt`, `reports/07_metricas_test.json`, `reports/07_equidad.csv`, `reports/07_importancia.csv`; `models/final_pipeline.joblib` (no se sube) |

## 7. Pruebas que deben existir

- ☒ Los segmentos de estrato separan «Sin Estrato» de «Sin dato (vacío)» y nunca convierten un vacío en estrato 0.
- ☒ La tabla de equidad cuenta bien los estudiantes, calcula el MAE de cada segmento y marca «cumple» solo si el modelo es
  estrictamente mejor.
- ☒ La diferencia de una métrica remuestrea sedes (con una sola sede el intervalo no tiene ancho) y su valor puntual es
  exactamente métrica(A) − métrica(B).
- ☒ La importancia por permutación da ~0 a una columna que el modelo no usa y > 0 a la que define el objetivo.
- ☒ `pytest` en verde (82 de 82, 5 nov 2026).

## 8. Criterios de cierre

- ☒ Decisiones congeladas con fecha y hora antes de abrir la prueba; marca de apertura única.
- ☒ `reports/07_validacion.md` con métricas, intervalos, metas, equidad por segmento e interpretación, **solo con cifras de
  la ejecución**; los segmentos que no cumplen se dicen claramente.
- ☒ Auditoría con `auditor-de-fuga` en `reports/auditoria_etapa7.md`.
- ☒ Todo subido a GitHub.
- ☐ Revisión del código de Claude por el grupo con `material-del-curso/kit/checklist-revision-ia.md`.

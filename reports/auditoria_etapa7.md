# Auditoría de fuga de información, etapa 7 (validación final e interpretación)

**Fecha:** 5 nov 2026
**Proyecto:** Predictor de resultados Saber 11 en Antioquia. Regresión de `punt_global`, métrica MAE, entidad repetida `cole_cod_dane_sede`.
**Auditor:** subagente `auditor-de-fuga` (solo lectura, no se modificó ningún archivo)

> Informe copiado sin cambios del subagente. Lo que se hizo con cada hallazgo está al final, en «Seguimiento».

## 1. Alcance

Archivos revisados, con lectura completa:
- `src/proyecto/models/evaluation.py`
- `notebooks/07_validacion_interpretacion.ipynb` (código y salidas guardadas)
- `tests/test_evaluation.py`
- `reports/07_decisiones_congeladas.json`
- `reports/prueba_abierta.txt`
- `reports/07_metricas_test.json`
- `reports/07_equidad.csv`
- `reports/07_importancia.csv`

Contexto leído:
- `especificaciones/07-validacion.md`
- `reports/06_best_params.json`
- `src/proyecto/models/tuning.py`
- `src/proyecto/models/train.py` (`feature_frame`, `regression_metrics`, `build_pipeline`)
- `src/proyecto/data/split.py`
- `src/proyecto/features/engineering.py`
- `reports/01_eda.md` (sección de fuga)
- `tests/test_split.py`
- `.gitignore`
- Parte de `reports/07_validacion.md`

**Lo que no pude comprobar:**
- No ejecuté `pytest`. No puedo afirmar que esté en verde.
- No abrí `train.joblib`, `test.joblib` ni `prueba_resultados.joblib`. No miré las fechas de modificación de los archivos. No tuve intérprete para ejecutar código.
- No tengo cómo verificar el ensayo general en la carpeta temporal. Lo tomo como dato de proceso que me dieron.
- No leí `reports/06_optimizacion.md` completo ni `tests/test_models.py::_frame`.
- No verifiqué que la etapa 6 usara `use_engineered=False`. El notebook 07 usa `build_tuned_pipeline`, que por defecto no usa las variables nuevas. Conviene confirmarlo contra el notebook 06.

## 2. Veredicto

**Sin fuga evidente.** No encontré ninguna fuga de información ni uso indebido de la prueba que invalide las cifras de la etapa 7.

Sí hay **6 puntos de endurecimiento**: 0 graves, 1 media y 5 bajas. Son mejoras al proceso, no errores en el resultado. Se listan en la sección 4.

## 3. Respuesta a cada pregunta

**1. ¿El orden del notebook garantiza que las decisiones se escriben antes de abrir la prueba y que no se reescriben después?**
En lo esencial, sí.
- Celda `20d5075a`: arma las decisiones y escribe `07_decisiones_congeladas.json`. Solo usa `06_best_params.json` y constantes. Aparece antes de cualquier `joblib.load(TEST_PATH)`, que está en la celda `b60ce8cf`, dentro del `else`.
- Las fechas son coherentes: congeladas 19:53:16, abierta 19:55:52, es decir 2 min 36 s después. Eso cuadra con entrenar 587 árboles en la celda `5b9d5215`, que va entre ambas.
- Si el JSON y la marca ya existen, las decisiones se releen del JSON y no se reescriben.
- **Matiz (hallazgo H1):** la protección depende de que existan los dos archivos. Si se borra el JSON pero queda la marca, se reescribe con fecha posterior a la apertura, en silencio.
- **Matiz (hallazgo H2):** la fecha la genera el mismo notebook. No hay evidencia externa del orden, porque el JSON y la marca están sin commit en Git.

**2. ¿El mecanismo de caché/marca impide reevaluar con la prueba al re-ejecutar?**
Sí, en el uso normal.
- Marca y caché presentes: reutiliza resultados y no abre la prueba.
- Marca presente y sin caché: lanza `RuntimeError`. Es el caso de un clon nuevo del repositorio, porque `data/processed/*` está en `.gitignore`.
- Marca ausente: abre la prueba.
- **Límites (H3):** el candado son dos archivos que se pueden borrar. No hay huella (hash) de `test.joblib`. La caché se escribe antes que la marca; si el proceso se cae entre ambas, queda caché sin marca y se reabriría.

**3. ¿El modelo y la línea base se ajustan solo con entrenamiento?**
Sí.
- Celda `5b9d5215`: `build_tuned_pipeline(...).fit(X_train, y_train)` y `DummyRegressor("median").fit(X_train, y_train)`.
- `X_train` sale de `train.joblib` completo: 57.286 estudiantes y 1.155 sedes. Ese número coincide con el declarado en la especificación antes de abrir la prueba.
- Imputador, codificador y modelo están dentro del `Pipeline` (`engineering.py:150-165`, `build_pipeline` en `train.py`). Se ajustan solo con entrenamiento.
- La línea base predice 243, la mediana del entrenamiento.
- Ninguna celda reajusta el modelo después de abrir la prueba.
- El `assert` de la celda `5b9d5215` comprueba los hiperparámetros del modelo, pero no `min_frequency`, que es del preprocesador (H6, baja).

**4. ¿Alguna celda usa la prueba para elegir algo?**
No.
- La prueba aparece en tres sitios: dentro del `else` de la celda `b60ce8cf` (predicciones, segmentos, importancia), en la sección 5 (métricas) y en la sección 6 (equidad).
- Los umbrales (38 y 35), la regla de equidad y el modelo se fijaron antes, en el JSON y en `especificaciones/07-validacion.md` §1, que dice estar aprobada antes de abrir la prueba.
- La clasificación «ventaja clara / sin ventaja concluyente» usa el intervalo, pero no cambia «cumple», como declara la regla.
- Los resultados no retroalimentan nada. Solo se guardan en reports.

**5. ¿Se verifica que las sedes de la prueba no estén en el entrenamiento?**
Sí.
- Celda `b60ce8cf`: `assert set(test[GROUP_COL]).isdisjoint(set(train[GROUP_COL]))`, antes de predecir. El assert ocurre antes de escribir la marca, así que un fallo no consume la apertura.
- Además, `split_by_group` usa `GroupShuffleSplit` y `assert_disjoint_groups` (`split.py:14-34`).
- Los números cuadran: 1.155 + 289 = 1.444 sedes, y el 20 % de 1.444 es 288,8, es decir 289.
- Prueba automática de la partición: existe en `tests/test_split.py:23-24` y `:43-44`. La segunda demuestra que `train_test_split` por fila **sí** mezcla sedes. Cumple el punto 5 de la lista del auditor.

**6. ¿Los intervalos y la tabla de equidad agrupan por sede?**
Sí.
- `bootstrap_metric_ci` y `bootstrap_mae_difference` (`tuning.py:192-223`) remuestrean sedes completas.
- `bootstrap_metric_difference` (`evaluation.py:43-59`) hace lo mismo para RMSE y R², con las mismas sedes para A y B (comparación pareada).
- `equity_table` (`evaluation.py:79`) pasa `groups[mask]`. El remuestreo es por sede dentro de cada segmento, y reporta el número de sedes por segmento.
- `tests/test_evaluation.py:55-56` comprueba que con una sola sede el intervalo no tiene ancho.

**7. ¿La importancia por permutación usa solo las columnas del modelo y no filtra nada al modelo?**
Sí.
- En la celda `b60ce8cf` se pasa `X_test[cols]`, con `cols = model_columns()`: 21 columnas, sin sede ni objetivo.
- `evaluation.py:105-109` permuta y devuelve solo esas columnas. El CSV tiene 21 filas.
- Se calcula con el modelo ya entrenado. No lo modifica y no hay celda posterior que descarte variables según este resultado.
- El informe `reports/07_validacion.md` (línea 140) remite cualquier ajuste futuro a un trabajo nuevo con validación.
- Es uso interpretativo, pedido por el grupo. Ver recomendación R3.

**8. ¿Hay variables con fuga o identificadores entre los predictores?**
No.
- Las 21 columnas son `NUMERIC_BASE` (5), `CATEGORICAL_BASE` (14) y los 2 códigos de municipio (`engineering.py:16-40`).
- Ninguna está en `FORBIDDEN_COLUMNS` (`engineering.py:48-67`). Esa lista incluye los 5 puntajes por área, `desemp_ingles`, `estu_estadoinvestigacion`, `estu_consecutivo`, la fecha de nacimiento y los códigos de sede y establecimiento. Coincide con las sospechas del EDA.
- La sede va en `X` pero el preprocesador usa `remainder="drop"`.
- `edad` (puesto 1) y `cole_jornada` (puesto 2) son datos conocidos antes del examen. Las variables del colegio son constantes por sede, pero como la prueba son sedes nuevas, la evaluación mide justamente esa generalización.

**9. ¿Las cifras son plausibles?**
Sí, no son sospechosamente perfectas.

| Métrica | Modelo | Línea base |
|---|---|---|
| MAE | 33,32 | 43,09 |
| RMSE | 41,46 | 51,97 |
| R² | 0,363 | −0,0006 |

- El MAE de prueba (33,32) es casi igual al MAE de validación cruzada por sede de la etapa 6 (33,40) y al de las sedes reservadas (33,675).
- Una fuga real daría un MAE mucho menor en la prueba o un R² cercano a 1.
- La importancia máxima es de 2,5 puntos de MAE, sin ninguna variable dominante.
- Línea base con R² ≈ 0 en la prueba: coherente con predecir una constante.

## 4. Hallazgos

| # | Dónde | Gravedad | Descripción | Cómo corregir |
|---|---|---|---|---|
| H1 | Notebook 07, celda `20d5075a`: `if DECISIONS_PATH.exists() and MARKER.exists()` | Media | Si se borra el JSON y queda la marca, la rama `else` reescribe las decisiones con fecha y hora posteriores a la apertura, sin avisar. Las decisiones viven en un solo archivo no versionado. | Antes del `if`, agregar `if MARKER.exists() and not DECISIONS_PATH.exists(): raise RuntimeError(...)`. Además, comprobar que `decisions["parametros"]` coincide con `06_best_params.json` y avisar si no. |
| H2 | `reports/07_decisiones_congeladas.json` y `reports/prueba_abierta.txt` (sin commit según `git status`) | Baja | El orden «congelar y luego abrir» solo está probado por fechas que escribe el mismo notebook. No hay constancia externa. | Hacer commit de estos dos archivos y de las métricas ya. En etapas futuras, hacer commit del JSON **antes** de ejecutar la apertura, para que el historial de Git pruebe el orden. |
| H3 | Celda `b60ce8cf`, ramas de `MARKER`/`CACHE`; `joblib.dump(results, CACHE)` y después `MARKER.write_text` | Baja | La caché se escribe antes que la marca. Si el proceso falla entre ambas, la prueba podría reabrirse. Borrar los dos archivos permite reabrir. No hay huella de `test.joblib`. | Escribir la marca primero (o ambas de forma atómica). Guardar en la marca el hash SHA-256 de `test.joblib` y el del modelo. Verificarlo al re-ejecutar. |
| H4 | Celda `5b9d5215`: `joblib.dump(final_model, ...)` sin condición | Baja | Cada re-ejecución reentrena y sobrescribe `models/final_pipeline.joblib`, aunque las predicciones guardadas vengan del modelo anterior. Con la misma semilla debería salir igual, pero no se verifica. | Si la marca existe, cargar el modelo guardado en lugar de reentrenar. O guardar el hash del modelo junto con la marca. |
| H5 | Celda `d7a2acfd` y `evaluation.py:62-88` (regla de equidad) | Baja (metodológica, no es fuga) | «Cumple» compara contra una constante global. Casi cualquier modelo la supera en todos los segmentos: salieron 14 de 14 «con ventaja clara». Son 14 intervalos sin ajuste por comparaciones múltiples. El MAE del Estrato 5 (39,57) supera la meta global de 38, aunque «cumple». Los segmentos con pocas sedes (Estrato 6: 61, Estrato 5: 89) tienen intervalos amplios. | No cambiar la regla ahora, porque estaba aprobada antes de abrir la prueba. Documentarlo como límite en `07_validacion.md`: «cumple» significa «mejor que predecir la mediana», no «igual de bueno para todos». |
| H6 | Celda `5b9d5215`: `assert ... if k != "min_frequency"` | Baja | No se comprueba que el preprocesador use `min_frequency = 0,001`. | Agregar la comprobación sobre `final_model.named_steps` (el codificador). |
| H7 | `tests/test_evaluation.py:21`: `from test_models import _frame` | Baja (mantenimiento) | La importación entre archivos de prueba depende de cómo se ejecute `pytest`. No afecta la fuga. | Mover `_frame` a `tests/conftest.py`. |
| H8 | `evaluation.py:104` (comentario) | Baja | `permutation_importance_table` permuta todas las columnas de `X` y luego filtra con `.loc`. Es inocuo, pero si alguien pasa `X` completo se gasta tiempo en columnas que no cuentan. | Filtrar `X[columns]` dentro de la función. |

No hay hallazgos de gravedad alta.

## 5. Recomendaciones

- **R1.** Hacer commit ahora de `07_decisiones_congeladas.json`, `prueba_abierta.txt`, `07_metricas_test.json`, `07_equidad.csv`, `07_importancia.csv`, `07_validacion.md` y el código. Es la evidencia externa del orden de la etapa 7.
- **R2.** Aplicar H1 y H3 antes de la etapa 8. Son cambios de pocas líneas y cierran los dos modos de reapertura accidental.
- **R3.** Dejar escrito que la importancia por permutación sobre la prueba es solo descriptiva. Ningún cambio al modelo, a las variables o al umbral debe derivarse de ella. Si el grupo quiere podar variables, debe hacerlo con validación por sede en un ciclo nuevo y declarar que la prueba ya se usó.
- **R4.** En la nota de transparencia, mencionar que el ensayo general usó solo `train.joblib` (dato de proceso, no verificable por mí) y que `test.joblib` se regeneró con el notebook 03.
- **R5.** En el informe, citar la concordancia entre MAE de prueba y de validación por sede como evidencia de que no hay fuga.
- **R6.** Ejecutar `pytest` completo antes de cerrar la etapa y confirmar que `tests/test_split.py` y `tests/test_evaluation.py` pasan.

Veredicto final: sin fuga evidente; hay 0 problemas graves y 8 mejoras menores de proceso (H1 a H8) que conviene aplicar antes de seguir.

## Seguimiento (5 nov 2026)

- **Conteo:** el veredicto de la sección 2 dice «6 puntos» y la tabla tiene 8 (H1 a H8: 1 media y 7 bajas). Vale la tabla.
- **H2 / R1:** atendido. Los archivos de la etapa 7 (decisiones congeladas, marca de apertura, métricas, equidad, importancia,
  informe y código) se suben en el commit de cierre de la etapa. El historial de Git queda como constancia externa.
- **H5:** atendido en `reports/07_validacion.md` §4 («cómo leer “cumple”»). La regla no se cambió: estaba aprobada antes.
- **R3:** atendido en `reports/07_validacion.md` §5 («uso solo descriptivo»).
- **R4 y R5:** ya estaban en `reports/07_validacion.md` §3 (transparencia, y comparación con las etapas 5 y 6).
- **R6:** `pytest` completo en verde (82 de 82) antes del commit.
- **H1, H3, H4 y H6:** atendidos el 5 nov 2026 (pedido del grupo, antes de la etapa 8), sin volver a evaluar con la prueba:
  - **H1:** si existe la marca de apertura y falta `07_decisiones_congeladas.json`, el notebook se detiene (no reescribe).
    Si existe, lo relee y se detiene si `06_best_params.json` ya no coincide con lo congelado.
  - **H3:** en una apertura nueva, la marca se escribe **antes** de evaluar (si algo falla a mitad, el notebook se detiene
    en vez de reabrir). Se guardan huellas SHA-256 de `test.joblib`, `final_pipeline.joblib` y `prueba_resultados.joblib` en
    `reports/prueba_huellas.json`; para la apertura del 5 nov se calcularon después, y las fechas de modificación muestran
    que los tres archivos no cambiaron desde entonces. Al reutilizar, se verifica la huella de los resultados guardados.
  - **H4:** si la prueba ya se abrió, el notebook **carga** el modelo evaluado (verificando su huella) en vez de reentrenar.
  - **H6:** se comprueba que el one-hot del preprocesador usa `min_frequency` = 0,001.
  - **Comprobación:** el notebook 07 se volvió a ejecutar; reutilizó los resultados guardados y los cinco archivos de
    resultados (`07_metricas_test.json`, `07_equidad.csv`, `07_importancia.csv`, `07_decisiones_congeladas.json`,
    `prueba_abierta.txt`) quedaron **idénticos byte a byte**; el modelo y los resultados guardados conservan su huella.
- **H7 y H8** (mantenimiento: mover `_frame` a `tests/conftest.py` y filtrar `X[columns]` dentro de
  `permutation_importance_table`): **anotados como pendientes**.

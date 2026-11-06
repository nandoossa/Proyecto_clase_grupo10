# Auditoría de fuga de información · Etapa 6 (optimización de hiperparámetros)

**Fecha:** 5 nov 2026
**Auditor:** subagente `auditor-de-fuga` (solo lectura; no se modificó ningún archivo)

> Informe copiado sin cambios del subagente. La auditoría se hizo sobre el código definitivo y sobre las salidas de la
> ejecución local (idéntica en código); la ejecución con tracking en Databricks corría en paralelo. Lo que se hizo con
> cada hallazgo está al final, en «Seguimiento».

## 1. Alcance

Revisé estos archivos:
- `src/proyecto/models/tuning.py`
- `notebooks/06_optimizacion.ipynb` (código definitivo)
- La ejecución idéntica con salidas (copia local del notebook ejecutado, fuera del repositorio)
- `src/proyecto/models/train.py`
- `src/proyecto/data/split.py`
- `src/proyecto/features/engineering.py`
- `especificaciones/06-optimizacion.md`
- `tests/test_tuning.py`
- `.gitignore`

No pude comprobar estas cosas:
- `reports/01_eda.md` y `reports/05_torneo.md`. La lista de columnas prohibidas la tomé de `FORBIDDEN_COLUMNS` en `engineering.py`, sin cotejarla con el EDA.
- `reports/06_optimizacion.md`. Aún no existe o no lo abrí. Cuando se escriba, sus cifras deben salir de la ejecución.
- El contenido real de `data/processed/train.joblib`. No ejecuté nada.
- Una ejecución propia de `pytest`. Solo leí las pruebas.
- Que la ejecución con salidas sea de verdad idéntica a la definitiva. Lo tomo de lo que dice el pedido. La única diferencia que vi es que el notebook definitivo imprime `experiment_label` y la copia ejecutada imprime la ruta completa del experimento.

## 2. Veredicto

**Sin fuga evidente.** No encontré ningún problema que invalide la etapa. Hay 5 observaciones menores, ninguna con fuga directa. Las dos primeras (H1 y H2) conviene corregirlas antes de redactar `reports/06_optimizacion.md`.

## 3. Respuesta a cada pregunta del pedido

| Pregunta | Resultado | Evidencia |
|---|---|---|
| ¿Alguna ruta lee `test.joblib`? | **No** | `Grep` de `test.joblib` en `src/` no da ninguna lectura. En el notebook solo aparece en dos textos explicativos. El único `joblib.load` de `src/` es `src/proyecto/inference/predict.py:33` (carga el modelo, no la prueba). El notebook carga solo `train.joblib`. |
| ¿Pliegues por sede, y los mismos en la búsqueda y en la partida? | **Sí** | `group_cv(3)` es `GroupKFold` (`split.py:37-39`). Es determinista y es un único objeto `cv`, que se pasa a `tune`. Dentro de `tune`, tanto `objective` como `measure_start` llaman a `evaluate_folds(..., X, y, cv)`. Esa función exige la columna de sede (`train.py:106-109`) y parte con `groups=X[GROUP_COL]` (`train.py:118`). El notebook además comprueba que los pliegues no comparten sedes. La salida muestra 3 pliegues de 29.203 / 29.203 / 29.204 estudiantes para ajustar. |
| ¿Las sedes reservadas quedan fuera de la búsqueda? | **Sí** | `reserve_groups` usa `split_by_group`, que usa `GroupShuffleSplit` y llama a `assert_disjoint_groups` (`split.py:18-22`). Solo `X_search` e `y_search` entran a `tune`; `X_res` e `y_res` aparecen únicamente en la sección 6. La salida muestra 866 sedes de búsqueda, 289 de reserva y 0 compartidas. La prueba `test_reserve_groups_disjoint` cubre esto. |
| ¿`min_frequency` y el resto del preprocesamiento se ajustan dentro de cada pliegue? | **Sí** | `build_tuned_pipeline` pasa `min_frequency` a `build_pipeline`, y este lo pasa al `OneHotEncoder` dentro del `ColumnTransformer` (`engineering.py:157`). La mediana del imputador y el codificador viven en el `Pipeline`. `evaluate_folds` hace `clone` y `fit` con el pliegue de ajuste, y predice sobre el de validación (`train.py:119-123`). `min_frequency` entra a la búsqueda como un hiperparámetro más, no como un valor calculado con todos los datos. `scale=False`, así que no hay `StandardScaler`. |
| ¿El bootstrap agrupa por sede? | **Sí** | `bootstrap_mae_difference` suma el error por sede y sortea sedes con reemplazo. `bootstrap_metric_ci` sortea índices de sede y concatena todas sus filas. Las pruebas `test_bootstrap_resamples_whole_sedes` y `test_bootstrap_keeps_school_rows_together` lo verifican. |
| ¿Hay columnas con fuga o identificadores como predictores? | **No** | El `ColumnTransformer` solo toma `NUMERIC_BASE`, `CATEGORICAL_BASE` y los dos códigos de municipio, con `remainder="drop"` (`engineering.py:159-165`). `feature_frame` deja la sede en `X` solo para agrupar (`train.py:137-139`), pero el preprocesador la descarta. Los puntajes por área, `desemp_ingles` y los identificadores están en `FORBIDDEN_COLUMNS` (`engineering.py:48-67`) y no son predictores. Los códigos de municipio son geográficos, no identifican al estudiante, y se conocen antes del examen. |
| ¿Se usa la reserva de modo que vuelva optimista la cifra reportada? | **Levemente** | Ver H1. |
| ¿Métricas casi perfectas? | **No** | MAE en la reserva de 33,7 a 34,1 puntos y R² de 0,35 a 0,36. El MAE en la reserva (33,68 y 33,72) es algo mayor que el de validación cruzada (33,40 y 33,44). Eso es lo esperable en una sede nueva y no es señal de fuga. |

## 4. Hallazgos

| # | Gravedad | Hallazgo | Archivo:línea | Por qué importa | Cómo corregirlo |
|---|---|---|---|---|---|
| H1 | Baja | La reserva se usa para decidir (regla 1: optimizado o partida, y regla 2: HGB o XGBoost). Después se reportan, con esas mismas sedes, el MAE y los intervalos de las configuraciones ya elegidas. La reserva deja de ser una medición completamente limpia. El sesgo es pequeño: son solo 3 decisiones binarias con reglas escritas antes. La spec lo permite expresamente. | notebook, sección 6; `especificaciones/06-optimizacion.md` §6 | Los 33,68 / 33,72 pueden quedar un poco bajos como estimación del error futuro. | En el informe, decir que la reserva se usó para elegir y que la cifra limpia llega en la etapa 7 con `test.joblib`. No presentar el MAE de la reserva como la cifra final del modelo. |
| H2 | Baja | La tabla «antes y después de la búsqueda» compara la partida con el **mejor de 25–30 ensayos**. Eso favorece al ganador, porque es una selección sobre los mismos pliegues. La columna «mejora / ruido» (2,5 en HGB y 4,9 en XGBoost) usa la desviación de solo 3 pliegues, un denominador poco fiable. En la reserva la mejora fue menor: −0,37 y −0,35, frente a −0,39 y −0,54 en validación cruzada. | notebook, sección 4 («mejora / ruido») | Es sesgo de selección dentro de la búsqueda, no fuga de datos. Si el informe cita 0,39 / 0,54 como la mejora real, la exagera. | En `reports/06_optimizacion.md` citar como mejora real la de la reserva con su intervalo, y la de validación cruzada solo como orientativa. El notebook ya avisa que es optimista. |
| H3 | Baja | Con `load_if_exists=True`, el estudio guardado en `optuna_06.db` se reanuda sin comprobar que los datos, los pliegues o el espacio de búsqueda sean los mismos que cuando se creó. El nombre del estudio (`saber11-<modelo>-mae`) no los incluye. Si se repite el notebook con otros datos o semilla de reserva y el `.db` queda del intento anterior, se mezclarían ensayos de otra partición. En la ejecución revisada se creó un estudio nuevo, y la salida del notebook no muestra ese problema. | `tuning.py:159-165` | Si la reserva incluyera sedes vistas por ensayos antiguos, la reserva dejaría de ser independiente. | Borrar `optuna_06.db` antes de cualquier rerun con cambios, o añadir al nombre del estudio una huella de las sedes de búsqueda. Opcional: en `tune`, guardar y comparar esa huella en `user_attrs`. |
| H4 | Muy baja (higiene) | `optuna_06.db-journal` aparece sin seguimiento en `git status`. El patrón `optuna_*.db` de `.gitignore` no lo cubre porque termina en `-journal`. Los archivos `reports/06_*_local*` también aparecen sin seguimiento. Los archivos `*_local` parecen salidas de la ejecución local y conviene no subirlos si duplican a los definitivos. | `.gitignore:27` | Podría subirse por descuido al repositorio. No es una fuga de entrenamiento. | Cambiar el patrón a `optuna_*.db*`, o añadir `*.db-journal`. Decidir si los `*_local` se descartan. |
| H5 | Baja | Las pruebas no cubren estas reglas: que `tune` use el `cv` agrupado que se le pasa; que `min_frequency` se ajuste dentro del pliegue; ni que las sedes reservadas no entren a la búsqueda más allá de `reserve_groups`. `test_tune_requires_group_column` cubre solo que falte la columna. Tampoco hay una prueba que falle si el notebook partiera por fila. | `tests/test_tuning.py` | El control más importante (la partición por sede) depende de revisarlo a mano. | Añadir una prueba que pase a `tune` un `cv` que registre los grupos de cada pliegue y verifique que ninguna sede esté en ajuste y validación a la vez. Añadir otra que mida que el `min_frequency` se calcula solo con el pliegue de ajuste. |

## 5. Recomendaciones

1. Antes de cerrar la etapa, escribir `reports/06_optimizacion.md` con las cifras exactas de la ejecución (no las de esta auditoría) y con el motivo de cada decisión de datos (regla 6 de `CLAUDE.md`). Incluir H1 y H2 como nota de lectura.
2. Dejar claro en el informe que las cifras de 3 pliegues sobre el 75 % de las sedes **no se comparan** con el 33,56 del torneo (5 pliegues sobre todo el entrenamiento). La spec ya lo dice en §6.
3. Cuando se reentrene el modelo final para la etapa 7, las sedes reservadas pueden volver al entrenamiento, pero `test.joblib` debe abrirse una sola vez, en esa etapa.
4. Aplicar H3 y H4 (cambios de una línea cada uno) y considerar H5 (una prueba nueva por regla).
5. Después de editar `.gitignore` o `tests/`, volver a ejecutar `pytest` y repetir esta auditoría solo si cambia `tuning.py`.

**Veredicto final:** sin fuga evidente. Hay 5 observaciones menores (H1 a H5) que no invalidan la etapa.

## Seguimiento (5 nov 2026)

- **H1 y H2:** atendidos en `reports/06_optimizacion.md`: la mejora que se cita es la de las sedes reservadas con su
  intervalo; la de validación cruzada se presenta como orientativa y optimista; se aclara que la reserva se usó para decidir
  y que la cifra limpia llega en la etapa 7.
- **H3:** la ejecución definitiva (Databricks) partió de un estudio nuevo (el anterior se renombró a `optuna_06_local.db`).
  Queda como precaución escrita en el informe: borrar o renombrar `optuna_06.db` antes de repetir con otros datos o semilla.
- **H4:** `.gitignore` cambiado a `optuna_*.db*`. Los `reports/06_*_local.*` se conservan a propósito (resultado de la
  ejecución local, pedido por el grupo para comparar con Databricks).
- **H5:** atendido (pedido del grupo, 5 nov 2026). Dos pruebas nuevas en `tests/test_tuning.py`:
  `test_tune_uses_folds_grouped_by_school` (un validador espía anota las sedes de cada pliegue: ninguna a los dos lados y
  la partida usa los mismos pliegues que los ensayos) y `test_min_frequency_fitted_inside_each_fold` (un espía del one-hot
  verifica que se ajusta una vez por pliegue, solo con sus filas de ajuste, con el umbral del ensayo, y que no conoce
  categorías que solo están en validación). Se comprobó con una versión con fuga simulada (ajuste con toda la tabla) que la
  segunda prueba falla. `pytest`: 76 de 76.

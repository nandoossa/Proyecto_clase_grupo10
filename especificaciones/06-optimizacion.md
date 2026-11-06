# Especificación · Etapa 6 · Optimización de hiperparámetros con seguimiento (tracking)

> Se llena **antes** de pedirle código a Claude, a partir de `reports/04_features.md` y `reports/05_torneo.md`.
> Claude la lee y la implementa; ustedes revisan que el código haga **exactamente** esto
> (`material-del-curso/kit/checklist-revision-ia.md`).
> Ejemplo de estructura (no de decisiones): `material-del-curso/ejemplo-creditsight/src/creditsight/models/tuning.py` y
> `material-del-curso/ejemplo-creditsight/notebooks/06_optimizacion.ipynb`. Guía: `material-del-curso/kit/guia-modelado-y-optimizacion.md`, secciones 3 y 4.

**Grupo:** Predictor de resultados Pruebas Saber 11 en Antioquia   **Fecha:** 5 nov 2026   **Estado:** ☐ borrador  ☒ cerrada (falta la revisión del grupo con el checklist)

> Borrador preparado por Claude a partir del pedido del grupo del 5 nov 2026. Los tiempos de la sección 4 se midieron en
> este equipo (5 nov 2026) con un ajuste de cada modelo sobre ~29.000 estudiantes. Ninguna cifra de resultados está escrita
> todavía: se llenan después de ejecutar el notebook 06.

## 1. Entrada y dependencia

- **Entrada:** `data/processed/train.joblib` (57.286 estudiantes, 1.155 sedes; lo deja el notebook 03).
  **`data/processed/test.joblib` no se abre en esta etapa** (constitución, principio III): se abre una vez, en la etapa 7.
- **Finalistas** (`reports/05_torneo.md`): `HistGradientBoostingRegressor` (MAE 33,56 ± 0,24) y XGBoost (33,66 ± 0,21),
  empatados dentro del ruido. **LightGBM no se usa** (no carga en los equipos del grupo; decisión del 31 oct 2026).
- **Variables** (`reports/04_features.md`): variables base, `use_engineered=False`, sin escalado (árboles).
- **Pipeline y métricas:** `build_pipeline`, `evaluate_folds` y `regression_metrics` de `src/proyecto/models/train.py`;
  validación agrupada por sede con `group_cv` de `src/proyecto/data/split.py`.

## 2. Métrica y dirección

| | Regla |
|---|---|
| Métrica que se optimiza | **MAE** en puntos (media entre pliegues), dirección **minimize**. Es la métrica del caso (los dos errores cuestan lo mismo) |
| Métricas que se registran también | RMSE y R², cada una con su desviación entre pliegues; MAE con su desviación; segundos de ajuste |
| Lo que **no** aplica (es regresión) | Matriz de costos, probabilidades, AUC, F1, log loss, regla de decisión por umbral |

## 3. Reserva de sedes (comprobación honesta)

- Dentro de `train.joblib` se reserva el **25 % de las sedes** con `split_by_group(train, test_size=0.25, seed=7)`
  (semilla 7, distinta de la 42 de la partición de prueba, como en el ejemplo). La búsqueda **solo** ve el 75 % restante.
- Una comprobación automática verifica que **ninguna sede** está a la vez en la búsqueda y en la reserva.
- Pliegues de la búsqueda: `group_cv(3)` (3 pliegues `GroupKFold` por sede sobre la parte de búsqueda), los mismos para todos
  los ensayos de un modelo. Se usan 3 y no 5 para que el presupuesto quepa en el tiempo (sección 4).

## 4. Espacios de búsqueda y presupuesto

Los rangos rodean los parámetros de partida del torneo (que ya dan 33,56) y no se alejan a zonas que se sabe que
sobreajustan o subajustan. Las dos decisiones pendientes de etapas anteriores entran como parámetros en **ambos** modelos:

| Parámetro | Modelo | Rango | Motivo |
|---|---|---|---|
| `min_frequency` | ambos | {0,01; 0,001} | Pendiente de la etapa 4: 0,1 % mejoró 0,17 puntos (0,77 veces el ruido), sin pasar la regla. Se prueba junto con los demás parámetros |
| Pérdida | HGB: `loss` ∈ {`squared_error`, `absolute_error`}; XGB: `objective` ∈ {`reg:squarederror`, `reg:absoluteerror`} | Pendiente de la etapa 5: el MAE se minimiza con error absoluto; el cuadrático persigue la media y es más sensible a puntajes extremos |
| `learning_rate` | ambos | 0,02–0,2 (logarítmica) | Alrededor del 0,05 de partida; por debajo de 0,02 harían falta miles de árboles |
| `max_iter` / `n_estimators` | ambos | 150–600 | Con tasas bajas hacen falta más árboles; 600 mantiene cada ensayo por debajo de ~1 minuto |
| `max_leaf_nodes` | HGB | 15–63 | Alrededor de 31 (el de partida y el de LightGBM) |
| `max_depth` | XGB | 3–10 | Alrededor de 6 (el de partida); más de 10 memoriza combinaciones raras |
| `min_samples_leaf` / `min_child_weight` | HGB / XGB | 20–200 / 1–100 (logarítmica) | Hojas con pocos estudiantes aprenden ruido; con sedes no vistas conviene hojas más grandes |
| `l2_regularization` / `reg_lambda` | HGB / XGB | 0,001–10 (logarítmica) | Encoge las hojas; escala logarítmica porque su efecto es multiplicativo |
| `max_features` | HGB | 0,5–1,0 | Fracción de variables por división; añade diversidad como `colsample_bytree` |
| `subsample`, `colsample_bytree` | XGB | 0,6–1,0 y 0,5–1,0 | Muestreo de filas y columnas por árbol; reduce el sobreajuste |

Fijos: `early_stopping=False` (HGB), `tree_method="hist"` y `n_jobs=2` (XGB), semilla 42 en ambos.

- **Presupuesto (fijado antes de empezar):** **25 ensayos de HistGradientBoosting y 30 de XGBoost**, con Optuna (TPE,
  semilla 42). Antes de la búsqueda, los **parámetros de partida del torneo** (con `min_frequency` 0,01 y pérdida
  cuadrática) se miden **con los mismos pliegues** y se registran como `<modelo>-partida`: así el «antes» es comparable con
  el «después». (No se meten como ensayo de Optuna porque `l2_regularization=0` de HGB no cabe en una escala logarítmica.)
- **Motivo del número:** un ajuste tarda ~4–10 s (HGB) y ~2–3 s (XGB) en este equipo; con 3 pliegues y hasta 600 árboles
  la búsqueda completa se estima en ~15–20 minutos, bajo el límite de 30 minutos del grupo.
- **Reanudación:** el estudio de Optuna se guarda en un archivo sqlite (`optuna_06.db`, en la raíz, ignorado por Git); si la
  ejecución se corta, al volver a correr se hacen solo los ensayos que faltan.

## 5. Seguimiento (MLflow)

- `configure_mlflow()` (Databricks si conecta; si no, respaldo local `mlflow_local.db`, y el notebook lo avisa) y
  `set_experiment("saber11-optimizacion")`.
- Una ejecución madre por modelo (`optuna-<modelo>`) y **cada ensayo como ejecución anidada** (`<modelo>-ensayo-NN`) con:
  parámetros del ensayo, MAE, RMSE y R² con su desviación entre pliegues, segundos de ajuste y etiquetas
  `etapa=06_optimizacion`, `modelo=<modelo>`, `metrica_optimizada=mae`.

## 6. Comprobación honesta y reglas de decisión (escritas antes de mirar)

Para cada finalista se entrenan **dos** modelos con toda la parte de búsqueda (parámetros de partida y optimizados) y se
evalúan en las **sedes reservadas**. La diferencia de MAE (optimizado − partida) lleva un intervalo del 95 % con 1.000
remuestreos de **sedes completas** (no de filas).

- **Regla 1 (optimizado o de partida):** se usan los parámetros optimizados de un modelo **solo si todo el intervalo está
  por debajo de cero**. Si cruza el cero, la mejora no se distingue del ruido y se usan los de partida.
- **Regla 2 (cuál de los dos finalistas):** se comparan las dos configuraciones elegidas por la regla 1 en las sedes
  reservadas (diferencia de MAE con intervalo del 95 % por sedes). Si el intervalo **no incluye el cero** (diferencia
  clara), gana el de menor MAE. Si **incluye el cero** (no se distingue del ruido), **se elige HistGradientBoosting**,
  porque viene en scikit-learn y no requiere librerías adicionales, lo que simplifica el registro y el despliegue de la app.
  *Aprobada por el grupo el 5 nov 2026, antes de ejecutar la búsqueda.*
- Se reporta también el MAE de cada modelo en la reserva con su intervalo del 95 % por sedes, y RMSE y R².
- **Medición de partida (aprobada por el grupo el 5 nov 2026):** cada modelo con sus parámetros del torneo, evaluado con
  los **mismos 3 pliegues y los mismos datos de la búsqueda**, para que la mejora sea comparable.
- La referencia del pedido (MAE 33,56) es de 5 pliegues sobre todo el entrenamiento; las cifras de esta etapa son de 3
  pliegues sobre el 75 % de las sedes y de la reserva, así que **no se comparan directamente** con el 33,56 (el informe lo
  aclara).

## 7. Entradas y salidas

| | Ruta |
|---|---|
| Entrada | `data/processed/train.joblib` |
| Código | `src/proyecto/models/tuning.py`: espacios, fábricas de modelos, `reserve_groups`, `tune`, bootstrap por sede |
| Pruebas | `tests/test_tuning.py` |
| Notebook que orquesta | `notebooks/06_optimizacion.ipynb` |
| Salidas | `reports/06_optimizacion.md`, `reports/06_best_params.json`, `reports/06_comprobacion.csv`; ejecuciones en MLflow |

## 8. Pruebas que deben existir

- ☒ **Espacios válidos:** cada espacio devuelve parámetros dentro de sus rangos (incluidos `min_frequency` y la pérdida) y
  la fábrica construye un modelo que se ajusta y predice sin vacíos.
- ☒ **El bootstrap agrupa por sede:** con una sola sede el intervalo se reduce al valor puntual (remuestrear filas daría
  un intervalo con ancho); el valor puntual es exactamente MAE(A) − MAE(B).
- ☒ **La reserva no comparte sedes con la búsqueda** y reserva ~25 % de las sedes.
- ☒ **`tune` mide los parámetros de partida con los mismos pliegues y se reanuda** desde el archivo sqlite sin repetir ensayos.
- ☒ **Pruebas de la auditoría (H5):** la búsqueda y la medición de partida usan pliegues por sede (ninguna sede en ajuste y
  validación de un mismo pliegue, los mismos pliegues para todos) y el one-hot con `min_frequency` se ajusta solo con las
  filas de ajuste de cada pliegue.
- ☒ `pytest` en verde (76 de 76, 5 nov 2026).

## 9. Criterios de cierre

- ☒ Cada ensayo registrado en MLflow (Databricks: 25 + 30 ensayos y 2 mediciones de partida). ☒ Tiempo de la búsqueda
  **aceptado por el grupo (5 nov 2026)**: con Databricks tardó 31,1 min de búsqueda (32,2 min el notebook completo). El
  cálculo es idéntico al de la ejecución con MLflow local (27,2 min, mismos 55 ensayos bit a bit); la diferencia se debe al
  registro por red en Databricks.
- ☒ `reports/06_optimizacion.md` con el mejor modelo, parámetros, MAE antes y después, comprobación en sedes reservadas con
  intervalo y decisiones, **solo con cifras de la ejecución**.
- ☒ Decisión anotada en la sección 7 de `especificacion-proyecto.md`.
- ☒ Auditoría con `auditor-de-fuga` en `reports/auditoria_etapa6.md`.
- ☒ Todo subido a GitHub.
- ☐ Revisión del código de Claude por el grupo con `material-del-curso/kit/checklist-revision-ia.md`.

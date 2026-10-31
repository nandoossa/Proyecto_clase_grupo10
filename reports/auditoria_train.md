# Auditoría de fuga: train.py y notebook 05 (etapa 5)

> Informe del subagente `auditor-de-fuga` (31 oct 2026), con sus instrucciones de `.claude/agents/auditor-de-fuga.md`,
> solo lectura. Se guarda tal cual; la nota final la agregó Claude y no es parte del informe del auditor.

**Archivos revisados:** `src/proyecto/models/train.py`, `notebooks/05_torneo.ipynb` (código y salidas), `src/proyecto/features/engineering.py`, `src/proyecto/data/split.py`, `tests/test_split.py`, `tests/test_models.py`, `especificaciones/03-preprocesamiento.md`, `reports/01_eda.md`. Las celdas del notebook se citan por su id (por ejemplo `664a5f30`) y por su tema, porque el archivo no me muestra su número de orden.

| Hallazgo | Archivo:línea | Por qué importa | Cómo corregirlo | Estado |
|---|---|---|---|---|
| Partición por grupo en la validación | `train.py:112-125` (`evaluate_folds`, `cv.split(X, y, groups=X[GROUP_COL])`); `split.py:37-39` (`group_cv` devuelve `GroupKFold`); notebook celda `664a5f30` (`cv = group_cv(n_splits=5)`) | Una sede completa cae en un solo pliegue. Partir por fila habría dejado estudiantes de la misma sede a ambos lados, y el MAE saldría optimista (la sede explica el 36 % del puntaje). | Nada. | Sin problema |
| Se comprueba que no se mezclen sedes | `train.py:106-109` (`_require_group_col` lanza error si falta la sede); celda `664a5f30` (`assert set(X.iloc[i_ent][ID_COL]).isdisjoint(...)` en cada pliegue) | Hay una defensa en el código y otra en el notebook que se ejecutó sin fallar. | Nada. | Sin problema |
| No hay `train_test_split`, `KFold` ni `.sample(` en `src/` | Búsqueda en `src/` | Solo aparecen `GroupKFold` y `GroupShuffleSplit` (`split.py:8,18,39`). | Nada. | Sin problema |
| Preprocesamiento dentro del `Pipeline` | `train.py:65-77` (`build_pipeline`); `engineering.py:151-165` (`SimpleImputer`, `StandardScaler`, `OneHotEncoder`); `train.py:119` (`clone(pipeline)` y `fit` solo con `train_idx`) | La mediana, la escala y las categorías se aprenden en cada pliegue solo con sus datos de entrenamiento. | Nada. | Sin problema |
| `add_features` solo usa datos de la misma fila | `engineering.py:92-107` | No calcula promedios ni medianas globales. Además, el torneo corre con `use_engineered=False` (celda `524006f6`), así que ni se usa. | Nada. | Sin problema |
| La prueba no se abre | Todo `src/` y todo el notebook | No hay ninguna lectura de `test.joblib`. El notebook solo carga `train.joblib` (celda `e4b5b4e6`) y lo dice en voz alta («la prueba NO se abre hoy»). La búsqueda de `test.joblib` en `src/` no da resultados. | Nada. | Sin problema |
| Columnas posteriores a la decisión | `engineering.py:16-45` y `48-67` | Ninguna de las 7 sospechosas del EDA entra como variable: los 5 puntajes por área, `desemp_ingles` y `estu_estadoinvestigacion`. Están en `FORBIDDEN_COLUMNS`, y `feature_columns` (línea 118-120) lanza error si alguien intenta añadirlas. `punt_global` también está prohibida como predictor, y `feature_frame` (`train.py:139`) la separa como objetivo. Las variables que sí entran (hogar, estrato, edad, atributos del colegio, municipio) las conoce el estudiante antes del examen. | Nada. | Sin problema |
| La sede no entra como predictor | `engineering.py:59` y `161` (`remainder="drop"`); `tests/test_models.py:84-89` (`test_pipeline_ignores_school_id_and_target`) | La sede viaja en `X` solo para agrupar. La prueba demuestra que cambiar la sede no cambia la predicción. | Nada. | Sin problema |
| Prueba automática de la partición | `tests/test_split.py:21-31` y `49-52`; `tests/test_models.py:133-140` | Fallarían si `split_by_group`, `group_cv` o `evaluate_folds` partieran por fila, porque comprueban que las sedes de entrenamiento y validación no se crucen. Aviso menor: `test_split.py:40-46` (`test_row_split_would_share_schools`) usa `train_test_split` solo para demostrar el problema; no vigila nada. No es fuga. | Opcional: añadir una prueba que verifique que `group_cv()` devuelve un objeto con grupos (`GroupKFold`). Hoy la cubre indirectamente el test de pliegues. | Sin problema (con matiz) |
| Métricas casi perfectas | Salidas de las celdas `524006f6` y `54b8f69a` | El mejor modelo (HistGradientBoosting) tiene MAE 33,56 y R² 0,349. La línea base tiene MAE 42,83 y R² -0,011. Las diferencias entre modelos son pequeñas y coherentes. No hay nada cercano a lo perfecto, y R² de 0,30 a 0,35 es creíble para este problema. | Nada. | Sin problema |
| Un estadístico descriptivo usa todo `train` | Celda `54b8f69a`: `y.mean()` para el «error relativo» | Es solo un dato para describir el resultado. No decide nada ni entra al modelo. No altera las métricas y no es fuga. | Nada. | Sin problema |

**Qué no pude comprobar:**

- No leí `.specify/memory/constitution.md` (principios II y III). Las reglas que apliqué salen de `especificacion-proyecto.md` y de los archivos de la etapa 3 y del EDA.
- No audité el notebook 03, donde se crea `train.joblib`. Por eso no puedo confirmar con el código a la vista que `train.joblib` se haya partido con `split_by_group` y que los duplicados exactos se hayan quitado antes de partir. La especificación lo declara, y el notebook 05 confirma que no hay sedes repartidas dentro de `train`, pero no que `test` esté separado por sede.
- No ejecuté las pruebas. Tampoco hice la comprobación manual de la especificación (cambiar a partición por fila y ver que `pytest` falla).

**Veredicto:** sin fuga evidente en `train.py` ni en el notebook 05: 0 problemas que corregir. Queda pendiente confirmar la partición inicial en el notebook 03.

---

**Nota de Claude (no es parte del informe del auditor):** en este equipo se ejecutó el notebook 03 completo el 31 oct 2026
para generar `train.joblib` y `test.joblib`. Su salida da 144.766 → 72.148 filas tras quitar duplicados y el calendario
«OTRO», 57.286 de entrenamiento (1.155 sedes), 14.862 de prueba (289 sedes) y **0 sedes en los dos lados**. Esa celda
tiene un `assert` de sedes disjuntas que habría fallado si no fuera así. `pytest` da 62 pruebas en verde. Esto responde en
parte al pendiente del auditor; una auditoría formal del notebook 03 ya existe en `reports/auditoria_etapa3.md`.

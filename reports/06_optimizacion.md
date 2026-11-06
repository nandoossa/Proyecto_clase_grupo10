# Informe de la optimización

> Resultado de `notebooks/06_optimizacion.ipynb` (ejecutado el 5 nov 2026 con seguimiento en Databricks; todas las cifras
> salen de su salida, de `reports/06_best_params.json` y de `reports/06_comprobacion.csv`). La mejor puntuación de una
> búsqueda es **optimista**: se comprueba en sedes que la búsqueda no vio. Guía:
> `material-del-curso/kit/guia-modelado-y-optimizacion.md`, secciones 3 y 4. Reglas: `especificaciones/06-optimizacion.md`.

## Diseño de la búsqueda

- **Finalistas optimizados** (`reports/05_torneo.md`): `HistGradientBoostingRegressor` y XGBoost. LightGBM no se usa (no
  carga en los equipos del grupo). Variables base, sin variables nuevas, sin escalado.
- **Métrica:** MAE en puntos (media de 3 pliegues `GroupKFold` por sede), dirección *minimize*. Se registran también RMSE y
  R², cada una con su desviación entre pliegues.
- **Espacio de búsqueda** (rangos alrededor de los parámetros de partida del torneo; motivo completo en
  `especificaciones/06-optimizacion.md` §4):

| Parámetro | Rango | Motivo |
|---|---|---|
| `min_frequency` (ambos) | {0,01; 0,001} | Pendiente de la etapa 4: 0,1 % mejoró 0,17 puntos (0,77 veces el ruido) sin pasar la regla |
| Pérdida: `loss` (HGB) / `objective` (XGB) | cuadrática o absoluta | Pendiente de la etapa 5: el error absoluto está alineado con el MAE; el cuadrático persigue la media |
| `learning_rate` (ambos) | 0,02–0,2 (logarítmica) | Alrededor del 0,05 de partida; por debajo de 0,02 harían falta miles de árboles |
| `max_iter` / `n_estimators` | 150–600 | Más árboles con tasas bajas; 600 mantiene el tiempo acotado |
| `max_leaf_nodes` (HGB) | 15–63 | Alrededor de 31, el de partida |
| `max_depth` (XGB) | 3–10 | Alrededor de 6, el de partida; más profundo memoriza combinaciones raras |
| `min_samples_leaf` (HGB) / `min_child_weight` (XGB) | 20–200 / 1–100 (log.) | Hojas grandes generalizan mejor a sedes no vistas |
| `l2_regularization` (HGB) / `reg_lambda` (XGB) | 0,001–10 (log.) | Encoge las hojas; efecto multiplicativo |
| `max_features` (HGB) | 0,5–1,0 | Fracción de variables por división |
| `subsample`, `colsample_bytree` (XGB) | 0,6–1,0 y 0,5–1,0 | Muestreo de filas y columnas; reduce el sobreajuste |

- **Presupuesto** (fijado y aprobado por el grupo antes de empezar, 5 nov 2026): **25 ensayos de HistGradientBoosting y 30
  de XGBoost**, Optuna TPE con semilla 42. Motivo: con los tiempos medidos (un ajuste de ~4–10 s HGB y ~2–3 s XGB) cabía en
  ~30 minutos; XGBoost tiene más ensayos porque es más rápido y tiene un parámetro más.
- **Sedes reservadas:** 25 % de las sedes del entrenamiento con `split_by_group` (semilla 7): **289 sedes, 13.481
  estudiantes**. La búsqueda usó las otras **866 sedes, 43.805 estudiantes**. **0 sedes compartidas.** `test.joblib` no se
  abrió.
- **Medición de partida:** cada modelo con sus parámetros del torneo, evaluado con los **mismos 3 pliegues y los mismos
  datos** de la búsqueda (ejecución `<modelo>-partida`).

## Seguimiento (tracking)

- **Dónde quedó registrado:** MLflow en **Databricks** (`configure_mlflow()` devolvió `databricks (token)`), experimento
  `saber11-optimizacion` (en la carpeta del usuario del espacio de trabajo; la ruta completa no se publica porque incluye su
  correo).
- **¿Está cada ensayo como una ejecución con parámetros, métrica y etiquetas?** ☒ sí ☐ no. Ejecución madre
  `optuna-hist gradient boosting` (`04e69d72e2aa45ddae3b35a620b7e357`) con 25 ensayos anidados + 1 medición de partida;
  `optuna-xgboost` (`a5272c975ae94ea3b19019fc49253351`) con 30 + 1. Cada ensayo tiene MAE, RMSE, R², sus desviaciones,
  segundos de ajuste y etiquetas `etapa=06_optimizacion`, `modelo`, `metrica_optimizada=mae`.
- **Mejor ejecución:** `hist gradient boosting-ensayo-14`, MAE 33,401 (± 0,153).
- **Tiempo:** búsqueda de 31,1 minutos (HGB 20,0 + XGB 11,1); el notebook completo tardó 1.932 s (32,2 min). Supera por
  poco el límite de 30 minutos (**el grupo lo aceptó el 5 nov 2026**): la misma búsqueda con MLflow local tardó 27,2 minutos (notebook completo 1.724 s, 28,7 min).
  La diferencia es el registro por red en Databricks (más de un centenar de ejecuciones con varias llamadas cada una), no
  el cálculo.
- **Reproducibilidad (ejecución local frente a Databricks):** antes de configurar Databricks se hizo una ejecución completa
  con MLflow local (estudio guardado en `optuna_06_local.db`; resultados en `reports/06_best_params_local.json` y
  `reports/06_comprobacion_local.csv`). Los 55 ensayos tienen **los mismos parámetros y el mismo MAE, bit a bit**, y la
  comprobación en sedes reservadas es idéntica. Motivo: misma semilla de Optuna (42), mismos datos y pliegues
  deterministas (`GroupKFold`), modelos con `random_state=42`; el destino del registro no interviene en el cálculo. Solo
  cambian los tiempos y los identificadores de las ejecuciones.

## Resultados de la búsqueda

> Validación cruzada con 3 pliegues sobre el 75 % de las sedes. **Estas cifras no se comparan directamente con el MAE 33,56
> del torneo**, que se midió con 5 pliegues sobre todo el entrenamiento: otros datos y otros pliegues. La comparación justa
> es contra la medición de partida, hecha con los mismos pliegues.

| Modelo | MAE partida (± ruido) | Mejor MAE (± ruido) | Mejora | RMSE partida → mejor | R² partida → mejor |
|---|---|---|---|---|---|
| HistGradientBoosting | 33,787 (± 0,396) | 33,401 (± 0,153), ensayo 14 | 0,386 | 41,745 → 41,481 | 0,335 → 0,343 |
| XGBoost | 33,982 (± 0,311) | 33,440 (± 0,111), ensayo 24 | 0,542 | 41,988 → 41,339 | 0,327 → 0,348 |

Esta mejora es **orientativa y optimista** (es el mejor de 25–30 ensayos sobre los mismos pliegues, y la desviación sale de
solo 3 pliegues). La mejora que cuenta es la de las sedes reservadas (siguiente sección).

**Mejores parámetros encontrados:**

| HistGradientBoosting (ensayo 14) | Valor | XGBoost (ensayo 24) | Valor |
|---|---|---|---|
| `min_frequency` | 0,001 | `min_frequency` | 0,001 |
| `loss` | `absolute_error` | `objective` | `reg:squarederror` |
| `learning_rate` | 0,0301 | `learning_rate` | 0,0384 |
| `max_iter` | 587 | `n_estimators` | 501 |
| `max_leaf_nodes` | 16 | `max_depth` | 7 |
| `min_samples_leaf` | 82 | `min_child_weight` | 61,99 |
| `l2_regularization` | 0,3657 | `reg_lambda` | 0,189 |
| `max_features` | 0,6155 | `subsample` / `colsample_bytree` | 0,8975 / 0,5599 |

(Valores completos en `reports/06_best_params.json`.)

**Parámetros que más influyeron** (importancia de Optuna): en HGB, `learning_rate` (0,387), `min_samples_leaf` (0,291) y
`max_features` (0,239); en XGBoost, `min_child_weight` (0,413), `max_depth` (0,198) y `colsample_bytree` (0,18). Los dos
ganadores prefieren hojas grandes (82 estudiantes como mínimo en HGB; `min_child_weight` ≈ 62 en XGB), coherente con
predecir para sedes no vistas.

**Los dos pendientes** (MAE medio de los ensayos; son promedios de ensayos con otros parámetros distintos, orientan):

| Modelo | Pérdida | `min_frequency` | MAE medio | Mejor | Ensayos |
|---|---|---|---|---|---|
| HGB | absoluta | 0,001 | 33,459 | 33,401 | 16 |
| HGB | absoluta | 0,01 | 33,975 | 33,720 | 3 |
| HGB | cuadrática | 0,001 | 33,695 | 33,514 | 3 |
| HGB | cuadrática | 0,01 | 33,724 | 33,652 | 3 |
| XGB | absoluta | 0,001 | 33,769 | 33,611 | 7 |
| XGB | absoluta | 0,01 | 34,556 | 34,556 | 1 |
| XGB | cuadrática | 0,001 | 33,626 | 33,440 | 19 |
| XGB | cuadrática | 0,01 | 33,795 | 33,731 | 3 |

- **Umbral 0,1 %:** los dos mejores ensayos lo usan, y en ambos modelos es mejor que el 1 % con la misma pérdida.
- **Pérdida:** en HGB gana el error absoluto; en XGBoost, el cuadrático. La importancia de la pérdida es baja (0,002 en
  ambos): no es lo que más mueve el MAE.

## Comprobación honesta (sedes reservadas)

> Cada modelo se entrenó con toda la parte de búsqueda (partida y optimizado) y se evaluó en las 289 sedes reservadas.
> Intervalo del 95 % con 1.000 remuestreos de **sedes completas**.

| Modelo | MAE con parámetros de partida | MAE con parámetros optimizados | Diferencia (optimizado − partida) | Intervalo 95 % |
|---|---|---|---|---|
| HistGradientBoosting | 34,041 [33,18; 34,81] | 33,675 [32,86; 34,39] | −0,366 | [−0,640 ; −0,118] |
| XGBoost | 34,072 [33,20; 34,83] | 33,723 [32,87; 34,47] | −0,349 | [−0,570 ; −0,131] |

| Modelo | RMSE partida → optimizado | R² partida → optimizado |
|---|---|---|
| HistGradientBoosting | 42,056 → 41,826 | 0,351 → 0,358 |
| XGBoost | 42,121 → 41,695 | 0,349 → 0,362 |

**Regla 1, escrita antes de mirar** (`especificaciones/06-optimizacion.md` §6): se usan los parámetros optimizados solo si
todo el intervalo de la diferencia está por debajo de cero.

**Resultado de la regla 1:** en los dos modelos todo el intervalo está bajo cero → **se usan los parámetros optimizados**
en ambos. La mejora real es de unos 0,35–0,37 puntos de MAE por estudiante (menor que la que sugería la búsqueda, como se
esperaba), y mejoran también RMSE y R².

**Regla 2, escrita antes de mirar** (aprobada por el grupo el 5 nov 2026): si el intervalo de la diferencia entre los dos
finalistas incluye el cero, se elige HistGradientBoosting; si no, el de menor MAE.

**Resultado de la regla 2:** HistGradientBoosting optimizado − XGBoost optimizado = **−0,048 puntos, IC 95 %
[−0,222 ; +0,119]**. El intervalo incluye el cero: **empate**. Se elige **HistGradientBoosting**.

## Decisión

- **Modelo elegido: HistGradientBoosting con los parámetros optimizados** (ensayo 14): `min_frequency` = 0,001,
  `loss` = `absolute_error`, `learning_rate` = 0,0301, `max_iter` = 587, `max_leaf_nodes` = 16, `min_samples_leaf` = 82,
  `l2_regularization` = 0,3657, `max_features` = 0,6155, sin parada temprana, `random_state` = 42.
  **Motivo:** la regla 1 confirma que la optimización mejora a sus parámetros de partida en sedes no vistas (intervalo
  [−0,640 ; −0,118], completo bajo cero); la regla 2 encuentra un empate con XGBoost (intervalo [−0,222 ; +0,119]) y el
  desempate escrito antes elige HistGradientBoosting, que viene en scikit-learn y no requiere librerías adicionales, lo que
  simplifica el registro y el despliegue de la app.
- **Pendientes de etapas anteriores, resueltos:** el umbral de poco frecuentes pasa a **0,1 %** y la pérdida a **error
  absoluto**, como parte de la configuración optimizada (no como decisiones aisladas: se evaluaron junto con los demás
  parámetros).
- **Lo que no pudimos concluir:**
  - Que HistGradientBoosting sea mejor que XGBoost: la diferencia (0,048 puntos) está dentro del ruido.
  - El error esperado en producción: el MAE de 33,675 en las sedes reservadas **no es la cifra final del modelo**. Esas
    sedes se usaron para decidir (reglas 1 y 2), así que pueden quedar levemente optimistas (auditoría, H1). La cifra limpia
    sale de la prueba (`test.joblib`) en la etapa 7.
  - Cuánto aporta cada parámetro por separado (por ejemplo, el umbral 0,1 % solo): la búsqueda los movió juntos.
  - La condición de equidad por segmento (estrato, zona, naturaleza): se revisa en la etapa 7.

## Riesgos y notas

- **Umbral 0,1 %:** aumenta las columnas del one-hot en todas las categóricas (`reports/04_features.md`). En la etapa 8/9
  revisar que la app no reciba categorías raras que el modelo trate de forma inestable.
- **Tiempo:** la búsqueda con Databricks tardó 31,1 minutos, por encima del objetivo de 30, por el registro por red. Si se
  repite, la misma búsqueda en local tarda 27,2 minutos.
- **Reanudación (auditoría, H3):** el estudio `optuna_06.db` se reanuda sin comprobar que los datos sean los mismos. Antes de
  repetir con otros datos o semilla, renombrarlo o borrarlo (como se hizo aquí con `optuna_06_local.db`).
- **Privacidad:** el notebook no publica la ruta del experimento (incluye el correo del usuario) ni los enlaces al espacio
  de trabajo de Databricks que MLflow imprime en cada ejecución (se quitaron de las salidas).
- **Auditoría de fuga:** `reports/auditoria_etapa6.md`, sin fuga evidente; 5 observaciones menores con su seguimiento. Las
  pruebas que pedía H5 (pliegues por sede en la búsqueda y `min_frequency` ajustado dentro de cada pliegue) ya existen.

## Para la clase siguiente

- **Modelo que pasa a la validación (etapa 7):** HistGradientBoosting con los parámetros optimizados de
  `reports/06_best_params.json`, reentrenado con **todo** el entrenamiento (búsqueda + sedes reservadas: las reservadas ya
  cumplieron su papel). La prueba (`test.joblib`) se abre **una sola vez** para medir el MAE final, la condición de
  equidad por segmento y la interpretación; después, el registro del modelo (etapa 8).

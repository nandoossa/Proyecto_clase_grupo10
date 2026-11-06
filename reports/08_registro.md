# Registro del modelo

> Resultado de `notebooks/08_registro_modelo.ipynb` (ejecución oficial del 5 nov 2026; cifras de su salida y de
> `reports/08_registro.json`). Reglas y decisiones del grupo: `especificaciones/08-registro.md`.

## 1. Dónde quedó registrado

| Dato | Valor |
|---|---|
| Plataforma | ☒ Databricks (`configure_mlflow()` devolvió «databricks (token)»)  ☐ MLflow local (respaldo) |
| Experimento | `saber11-modelo-final` (en la carpeta del usuario del espacio de trabajo; la ruta completa no se publica porque incluye su correo) |
| Nombre del modelo registrado | `workspace.default.saber11_puntaje_global` (Unity Catalog) |
| Versión | **1** |
| Alias | `champion` → versión 1 |
| Quién lo registró y cuándo | El grupo, con la cuenta del espacio de trabajo configurada en `.env`, el 2026-11-05 a las 20:31:30 (ejecución `78b51940c3f74aa8a6d3877b8a4ee739`) |

Antes de la ejecución oficial se hizo un **ensayo general** con MLflow **local** en una carpeta temporal (equivalente a
`MLFLOW_FORCE_LOCAL=1`): no creó nada en Databricks y solo comprobó que el notebook corre completo.

## 2. Qué se registró junto al modelo

- **Parámetros:** el modelo (`hist gradient boosting`), sus 8 hiperparámetros con prefijo `param_` y los fijos con
  prefijo `fijo_`:
  - `min_frequency` 0,001;
  - `loss` absolute_error;
  - `learning_rate` 0,0301;
  - `max_iter` 587;
  - `max_leaf_nodes` 16;
  - `min_samples_leaf` 82;
  - `l2_regularization` 0,3657;
  - `max_features` 0,6155;
  - fijos: `early_stopping` False y `random_state` 42.
- **Métricas de la prueba,** copiadas de `reports/07_metricas_test.json`, no recalculadas:
  - `test_mae` 33,316, IC [32,394 ; 34,207];
  - `test_rmse` 41,463, IC [40,344 ; 42,496];
  - `test_r2` 0,363, IC [0,306 ; 0,414];
  - línea base: MAE 43,088, RMSE 51,971, R² −0,001;
  - diferencia de MAE frente a la línea base: −9,772, IC [−11,781 ; −7,990].
- **Firma y ejemplo de entrada:**
  - **solo las 21 columnas del modelo**: 5 numéricas (`edad`, `fami_estratovivienda`, `sin_estrato`,
    `fami_personashogar`, `fami_cuartoshogar`) y 16 categóricas (14 del colegio, del estudiante y de la familia, más los 2
    códigos de municipio);
  - sin `cole_cod_dane_sede`, sin identificadores, sin columnas prohibidas y sin `punt_global`, comprobado con `assert`
    en el notebook;
  - la firma se calculó con 200 filas y el ejemplo tiene 5, todas del **entrenamiento**;
  - las numéricas van como decimales, porque tienen vacíos.
- **Etiquetas:**
  - `etapa=08_registro` y fecha de registro;
  - `commit=3a75853`, con `cambios_sin_commit=True`, porque el código de la etapa 8 aún no estaba en un commit al
    registrar;
  - fechas de las decisiones congeladas y de la apertura de la prueba;
  - `unidad_de_particion=cole_cod_dane_sede` y `objetivo=punt_global`.
- **Ejemplo de entrada (auditoría etapa 8, H4):** son 5 filas **reales** del entrenamiento, sin identificadores ni sede.
  Es una decisión consciente: el espacio de trabajo es privado del grupo. Si el modelo se publicara fuera del grupo, se
  cambiaría por un ejemplo sintético.
- **Formato:** `cloudpickle`. Un *pickle* puede ejecutar código al cargarse: solo se carga este modelo, registrado por el
  grupo.

## 3. Comprobación de ida y vuelta

- ¿El modelo recuperado del registro predice igual que el local? ☒ sí  ☐ no
- **Cómo se comprobó:** se cargó `models:/workspace.default.saber11_puntaje_global@champion` y se comparó con el pipeline
  registrado en 500 filas del entrenamiento con **igualdad exacta** (`np.array_equal`). Resultado: **idénticas**, con
  diferencia máxima de 0.

## 4. Exportación, esquema y «el exportado es el evaluado»

- **`models/model.joblib`:** exportado **desde la versión `champion`**. No está en `.gitignore`; se sube para la app.
- **`models/input_schema.json`:** calculado **solo con el entrenamiento**. No está en `.gitignore`. Contiene:
  - las 21 columnas con su tipo y los valores válidos de cada categórica;
  - el rango observado y la mediana de cada numérica;
  - el rango **válido** aprobado por el grupo: edad 13–80, estrato 1–6, marca «Sin Estrato» 0–1, personas 1–5,
    cuartos 1–6. Fuera de ese rango, la predicción se niega;
  - **12 campos que admiten vacío** («sin respuesta»), porque tenían vacíos en el entrenamiento: `edad`,
    `fami_estratovivienda`, `fami_personashogar`, `fami_cuartoshogar`, `cole_bilingue`, `cole_caracter`,
    `fami_educacionmadre`, `fami_educacionpadre`, `fami_tieneautomovil`, `fami_tienecomputador`, `fami_tieneinternet` y
    `fami_tienelavadora`. Los otros 9 son obligatorios;
  - las categorías nuevas se **rechazan** en las 14 listas cerradas y en los 2 códigos de municipio solo se **advierte**.
- **El exportado es el evaluado** (opción A del grupo: **no se volvió a predecir sobre la prueba**):
  1. La huella SHA-256 de `final_pipeline.joblib` coincide con la del modelo que produjo las predicciones de la prueba
     (`reports/prueba_huellas.json`).
  2. `models/model.joblib` predice **exactamente** igual que `final_pipeline.joblib` en las **57.286** filas del
     entrenamiento.
  3. El MAE recalculado con las predicciones y etiquetas **ya guardadas** de la prueba es **33,316**, igual al de la etapa 7.

  Es una cadena de evidencia, no una verificación directa sobre la prueba (auditoría etapa 8, R6). Depende de
  `reports/prueba_huellas.json`, cuyas huellas se calcularon después de la apertura; las fechas de modificación (modelo
  19:53:39, apertura 19:55:52) respaldan que no cambiaron. Por eso el notebook 07 ahora se detiene si ese archivo falta.
- **Prueba de humo de la predicción,** con filas del entrenamiento:
  - una fila normal y una con «sin respuesta» en campos que lo admiten **responden**;
  - una edad de 200 **se niega** («edad: debe estar entre 13 y 80»);
  - una naturaleza «PRIVADA» **se niega** («categoría no vista en el entrenamiento; elige uno de los valores válidos»).

## 5. Inferencia y pruebas

- `src/proyecto/inference/schema.py` y `predict.py` quedaron extendidos a regresión:
  - `build_schema(..., task="regression")`;
  - una validación que rechaza columnas faltantes, valores no numéricos, valores fuera del rango válido, vacíos donde no se
    admiten y categorías nuevas en listas cerradas;
  - `predict_score`, que devuelve `puntaje_estimado` sin redondear ni recortar.
- Las funciones de clasificación de la plantilla se conservan hasta la etapa 9 y se quitarán allí.
- **Mediana de `schema.py`** (auditoría de la etapa 3, hallazgo 5): `build_schema` la calcula con la tabla que recibe, que
  en el notebook 08 es **solo el entrenamiento**. Queda en el esquema como dato informativo para la app y **nunca** se
  calcula al predecir. Lo verifican `test_schema_median_comes_only_from_given_frame` y
  `test_predict_score_does_not_learn_from_input`.
- `tests/test_inference.py`: 23 pruebas, todas en verde. Incluye `test_real_model_predicts_a_training_row`, que antes de
  exportar se saltaba y ahora pasa con `models/model.joblib` y una fila real del entrenamiento.

## 6. Tracking frente a registro (en nuestras palabras)

- **Tracking:** guardó las ejecuciones de la búsqueda de la etapa 6: 55 ensayos y 2 mediciones de partida en
  `saber11-optimizacion`. Lo usamos para comparar configuraciones y comprobar que la ejecución local y la de Databricks
  dieron lo mismo.
- **Registro:** guarda **una versión del modelo elegido**, con lo necesario para confiar en él: métricas de la prueba,
  firma y origen. El alias `champion` dice cuál es el vigente. Si mañana hay una versión mejor, se mueve el alias y quien
  use el modelo no cambia nada.

## 7. Reproducibilidad

- ¿Alguien de otro grupo podría recuperar el modelo con lo que dejamos escrito? ☒ sí, con acceso al espacio de trabajo
  (`models:/workspace.default.saber11_puntaje_global@champion`). Sin ese acceso, puede usar la copia `models/model.joblib`
  del repositorio.
- Para regenerarlo desde cero: notebooks 03 → 07 → 08. El notebook 07 no vuelve a abrir la prueba si ya existe su marca.
- **Commit de origen (auditoría etapa 8, H3):** la versión 1 se registró desde `3a75853` con los cambios de la etapa 8 aún
  sin commit (`cambios_sin_commit=True`). El código exacto queda en el commit de cierre de la etapa 8, el siguiente a
  `3a75853`.
- **Quien clone el repositorio** (auditoría etapa 8, R3) no tendrá `models/final_pipeline.joblib` ni `data/processed/`,
  que están ignorados por Git. Los notebooks 07 y 08 se detendrán con un mensaje claro. La app solo necesita
  `models/model.joblib` y `models/input_schema.json`, que sí están en el repositorio.

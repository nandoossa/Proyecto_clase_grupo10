# Auditoría de fuga de información, etapa 8 (registro del modelo, exportación y esquema de entrada)

**Fecha:** 5 nov 2026
**Proyecto:** Predictor de resultados Saber 11 en Antioquia. Regresión de `punt_global`, métrica MAE, entidad repetida `cole_cod_dane_sede`.
**Auditor:** subagente `auditor-de-fuga` (solo lectura, no se modificó ningún archivo)

> Resumen del informe del subagente. Lo que se hizo con cada hallazgo está al final, en «Seguimiento». En el hallazgo H1 se
> omite el correo que el auditor citó textualmente, para no publicarlo.

## 1. Alcance

Leídos completos:
- `notebooks/08_registro_modelo.ipynb` (código y salidas)
- `src/proyecto/inference/schema.py` y `predict.py`
- `tests/test_inference.py` (sección «Regresión (etapa 8)»)
- `models/input_schema.json` y `reports/08_registro.json`
- `notebooks/07_validacion_interpretacion.ipynb`
- `reports/prueba_huellas.json` y `reports/07_metricas_test.json`

Contexto:
- `especificaciones/08-registro.md`
- `reports/auditoria_etapa7.md` y `reports/auditoria_etapa3.md` (hallazgo 5)
- `.gitignore`
- `engineering.py`, `evaluation.py` y `mlflow_utils.py`

Se buscaron correos, `*.databricks.com`, `/Users/` y tokens en todo el repositorio (sin `.git` ni `data/`).

**No comprobado por el auditor:**
- no ejecutó `pytest` ni los notebooks;
- no abrió los `.joblib` ni recalculó huellas;
- no vio los artefactos en Databricks;
- el ensayo con MLflow local lo tomó como dato de proceso;
- no revisó `models/ficha_modelo.md` ni `reports/08_registro.md`.

## 2. Veredicto

**Sin fuga de información ni uso indebido de la prueba.** 4 hallazgos: 0 graves, 1 media (privacidad, no fuga) y 3 bajas.

## 3. Respuesta a cada pregunta

1. **¿Firma y ejemplo con solo las 21 columnas, del entrenamiento?** Sí.
   - `model_columns()` da 21 columnas, con `assert` de que no hay sede, objetivo ni columnas prohibidas.
   - `example = train[COLUMNS].head(200)`; la firma y el ejemplo de 5 filas salen de ahí.
   - Las 21 columnas de `08_registro.json` coinciden con el esquema.
2. **¿El notebook 08 vuelve a predecir sobre la prueba o la carga?** No.
   - `test.joblib` no está en la lista de archivos necesarios y ninguna celda lo carga.
   - Todos los `.predict` usan filas del entrenamiento.
   - De la prueba solo se lee `prueba_resultados.joblib`, con su huella verificada, para recalcular el MAE con lo guardado
     (opción A del grupo). No decide nada.
3. **¿El esquema se calcula solo con el entrenamiento?** Sí.
   - `build_schema(train, ...)`.
   - Categorías, `nullable`, rangos observados y medianas salen de `df`.
   - `valid_range` y `warn_only_categories` son constantes del grupo.
4. **¿`predict_score` calcula algo de los datos que recibe?** No.
   - Valida, selecciona las 21 columnas y llama a `model.predict`.
   - No hay `fit`, `mean` ni `median` en la inferencia; la única mediana está en `build_schema`.
   - `test_predict_score_does_not_learn_from_input` lo demuestra.
5. **¿Queda resuelta la mediana de `schema.py` (etapa 3, hallazgo 5)?** Sí.
   - Ahora está en `schema.py:94`.
   - Se calcula solo con la tabla que recibe (en el notebook, el entrenamiento), es informativa y no se calcula al predecir.
   - La verifica `test_schema_median_comes_only_from_given_frame`.
6. **¿Las métricas registradas coinciden con `07_metricas_test.json`?** Sí.
   - Los 15 valores son idénticos hasta el último decimal: se leen de ese JSON y no se recalculan.
   - El MAE recalculado con lo guardado también es idéntico.
7. **¿El notebook 07 cumple H1, H3, H4 y H6 sin reevaluar?** Sí, con un matiz en H3 (hallazgo H2).
   - `test.joblib` solo se carga en la rama de primera apertura, que no se ejecutó.
8. **¿Hay correos, dominios del espacio de trabajo, tokens o `/Users/`?**
   - **En el notebook 08, sí:** un aviso automático de MLflow guardó la ruta del experimento con el correo personal
     (hallazgo H1).
   - No hay tokens, dominios ni «View run».
   - En `input_schema.json` y `08_registro.json`, no.
   - En el resto del repositorio solo hay marcadores de ejemplo (`TU-WORKSPACE…`) en `.env.example` y las guías.

## 4. Hallazgos

| # | Dónde | Gravedad | Descripción | Cómo corregir |
|---|---|---|---|---|
| H1 | Notebook 08, salida de la celda de conexión | Media (privacidad) | Un aviso de MLflow («Experiment with name '/Users/‹correo›/saber11-modelo-final' does not exist…») dejó el correo personal en la salida guardada; el repositorio es público | Limpiar esa salida antes del commit y silenciar el log `mlflow.tracking.fluent` antes de `set_experiment`; comprobar con `grep` |
| H2 | Notebook 07, `if FINGERPRINTS.exists():` | Baja | Si se borra `prueba_huellas.json` con la marca y la caché presentes, se omite la verificación sin avisar. Las huellas de la apertura del 5 nov se calcularon después; las respaldan las fechas de modificación | Detenerse si la marca existe y falta `prueba_huellas.json`; decir en el informe que la cadena «exportado = evaluado» depende de ese JSON y de las fechas |
| H3 | `08_registro.json` y etiquetas del modelo (`commit` 3a75853, `cambios_sin_commit` true) | Baja | La versión 1 quedó marcada con un commit que no contiene el código de la etapa 8 | Hacer el commit de la etapa 8 y dejar constancia en `08_registro.md`; no hace falta volver a registrar |
| H4 | Celda de registro: `input_example=example.head(5)` | Baja | El ejemplo de entrada sube a Databricks 5 filas reales del entrenamiento (sin identificadores ni sede, pero con edad, estrato y municipios) | Aceptable con el espacio de trabajo privado; anotarlo como decisión consciente, o usar un ejemplo sintético |

## 5. Recomendaciones

- **R1:** resolver H1 y confirmar con `grep` y `git diff` antes del commit.
- **R2:** aplicar H2 y volver a comprobar que los resultados de la etapa 7 quedan idénticos.
- **R3:** hacer commit de `model.joblib`, `input_schema.json`, `08_registro.json` y el código. Quien clone el repositorio no
  tendrá `final_pipeline.joblib` (ignorado por Git) y los notebooks 07 y 08 se detendrán con un mensaje claro: decirlo en
  el informe.
- **R4:** `pytest` completo, confirmando que `test_real_model_predicts_a_training_row` no se salta (`pytest -rs`).
- **R5:** quitar las funciones de clasificación en la etapa 9.
- **R6:** documentar los tres eslabones de «el exportado es el evaluado» y que no es una verificación directa sobre la
  prueba.

## Seguimiento (5 nov 2026)

- **H1:**
  - la línea con el correo se quitó de la salida del notebook 08 antes de cualquier commit;
  - se agregó al código de la celda (y al generador) `logging.getLogger("mlflow.tracking.fluent").setLevel(logging.WARNING)`
    antes de `set_experiment`, para futuras ejecuciones;
  - esa línea se agregó **después** de la ejecución oficial y no cambia ningún resultado;
  - la búsqueda de correos, `/Users/`, `*.databricks.com` y tokens da 0 en todos los notebooks, `reports/` y `models/`.
- **H2:**
  - el notebook 07 ahora se detiene si existe la marca y falta `reports/prueba_huellas.json`;
  - se volvió a ejecutar reutilizando los resultados guardados, y los cinco archivos de resultados de la etapa 7 quedaron
    idénticos byte a byte;
  - la dependencia de la cadena de evidencia está escrita en `reports/08_registro.md`.
- **H3:** documentado en `reports/08_registro.md`. La versión 1 se registró desde `3a75853` con los cambios de la etapa 8
  sin commit; el código exacto queda en el commit de cierre de la etapa 8, el siguiente.
- **H4:** decisión consciente, anotada en `reports/08_registro.md` y en la ficha. El ejemplo son 5 filas del entrenamiento
  sin identificadores; el espacio de trabajo es privado del grupo. Si se publicara el modelo fuera del grupo, usar un
  ejemplo sintético.
- **R3:** escrito en `reports/08_registro.md` §7.
- **R4:** `pytest` completo en verde; `test_real_model_predicts_a_training_row` pasa (ya no se salta).
- **R5:** anotado en la especificación de la etapa 8 y en la documentación general.
- **R6:** escrito en `reports/08_registro.md` §4.

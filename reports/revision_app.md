# Revisión del código de la app y de la inferencia (preparación del despliegue)

**Fecha:** 6 nov 2026
**Revisor:** subagente `revisor-de-codigo-ia` (solo lectura; no modificó archivos), con el checklist del curso
(`material-del-curso/kit/checklist-revision-ia.md`)
**Alcance:** `app/streamlit_app.py` y `src/proyecto/inference/` (`schema.py`, `predict.py`, `form.py`)

> Informe copiado del subagente. Este informe no reemplaza que el grupo entienda el código. Lo que se hizo con cada
> hallazgo está al final, en «Seguimiento».

**VEREDICTO: aceptar con cambios.** La app funciona, no consulta Databricks, no lleva secretos y las dos suites relacionadas
pasan (`pytest tests/test_app.py tests/test_inference.py`: 34 passed). Hay cuatro puntos que conviene arreglar antes de
desplegar (H1 a H4) y varios menores.

## 1. Hallazgos por gravedad

### Importantes (arreglar antes del despliegue)

**H1. Fallo al cargar el modelo o el esquema sin mensaje amable.** `app/streamlit_app.py:95-98` comprueba que los archivos
existan, pero `get_model()` y `get_schema()` (líneas 49-56) no capturan nada. Si el `.joblib` está dañado, si hay otra versión
de scikit-learn (`InconsistentVersionWarning` o error), si falta `proyecto` en el path o si el JSON está roto, el usuario ve un
traceback de Streamlit. Es justo el fallo típico en la nube, según la guía de despliegue §8.
- Corrección propuesta: envolver la línea 98 en `try/except Exception` y mostrar `st.error("No se pudo cargar el modelo…")`
  seguido de `st.stop()`. No imprimir rutas del equipo.

**H2. El aviso de uso responsable no está «siempre visible».**
- El docstring (línea 7) dice «siempre visible», pero `RESPONSIBLE_USE` se dibuja en la línea 120, al final de la página,
  debajo del formulario de tres columnas. Hay que desplazarse para verlo.
- Si faltan los archivos del modelo, `st.stop()` (línea 97) corta antes de la línea 120, y entonces no aparece.
- Corrección propuesta: mostrarlo justo bajo el título (o en `st.warning`/`st.expander` abierto) y antes de cualquier
  `st.stop()`.
- Las cifras del texto sí coinciden con `models/ficha_modelo.md`: R² 0,363, 39,57, 35,74, 31,40, 35,55, 32,66 y 289 sedes.

**H3. Código de clasificación de la plantilla que la etapa 8 dijo que se quitaría en la etapa 9 sigue en `schema.py`.**
- `predict.py` sí quedó limpio. `predict_with_scores`, `decide_min_cost` y `_ordered_proba` ya no existen, y hay una prueba
  que lo exige (`tests/test_inference.py:63`).
- `src/proyecto/inference/schema.py` conserva todo lo de clasificación:
  - parámetros `class_names`, `cost_matrix` y `review_threshold` (líneas 36-40);
  - `task="classification"` como valor por defecto (línea 42);
  - validaciones de clases y costos (líneas 64-69);
  - rama `if task == "classification"` (líneas 82-84);
  - `cost_matrix` guardado (líneas 97-98);
  - docstring de módulo con el ejemplo de clasificación (líneas 6-12).
- Las pruebas `tests/test_inference.py:43-80` siguen ejercitando esa rama.
- Además hay un bug latente en las líneas 66-69. Con `task="regression"`, `class_names=None` y un `cost_matrix`,
  `len(class_names)` lanza `TypeError`.
- Corrección propuesta, que el grupo debe decidir:
  - (a) quitar la rama de clasificación y dejar `task="regression"` fijo, o
  - (b) dejarla y documentarla explícitamente como «se mantiene por compatibilidad con la plantilla».
  - Lo que no conviene es que las dos cosas convivan sin decirlo. El docstring de `predict.py` (líneas 8-9) afirma que
    «solo queda la regresión», y eso no es cierto para `schema.py`.

**H4. `requirements.txt` instala librerías que la app no usa.**
- Incluye `mlflow==3.17.1`, `databricks-sdk==0.153.0`, `python-dotenv`, `shap`, `optuna`, `nbconvert`, `nbformat`,
  `ipykernel`, `pytest`, `matplotlib` y `seaborn`.
- La app no importa ninguna de ellas, pero Streamlit Cloud las instalará todas. Eso alarga el despliegue y aumenta la
  superficie de fallo. También deja `mlflow` y `databricks-sdk` instalados en una app que, por la regla 8, no debería
  tocarlos.
- Las versiones locales coinciden con las fijadas (sklearn 1.9.1, pandas 3.0.6, numpy 2.5.4, joblib 1.6.0, streamlit 1.66.0).
  Eso es lo que evita el `InconsistentVersionWarning`.
- Las librerías mínimas de la app son `streamlit`, `pandas`, `numpy`, `scikit-learn` y `joblib`. Como CLAUDE.md exige un solo
  `requirements.txt` en la raíz, la decisión es del grupo: mantenerlo completo y aceptar el despliegue lento, o recortarlo. Si
  lo recortan, registrar el motivo en `reports/`.

### Menores

**H5. `sys.path.insert` en cada ejecución.** `app/streamlit_app.py:17` se ejecuta en cada rerun de Streamlit y acumula
entradas duplicadas en `sys.path`. No rompe nada. Corrección propuesta: `if str(ROOT / "src") not in sys.path:` antes de
insertar.

**H6. Dependencia oculta del pickle.** El `model.joblib` referencia `proyecto.features.engineering._as_text` (un
`FunctionTransformer`). Cargarlo sin `src/` en el path da `ModuleNotFoundError: No module named 'proyecto'`. Lo comprobé. En
la app funciona porque el path se arma en las líneas 16-17, pero:
- `src/proyecto/features/engineering.py` debe seguir en el repo y no puede renombrarse;
- vale la pena anotarlo en `models/ficha_modelo.md` y en la guía;
- un `joblib.load` de un archivo del propio repo es aceptable; no debe cargarse un `.joblib` de origen desconocido.

**H7. La prueba anti-Databricks es débil.**
- `tests/test_app.py:201-204` busca las palabras `mlflow`, `databricks` y `token` solo en `streamlit_app.py` y `form.py`. No
  revisa `predict.py` ni `schema.py`.
- Es frágil: una palabra como «token» dentro de un comentario la haría fallar.
- Corrección propuesta: revisar los cuatro archivos y buscar imports (`import mlflow`, `from databricks`) y `os.environ`, en
  vez de texto libre.
- Hoy la búsqueda (`mlflow|databricks|token|getenv|environ|dotenv`) en `app/` y `src/proyecto/inference/` no encontró nada
  fuera de los `.pyc`.

**H8. `form.py` falla con `KeyError` si el esquema no es de regresión.**
- `form.py:66, 74` y `127` leen `schema["nullable"]` sin comprobarlo. `form.py:139` hace `codes[value]` sin proteger un valor
  fuera del diccionario.
- En uso normal no ocurre, porque `options()` solo ofrece valores válidos, pero un esquema viejo daría un error críptico.
- Corrección propuesta: validar `schema.get("task") == "regression"` al inicio de `form_to_row` y `options`.

**H9. Cifras escritas a mano en tres sitios.**
- `RESPONSIBLE_USE` (`app/streamlit_app.py:36-46`), el texto «MAE 33,3» (línea 81) y `TYPICAL_ERROR = 33` (`form.py:19`) se
  copiaron de la ficha. Hoy coinciden con ella (MAE 33,32).
- Si el modelo se reentrena, hay que cambiarlas en tres sitios.
- Además, la app muestra «33 puntos» y a la vez «MAE 33,3»: una pequeña incoherencia visual.
- Corrección propuesta: dejarlas en una sola constante y anotar que se actualizan con la ficha.

**H10. Datos que se guardan en el esquema y nadie usa (código muerto).**
- `build_schema` guarda `median`, `integer_columns` y `labels` (`schema.py:76-80, 89-96`). La app no los usa: tiene sus
  propias etiquetas en `form.py: SECTIONS/LABELS` y su propio manejo de enteros en `ask()`.
- Con `task="classification"` también guarda `review_threshold` (sin uso).
- `form.py:84` tiene `field in ("estu_genero",)`, una tupla de un solo elemento; se puede escribir `field == "estu_genero"`.
- Corrección propuesta: borrarlos o documentar para qué sirven.

**H11. El esquema no valida la coherencia entre `fami_estratovivienda` y `sin_estrato`.** `validate_inputs` acepta
`sin_estrato=1` junto con un estrato numérico si alguien llama a `predict_score` directamente. La app no lo permite
(`form_to_row`, líneas 130-135), así que solo afecta a otros usos, como el notebook 09.

### Lo que sí cumple

- **Rutas:** `app/streamlit_app.py:16` usa `Path(__file__).resolve().parents[1]`, no la carpeta de trabajo. No hay
  `Path.cwd`, `os.getcwd` ni `../` en `app/` ni en `inference/` (solo en un ejemplo del docstring de `schema.py:10`).
- **Sin Databricks, MLflow ni tokens** en `app/` ni en `src/proyecto/inference/`.
- **Archivos en el repo:** `models/model.joblib` (1,17 MB), `models/input_schema.json` y `models/ficha_modelo.md` están
  versionados. `models/final_pipeline.joblib` está ignorado a propósito; `data/raw`, `.env` y los CSV también.
- **Validación en dos capas:**
  - `form_to_row` rechaza campo vacío, edad no entera o fuera de 13-80, y «Sin respuesta» en campos obligatorios, y junta
    todos los errores en un solo mensaje.
  - `predict_score` revalida contra el esquema: columnas faltantes, no numéricos, rango válido, vacíos donde el
    entrenamiento nunca los tuvo y categorías nuevas. Los municipios nuevos solo dan advertencia.
  - La app muestra el error y ningún puntaje (`app/streamlit_app.py:113-114`).
- **Pruebas con `AppTest`:** `tests/test_app.py` cubre carga, perfil normal, «Sin respuesta», edad inválida, campo faltante y
  aviso de uso responsable.
- **Estructura:** la lógica está en `src/`, los identificadores van en inglés y los textos en español.

## 2. Funciones públicas sin prueba directa en `tests/`

Entre paréntesis, qué las cubre de forma indirecta.

**`app/streamlit_app.py`**
- `get_model` y `get_schema` (vía `AppTest`; sin prueba de su fallo, H1).
- `ask` y `show_result` (solo vía `AppTest`).
- `main` (vía `AppTest`; la rama de archivos faltantes con `st.stop` no está probada).

**`src/proyecto/inference/`**
- `form.options` (solo vía `AppTest`; sin prueba con un esquema incompleto).
- `predict.validate_inputs` con esquema de regresión (se prueba directamente solo con uno de clasificación; la validación
  real se prueba vía `predict_score`).
- `predict.load_model` (sin prueba del `FileNotFoundError`).
- `schema.save_schema` (solo vía el parámetro `path` de `build_schema`).

**Regla 9 (funciones que limpian o transforman datos):**
- `form_to_row` y `reference_range` tienen prueba directa en `tests/test_app.py`; también `display_value` y `build_schema`.
- `_required` y `_age` (privadas) se prueban de forma indirecta vía `form_to_row`. **Cumple la regla.**
- `validate_inputs` no tiene una prueba directa de sus advertencias por rango observado.
- Las pruebas de `tests/test_app.py` se saltan solas si faltan los archivos del modelo: conviene confirmar que no se salten en
  silencio.

**Pruebas que sugirió añadir:**
- `options()` con y sin `nullable`;
- `load_model` con una ruta inexistente;
- `validate_inputs` con regresión y con `observed_range`;
- el fallo de carga del modelo en la app.

## 3. Explicación en palabras simples

**`app/streamlit_app.py`**
- `get_model()`: abre el archivo del modelo una sola vez y lo guarda en memoria, para no releerlo cada vez que alguien pulsa
  un botón.
- `get_schema()`: igual, pero con el «contrato de entrada»: el archivo que lista las columnas, los rangos y las categorías que
  el modelo conoce.
- `ask(field, label, schema)`: dibuja un campo del formulario. La edad es un número con la casilla «Sin respuesta»; lo demás
  es una lista desplegable que empieza sin opción elegida, para detectar que falte un dato.
- `show_result(score, warnings)`: muestra el puntaje redondeado, el rango de referencia (estimación ± 33) y una aclaración de
  que no es un intervalo de confianza; si hubo advertencias, también las enseña.
- `main()`: arma la página. Comprueba que existan los archivos, carga el modelo, dibuja el formulario y, al pulsar «Estimar»,
  traduce las respuestas, predice y muestra el resultado o el error. Termina mostrando el aviso de uso responsable.

**`src/proyecto/inference/form.py`**
- `options(field, schema)`: devuelve las opciones de un campo. Agrega «Sin respuesta» solo si en el entrenamiento ese campo
  tuvo vacíos; el estrato también ofrece «Sin estrato».
- `display_value(field, value, schema)`: convierte un código en algo legible: `S` pasa a «Sí», `F` a «Femenino», `5001` a
  «MEDELLÍN (5001)».
- `_required(...)` (privada): revisa que un campo tenga respuesta; devuelve el valor, o vacío si eligió «Sin respuesta» donde
  se permite; si no, anota un error.
- `_age(...)` (privada): valida que la edad sea un entero entre 13 y 80, o «Sin respuesta».
- `form_to_row(answers, schema)`: arma la fila con las 21 columnas que espera el modelo, convierte textos como «3 a 4» en su
  código de la etapa 3, aplica la regla del estrato (`sin_estrato`) y junta todos los errores en un solo aviso.
- `reference_range(score)`: devuelve «estimación ± 33», recortado a 100-477. Es una referencia, no un intervalo de confianza.

**`src/proyecto/inference/predict.py`**
- `InputValidationError`: el error que significa «los datos no sirven; esto es lo que hay que corregir».
- `load_model(path)`: abre el modelo guardado (un `Pipeline` completo con el preprocesamiento); avisa si el archivo no existe.
- `validate_inputs(df, schema)`: revisa la fila contra el contrato. Falla si faltan columnas, hay vacíos donde nunca los hubo,
  valores no numéricos o fuera de rango, o categorías nuevas; con municipios nuevos solo advierte.
- `predict_score(df, model, schema)`: valida, ordena las columnas y pide al modelo el puntaje; devuelve `puntaje_estimado` y
  deja las advertencias en `.attrs["warnings"]`. No redondea ni aprende nada de lo que recibe.

**`src/proyecto/inference/schema.py`**
- `build_schema(df, ...)`: arma el contrato de entrada a partir de los datos de **entrenamiento** y puede guardarlo.
- `_is_integer_column(values)` (privada): dice si todos los valores de una columna son enteros.
- `save_schema(schema, path)` y `load_schema(path)`: escriben y leen el contrato en JSON.

## 4. Tres preguntas para quien no escribió el código

1. Si alguien pone la edad 17,5 o deja el campo «Jornada» sin elegir, ¿qué ve en pantalla y qué función lo detecta? ¿Por qué
   la revisión se hace en dos sitios (`form_to_row` y `predict_score`)?
2. La app no consulta Databricks. ¿De dónde sale entonces el modelo, por qué `models/final_pipeline.joblib` no se sube y qué
   pasaría si cambia la versión de scikit-learn en `requirements.txt`?
3. ¿Por qué la app dice «se equivoca en promedio 33 puntos» y aclara que no es un intervalo de confianza? ¿En qué grupos
   (estrato 5, hombres) es peor ese error, y dónde se ve ese aviso en la pantalla?

## Seguimiento (6 nov 2026)

- **Pruebas faltantes:** el subagente `escritor-de-pruebas` agregó 8 pruebas (options, load_model, validate_inputs con regresión, guardar y leer el esquema); el proyecto pasa de 105 a 113 pruebas, todas en verde (ver `reports/despliegue_preparacion.md` §3).
- **H1 a H11:** en la revisión no se aplicaron (el pedido fue revisar). El grupo pidió después aplicar H1 a H4 y los
  menores que no cambian el comportamiento; ver la tabla siguiente.

### Qué se hizo con cada hallazgo (6 nov 2026, pedido del grupo)

| # | ¿Se aplicó? | Qué cambió / por qué no |
|---|---|---|
| H1 | ☒ sí | `main()` carga el modelo y el esquema dentro de `try/except`. Si fallan, muestra «No se pudo cargar el modelo o su esquema…» (sin rutas ni traza técnica) y se detiene. Prueba nueva: `test_app_shows_clear_message_if_model_fails_to_load` |
| H2 | ☒ sí | El aviso de uso responsable se muestra con `st.warning` justo bajo el título, **antes** de cualquier `st.stop()`, y ya no al final. Pruebas: `test_responsible_use_is_shown_before_the_form` y la de H1 (el aviso se ve aunque el modelo no cargue) |
| H3 | ☒ sí (opción a) | `schema.py` quedó solo para regresión: se quitaron `class_names`, `cost_matrix`, `review_threshold` y la rama de clasificación (con su error latente). `task` se conserva y solo acepta `"regression"`, porque el notebook 08 lo pasa. Se reemplazaron 3 pruebas de clasificación por 3 de regresión (`test_build_schema_rejects_classification`, `…_rejects_missing_column`, `…_marks_integer_columns_and_observed_range`). `models/input_schema.json` no cambia |
| H4 | ☒ sí | Nuevo `app/requirements.txt` con solo lo que usa la app y las mismas versiones de la raíz: streamlit 1.66.0, pandas 3.0.6, numpy 2.5.4, scikit-learn 1.9.1, scipy 1.18.1, joblib 1.6.0. Streamlit Community Cloud busca primero el archivo junto al archivo principal. El `requirements.txt` de la raíz se mantiene completo (CLAUDE.md). **Comprobado** en un entorno limpio con Python 3.12.10 y solo esas 6 librerías (sin mlflow): la app arrancó, el chequeo de salud respondió 200 y el perfil inventado de las pruebas dio 250, igual que en `reports/09_despliegue.md`, sin advertencias de versión |
| H5 | ☒ sí | `sys.path.insert` solo si `src/` no está ya en el path. No cambia el comportamiento |
| H6 | ☒ sí (documentación) | Anotado en `models/ficha_modelo.md`: el modelo necesita `src/proyecto/features/engineering.py` con el mismo nombre; solo se carga este pickle |
| H7 | ☒ sí | La prueba `test_app_code_does_not_use_databricks` ahora revisa los cuatro archivos (`streamlit_app.py`, `form.py`, `predict.py`, `schema.py`) buscando imports de `mlflow`, `databricks` o `dotenv` y lecturas de `os.environ` / `os.getenv`, no palabras sueltas en comentarios |
| H8 | ☐ no | Cambiaría el comportamiento (el error ante un esquema que no es de regresión pasaría de `KeyError` a otro tipo). Con el esquema actual no ocurre. **No se aplica: decisión del grupo, 7 nov 2026** (ver abajo) |
| H9 | ☒ sí (parcial) | `TEST_MAE = 33.32` en `form.py` es la única fuente del «33» y del «MAE 33,3» de la app (el texto que se ve es idéntico). Las cifras por segmento del aviso siguen escritas en la app (un solo sitio), con la nota de actualizarlas con la ficha |
| H10 | ☒ sí (parcial) | Solo el cambio de forma `field in ("estu_genero",)` → `field == "estu_genero"`. No se quitaron `median`, `integer_columns` ni `labels` del esquema: cambiaría su contenido (y `median` la verifican pruebas de la etapa 8) |
| H11 | ☐ no | Agregar el control de coherencia estrato / «Sin estrato» en `validate_inputs` cambiaría qué filas se rechazan. La app ya no permite esa combinación. **No se aplica: decisión del grupo, 7 nov 2026** (ver abajo) |

**Pruebas:** 115 de 115 en verde, ninguna saltada (`PYTHONUTF8=1 python -m pytest -q -rs`).

### Decisión del grupo sobre H8 y H11 (7 nov 2026)

**H8 y H11 no se aplican.** Motivo: la app solo carga nuestro esquema de regresión y el formulario usa un único campo para el estrato, así que esas situaciones no ocurren; aplicarlos cambiaría qué entradas se rechazan.

- **H8:** la app solo carga `models/input_schema.json`, que es de regresión, así que `form.py` nunca recibe un esquema
  de otro tipo.
- **H11:** el formulario tiene un solo campo de estrato («1» a «6», «Sin estrato» o «Sin respuesta»), que `form_to_row`
  convierte siempre en una combinación coherente de `fami_estratovivienda` y `sin_estrato`.

# Implementation Plan: Inferencia de regresión y app de Streamlit (etapa 9)

**Branch**: `007-app-inference` (trabajo en `main`) | **Date**: 2026-11-06 | **Spec**: [spec.md](spec.md)

## Summary

Dejar `predict.py` solo con la regresión; reescribir la app de la plantilla (pensada para clasificación) como un formulario
en español que traduce texto a las 21 columnas del esquema, valida, muestra el puntaje redondeado con el error típico y un
aviso de uso responsable con los límites de la ficha; notebook 09 con perfiles inventados; pruebas con AppTest; informes.

## Technical Context

**Language/Version**: Python 3.12 · **Primary Dependencies**: streamlit 1.66.0, scikit-learn 1.9.1, pandas 3.0.6
(fijadas en `requirements.txt`) · **Testing**: pytest 9.1.1 + `streamlit.testing.v1.AppTest` (comprobado: importa en el
`.venv`) · **Constraints**: la app no consulta Databricks; nada de la prueba.

## Constitution Check

| Principio | ¿Cumple? | Cómo |
|---|---|---|
| III. La prueba se abre una sola vez | ✅ | Ni la app ni el notebook 09 leen `test.joblib` |
| IV. Decisiones con motivo | ✅ | En `reports/09_despliegue.md` y `especificacion-proyecto.md` §7 |
| V. Nada sensible sale | ✅ | Perfiles inventados; sin `.env`, tokens ni datos de estudiantes |
| VI. El código es nuestro | ✅ | Funciones pequeñas con docstring en español; el grupo las revisa con el checklist |
| VII. No se inventan resultados | ✅ | Las cifras del aviso salen de la ficha; los puntajes de los perfiles salen de la ejecución |

## Diseño

### `predict.py`
Quitar `predict_with_scores`, `decide_min_cost`, `_ordered_proba` y la rama de clasificación de `validate_inputs`
(lanza `InputValidationError` si el esquema no es de regresión). Actualizar el docstring. En `tests/test_inference.py`
quitar las pruebas de clasificación y el modelo de juguete de clasificación; las de regresión no cambian.

### App (`app/streamlit_app.py`)
Funciones puras (se prueban sin Streamlit) y una función `main()` que dibuja:

- `form_to_row(answers: dict, schema) -> pd.DataFrame`: traduce las respuestas de texto a la fila de 21 columnas
  (personas «1 a 2» → 1 …; cuartos «Uno» → 1 …; estrato «Sin estrato» → vacío + `sin_estrato` = 1; «Sin respuesta» → vacío)
  y junta los mensajes de corrección (edad inválida, obligatorios vacíos). Si hay mensajes, lanza `InputValidationError`.
- `format_estimate(score) -> str` y el rango de referencia (P3).
- Los mapas de texto a código se importan de `proyecto.data.cleaning` (`HOUSEHOLD_SIZE_CODES`, `ROOM_CODES`) para no
  duplicarlos.
- Etiquetas en un diccionario `LABELS` en la app (español claro); el aviso de uso responsable en una constante con las
  cifras de la ficha. El esquema no cambia, salvo `municipality_names` si se aprueba P2 (calculado con el entrenamiento).
- `st.form` con tres secciones; listas con `index=None` y marcador «Elige una opción» para que un obligatorio vacío se
  detecte; «Sin respuesta» solo como opción en los campos `nullable`.
- Errores con `st.error` («Revisa estos datos: …»); advertencias de municipio con `st.warning`; resultado con `st.metric`.

### Notebook 09
Reemplazar las celdas de la plantilla: cargar modelo y esquema; 4 perfiles inventados construidos con `form_to_row`
(los mismos textos que vería la app); tabla con su puntaje redondeado; un ejemplo rechazado (edad 12) con su mensaje.

### Pruebas (`tests/test_app.py`, nuevo)
AppTest sobre `app/streamlit_app.py` (se salta si falta `models/model.joblib`): carga y aviso visible; perfil normal →
puntaje entero en [100, 477]; «Sin respuesta» en los 12 campos → puntaje; edad 12 y «abc» → error que nombra la edad y
sin puntaje; obligatorio vacío → error que lo nombra. Pruebas unitarias de `form_to_row` (códigos, regla 7b). Prueba de que
el código de la app no contiene `mlflow`, `databricks` ni `token`.

### Documentación y revisión
`reports/09_despliegue.md` (sin desplegar: decisiones, pruebas locales con resultados reales, plan de despliegue y plan B;
el ensayo cronometrado queda pendiente porque son datos de la clase), `reports/documentacion_proyecto.md`,
`especificacion-proyecto.md` §7, `reports/auditoria_etapa9.md` (auditor-de-fuga + búsqueda de datos sensibles).

## Preguntas para el grupo (respondidas el 6 nov 2026)

**Respuestas:** P1 campo numérico entero sin mínimo ni máximo (fuera de 13–80 → mensaje); P2 nombre y código;
P3 sí, con la frase «se equivoca en promedio 33 puntos; como referencia, entre X y Y»; P4 el género se mantiene.
**Ajuste al implementar:** las funciones puras del formulario van en `src/proyecto/inference/form.py` y no en la app,
para que el notebook 09 las importe de `src/` (`CLAUDE.md`).

- **P1 · Edad:** ¿campo de texto (permite mostrar el mensaje de corrección con «12» o «abc») o campo numérico con flechas
  limitado a 13–80 (no deja escribir un valor inválido, así que el mensaje solo saldría en `predict`)? *Recomendado: texto.*
- **P2 · Municipios:** ¿mostrar «NOMBRE (código)» con los nombres del entrenamiento (cada código tiene un solo nombre;
  se guarda en `input_schema.json` como `municipality_names`), o solo el código DANE? *Recomendado: nombre y código.*
- **P3 · Rango:** ¿mostrar además «como referencia: entre X y Y puntos» (estimación ± 33, recortado a 100–477)? Aclarando
  que **no** es un intervalo de confianza: el error típico es un promedio. *Recomendado: sí, con esa aclaración.*
- **P4 · Género:** la ficha dice que su uso como entrada está pendiente de revisión. El modelo lo necesita, así que la app
  lo pide. ¿Lo confirman para esta etapa?

## Complexity Tracking

Sin violaciones.

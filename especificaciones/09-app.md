# Especificación · Etapa 9 · Inferencia y app

> Se llena **antes** de escribir código, a partir de `models/ficha_modelo.md`, `models/input_schema.json` y la guía
> `material-del-curso/kit/guia-validacion-registro-y-app.md` (secciones 7 a 11). Claude la lee y la implementa; ustedes
> revisan que el código haga **exactamente** esto.

**Grupo:** Predictor de resultados Pruebas Saber 11 en Antioquia   **Fecha:** 6 nov 2026   **Estado:** ☐ borrador  ☒ cerrada (falta la revisión del grupo con el checklist)

> Borrador preparado por Claude a partir del pedido del grupo del 6 nov 2026. Las cifras salen de `models/ficha_modelo.md`
> (prueba, 5 nov 2026). Plan y tareas aprobados por el grupo el 6 nov 2026, con las respuestas a P1–P4 que se ven abajo.

## 1. Entrada

- `models/model.joblib` y `models/input_schema.json` (etapa 8). La app y el notebook 09 **solo** leen estos dos archivos.
- **No** se usa Databricks, ni MLflow, ni `data/processed/test.joblib`. El notebook 09 tampoco abre la prueba.

## 2. Inferencia (`src/proyecto/inference/predict.py`)

- Queda **solo la regresión**: `load_model`, `validate_inputs` y `predict_score`, que devuelve la columna
  `puntaje_estimado` (sin redondear; el redondeo es cosa de la app).
- Se quitan las funciones de clasificación de la plantilla: `predict_with_scores`, `decide_min_cost` y `_ordered_proba`,
  junto con sus pruebas. `validate_inputs` exige un esquema de regresión (`task="regression"`).
- `schema.py` no se toca en esta etapa.
- La traducción del formulario a las 21 columnas va en `src/proyecto/inference/form.py` (`form_to_row`), para que la
  usen la app y el notebook 09 desde `src/` y tenga pruebas.

## 3. App (`app/streamlit_app.py`)

| Qué | Cómo |
|---|---|
| Título | «Predictor de resultados Pruebas Saber 11 en Antioquia» |
| Etiquetas | En español claro, agrupadas en **Colegio**, **Estudiante** y **Hogar** (por ejemplo «Jornada del colegio», no `cole_jornada`) |
| Personas y cuartos del hogar | Como texto: «1 a 2», «3 a 4», «5 a 6», «7 a 8», «9 o más» y «Uno» … «Seis o más». La app los convierte a los códigos 1–5 y 1–6 de la etapa 3 |
| Estrato | Un solo campo: «1» … «6», «Sin estrato», «Sin respuesta». La app lo convierte a `fami_estratovivienda` + `sin_estrato` (regla 7b) |
| «Sin respuesta» | Solo en los 12 campos que admiten vacío (`nullable` del esquema): edad, estrato, personas, cuartos, bilingüe, carácter, educación de la madre y del padre, automóvil, computador, internet y lavadora. Los otros 9 son obligatorios |
| Edad | **P1 (grupo):** campo numérico entero **sin mínimo ni máximo**, más la casilla «Sin respuesta»; fuera de 13–80 → mensaje de corrección |
| Municipios | **P2 (grupo):** nombre y código, por ejemplo «MEDELLÍN (5001)»; clave `municipality_names` en el esquema, calculada con el entrenamiento |
| Resultado | **P3 (grupo):** puntaje redondeado a entero y «se equivoca en promedio 33 puntos; como referencia, entre X y Y» (estimación ± 33, recortada a 100–477), aclarando que no es un intervalo de confianza |
| Entrada inválida | Mensaje que dice **qué corregir** (por ejemplo «Edad: escribe un número entero entre 13 y 80») y **ninguna** estimación |
| Campo obligatorio vacío | Mensaje con el nombre del campo que falta |
| Municipio no visto | Advertencia, no error (decisión de la etapa 8) |
| Aviso de uso responsable | Siempre visible, con los límites de la ficha: orienta y no excluye; solo calendario A, Antioquia, 2022; explica el 36 % de la variación (R² 0,363); en **estrato 5 el MAE es 39,57**; **hombres 35,74 frente a 31,40 en mujeres**; no oficiales 35,55 |
| Databricks | **No.** La app no importa `mlflow` ni `databricks` y no lleva credenciales |
| Género | **P4 (grupo):** se mantiene como entrada; la ficha anota que quitarlo exigiría reentrenar y volver a evaluar con la prueba, que ya se abrió |

## 4. Notebook 09

- Carga `models/model.joblib` y `models/input_schema.json`, sin Databricks y sin la prueba.
- 3–4 **perfiles inventados** (no salen de los datos) con su puntaje estimado, y un **ejemplo rechazado** con su mensaje.
- Se quitan las celdas de la plantilla que exportaban desde el registro y comparaban con la prueba: eso ya se hizo en la
  etapa 8 (`reports/08_registro.md`).

## 5. Pruebas que deben existir

- ☒ `predict.py`: ya no existen las funciones de clasificación; las pruebas de regresión siguen en verde.
- ☒ AppTest: la app carga con el título y el aviso de uso responsable visible.
- ☒ AppTest: un perfil normal muestra un puntaje entero y el error típico.
- ☒ AppTest: «Sin respuesta» en los campos que lo admiten no rompe nada.
- ☒ AppTest: una edad inválida y un campo obligatorio vacío muestran un mensaje de corrección y **ninguna** estimación.
- ☒ El código de la app no menciona `mlflow`, `databricks` ni tokens.
- ☒ `pytest` en verde (103 de 103, 6 nov 2026).

## 6. Criterios de cierre

- ☒ La app corre en local con `streamlit run app/streamlit_app.py`.
- ☒ Notebook 09 ejecutado de principio a fin.
- ☒ `reports/09_despliegue.md` completo **sin desplegar** (plan B y plan de despliegue escrito).
- ☒ `reports/documentacion_proyecto.md` actualizado (regla 10 de `CLAUDE.md`).
- ☒ Auditoría con `auditor-de-fuga` en `reports/auditoria_etapa9.md`.
- ☒ Sin datos sensibles en lo que se sube: `.env`, tokens, correos, direcciones del espacio de trabajo, datos de estudiantes.
- ☒ Todo subido a GitHub.
- ☐ Revisión del código de Claude por el grupo con `material-del-curso/kit/checklist-revision-ia.md`.

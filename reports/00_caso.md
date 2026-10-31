# Ficha de caso

- **case_id:** `saber11-antioquia`

- **business_question:** Hoy el puntaje de un estudiante en Saber 11 solo se conoce después de presentar la prueba,
  cuando ya no hay tiempo de actuar. Queremos estimar el **puntaje global** que puede esperar un estudiante de Antioquia
  a partir de las características de su colegio, su perfil y su familia, e identificar **qué factores influyen más**.
  El resultado se entrega en una app web y lo usan: la **Secretaría de Educación**, para decidir a qué colegios o
  municipios dirigir programas de refuerzo; **rectores y docentes**, para decidir qué estudiantes de grado 11 necesitan
  preparación adicional; y **estudiantes y familias**, para decidir a qué universidad o beca aspirar y si conviene
  invertir en preparación. El modelo orienta; la decisión la toma una persona.

- **dataset_source:** Resultados oficiales del ICFES, prueba Saber 11, publicados en datos.gov.co (recurso `kgxf-xxbe`),
  filtrado a periodo 20224 y departamento ANTIOQUIA. Se descarga a `data/raw/saber11_antioquia_2022.csv` con:
  `https://www.datos.gov.co/resource/kgxf-xxbe.csv?$where=periodo=%2720224%27%20AND%20cole_depto_ubicacion=%27ANTIOQUIA%27&$order=estu_consecutivo&$limit=200000`.
  **Licencia: por confirmar.**

- **dataset_rows:** 144.766 filas descargadas, que corresponden a **72.383 estudiantes**: cada fila viene duplicada
  exactamente en la fuente. Los duplicados se eliminan antes de cualquier análisis.

- **dataset_columns:** 51 (incluye `estu_consecutivo`, identificador del estudiante, y `estu_fechanacimiento`, que son
  datos personales).

- **target:** `punt_global` (de 100 a 477 puntos; promedio 245,9, mediana 242, sin valores vacíos). El modelo usa solo
  variables del colegio (`cole_`), del estudiante (`estu_`) y de la familia (`fami_`). Se excluyen por fuga de
  información: `punt_matematicas`, `punt_lectura_critica`, `punt_sociales_ciudadanas`, `punt_c_naturales` y
  `punt_ingles` (el puntaje global se calcula con ellas), `desemp_ingles` (sale del resultado de inglés) y
  `estu_estadoinvestigacion` (se conoce después del examen).

- **problem_type:** regresión

- **primary_metric:** **MAE** (error absoluto medio, en puntos; menor es mejor), porque los dos errores cuestan lo mismo
  y el costo crece en proporción a los puntos de error, que es justo lo que mide el MAE. Además se explica sin formación
  técnica: "el modelo se equivoca en promedio ±N puntos". Como controles se reportan **RMSE** (revela errores muy grandes)
  y **R²**. Línea base sin modelo: predecir siempre la mediana da un **MAE de 42,8 puntos** (siempre el promedio: 42,9;
  al azar: 58,9). Meta para decir que el modelo «sirve»: por definir con el grupo.

- **business_cost_note:** Equivocarse cuesta lo mismo en las dos direcciones (proporción 1 a 1).
  - **Sobreestimar** (decir que le irá mejor de lo real): un estudiante o colegio puede quedarse sin el apoyo que
    necesitaba.
  - **Subestimar** (decir que le irá peor de lo real): se dirigen recursos de refuerzo a quien no los necesitaba o se
    desanima al estudiante.
  - El grupo decidió darles el mismo peso porque la app la usan perfiles distintos y ninguno de los dos errores es
    claramente más grave para todos. El costo de un error de 10 puntos es el mismo hacia arriba o hacia abajo.

- **status:** borrador

- **reviewer_notes:**

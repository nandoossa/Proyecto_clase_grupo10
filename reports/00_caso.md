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
  **Licencia:** Creative Commons Atribución-CompartirIgual 4.0 Internacional (CC BY-SA 4.0), según los metadatos del
  recurso `kgxf-xxbe` en datos.gov.co (consultado el 31 oct 2026). Fuente: Instituto Colombiano para la Evaluación de
  la Educación (ICFES). Permite usar y transformar los datos, incluso con fines comerciales, siempre que se dé crédito
  al ICFES, se indique la licencia y que los datos fueron modificados; si se publica una versión modificada de los
  datos, debe compartirse bajo la misma licencia. Los datos usados aquí están filtrados a Antioquia, periodo 20224, y
  sin filas duplicadas.

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
  al azar: 58,9). Meta para decir que el modelo «sirve» (acordada por el grupo):
  - **Meta mínima: MAE ≤ 38 puntos** en validación cruzada agrupada por sede (`cole_cod_dane_sede`, `GroupKFold`), al
    menos un 11 % mejor que la línea base de 42,8. Se agrupa por sede para medir el error con colegios nunca vistos, como
    en la app (decisión 10 del EDA).
  - **Meta deseable: MAE ≤ 35 puntos** (18 % mejor que la línea base), medida de la misma forma.
  - **Condición de equidad:** el MAE del modelo debe ser **menor que el de la línea base en cada segmento** de estrato
    (`fami_estratovivienda`, con «Sin Estrato» y los vacíos como segmentos propios), zona (`cole_area_ubicacion`) y
    naturaleza del colegio (`cole_naturaleza`). Motivo: un MAE promedio bueno puede esconder un grupo en el que el modelo
    se equivoca más que no usar modelo, y esas variables marcan a grupos en desventaja.

  Línea base por segmento (predecir siempre la mediana global, 242 puntos; 72.383 estudiantes sin duplicados; calculada
  en `notebooks/01_caso_negocio.ipynb`, sección 3):

  | Variable | Segmento | Estudiantes | MAE línea base (puntos) |
  |---|---|---:|---:|
  | Estrato | Estrato 1 | 14.173 | 38,4 |
  | Estrato | Estrato 2 | 26.652 | 39,5 |
  | Estrato | Estrato 3 | 18.596 | 44,4 |
  | Estrato | Estrato 4 | 4.317 | 54,5 |
  | Estrato | Estrato 5 | 1.694 | 65,8 |
  | Estrato | Estrato 6 | 668 | 68,2 |
  | Estrato | Sin Estrato | 1.561 | 46,6 |
  | Estrato | Sin dato (vacío) | 4.722 | 44,6 |
  | Zona | Rural | 12.539 | 42,7 |
  | Zona | Urbano | 59.844 | 42,8 |
  | Naturaleza | No oficial | 14.753 | 53,4 |
  | Naturaleza | Oficial | 57.630 | 40,1 |

  La línea base se equivoca más en los estratos 5 y 6 y en los colegios no oficiales (puntajes lejos de 242) y menos en
  los estratos 1 y 2. En el estrato 1 (38,4) ya está casi en la meta mínima global, así que cumplir la meta global no
  garantiza la condición de equidad.

- **business_cost_note:** Equivocarse cuesta lo mismo en las dos direcciones (proporción 1 a 1).
  - **Sobreestimar** (decir que le irá mejor de lo real): un estudiante o colegio puede quedarse sin el apoyo que
    necesitaba.
  - **Subestimar** (decir que le irá peor de lo real): se dirigen recursos de refuerzo a quien no los necesitaba o se
    desanima al estudiante.
  - El grupo decidió darles el mismo peso porque la app la usan perfiles distintos y ninguno de los dos errores es
    claramente más grave para todos. El costo de un error de 10 puntos es el mismo hacia arriba o hacia abajo.

- **status:** borrador

- **reviewer_notes:**

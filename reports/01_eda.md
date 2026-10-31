# Informe del EDA — Saber 11 Antioquia

Resultado de `notebooks/02_eda.ipynb` (30 oct 2026). Cada hallazgo termina en una decisión. Las decisiones se
implementan con pruebas en `src/proyecto/data/` en la etapa 3 (preprocesamiento).

## Qué son los datos

- **Filas × columnas:** 144.766 × 51 en el archivo descargado; **72.383 filas** al quitar duplicados exactos.
- **Unidad de análisis (qué es una fila):** un estudiante que presentó Saber 11 en el periodo 20224 en un colegio de
  Antioquia.
- **¿Una entidad aparece en varias filas?** El estudiante, no: cada fila viene **duplicada exactamente** en la fuente
  (2 filas por estudiante) y, al quitar duplicados, ningún estudiante se repite. El **colegio-sede** sí agrupa a muchos
  estudiantes: 1.447 sedes, mediana de 33 estudiantes por sede (de 1 a 618); 319 sedes tienen menos de 10. La sede sola
  explica el **36 %** de la variación del puntaje (el municipio, el 11 %).
- **Objetivo y distribución:** `punt_global`, de 100 a 477 puntos; promedio 245,9, mediana 242, desviación 51,6. Sin
  vacíos ni valores fuera de la escala 0–500. Casi simétrico (asimetría 0,31): no hace falta transformarlo.
- **Línea base** (resultado de una regla trivial): predecir siempre la mediana da un **MAE de 42,8 puntos**.

## Calidad de los datos

- **Duplicados:** 72.383 filas exactamente duplicadas (50 % del archivo).
- **Números guardados como texto:** estrato ("Estrato 1"…"Estrato 6"), personas en el hogar ("1 a 2"…"9 o más") y
  cuartos ("Uno"…"Seis o mas") son categorías con orden natural guardadas como texto.
- **Centinelas:** "No sabe" (1.695 en educación de la madre, 5.966 del padre), "No Aplica" (156 / 1.255) y
  "Sin Estrato" (1.561, con puntaje promedio de 211,2, el más bajo de todos los estratos).
- **Vacíos que significan algo:** el 10,1 % de los estudiantes tiene algún vacío en las variables `fami_` (1.790 no
  respondieron ninguna), y sacan en promedio **~18 puntos menos** (229,2 vs. 247,8). `cole_bilingue` tiene 16,4 % de
  vacíos, con 16 puntos menos (232,6 vs. 248,5). El vacío no es aleatorio.
- **Valores imposibles:** 30 estudiantes con edad aproximada menor de 13 años (incluso 0 años). Los adultos (1.807 entre
  26 y 60 años; 28 mayores de 60) son plausibles: personas que validan el bachillerato.
- **Variables que deberían ser estables:** las características del colegio (municipio, zona, naturaleza, calendario,
  carácter, bilingüe, género) son constantes dentro de cada sede (0 % de sedes con más de un valor). `cole_jornada`
  varía en el 20,7 % de las sedes, pero es un cambio real: una sede puede tener varias jornadas.
- **Columnas sin información:** `periodo`, `cole_cod_depto_ubicacion`, `cole_depto_ubicacion` y `estu_estudiante` tienen
  un solo valor. `estu_nacionalidad`, `estu_pais_reside` y `estu_depto_reside` tienen el 98,5 % o más en un solo valor.
- **Alta cardinalidad:** 125 municipios de colegio, 173 de residencia, 1.447 sedes. 30 nombres de sede corresponden a más
  de un código: ningún identificador del colegio se usa como predictor (decisión 9).
- **Calendario:** 72.148 estudiantes en calendario A y 235 (0,3 %) en "OTRO", en 3 sedes, con puntaje promedio de 227,1.
  No hay calendario B.
- **Datos personales:** `estu_consecutivo` (identificador del estudiante) y `estu_fechanacimiento`.

## Sospechas de fuga de información

- `punt_matematicas`, `punt_lectura_critica`, `punt_sociales_ciudadanas`, `punt_c_naturales` y `punt_ingles`: correlación
  de 0,80 a 0,92 con `punt_global`, que se calcula con ellas. Son la respuesta.
- `desemp_ingles`: el puntaje promedio sube de 211,8 (A-) a 347,6 (B+); sale del resultado de inglés.
- `estu_estadoinvestigacion`: 26 estudiantes en revisión jurídica; se conoce después del examen.

## Decisiones

Todas son propuestas pendientes del acuerdo del grupo (10 y 11 propuestas por el grupo el 30 oct 2026; 1 a 9 propuestas en
el EDA). Si el grupo está de acuerdo, se aplican en `notebooks/03_preprocesamiento.ipynb`.

| # | Hallazgo (con cifra) | Decisión | Motivo |
|---|---|---|---|
| 1 | 72.383 filas exactamente duplicadas (50 % del archivo) | Eliminar duplicados exactos al cargar | Un mismo estudiante en entrenamiento y prueba haría que la métrica saliera optimista |
| 2 | 5 puntajes por área con correlación de 0,80–0,92 con el objetivo; `desemp_ingles` y `estu_estadoinvestigacion` se conocen después del examen | Excluir las 7 columnas | Son la respuesta o información posterior: fuga |
| 3 | `estu_consecutivo` identifica al estudiante; `estu_fechanacimiento` es dato personal | Usar `estu_consecutivo` solo para controlar duplicados (nunca como variable); convertir la fecha de nacimiento en edad y eliminarla | No exponer datos personales; la edad conserva la información útil |
| 4 | 30 estudiantes con edad menor de 13 años | Edad < 13 → vacío (sin borrar la fila) | Es imposible presentar Saber 11 a esa edad; borrar filas perdería el resto de su información |
| 5 | 10,1 % con algún vacío en `fami_`, con ~18 puntos menos de promedio; `cole_bilingue` 16,4 % vacío, 16 puntos menos | Imputar vacíos como categoría propia "sin respuesta" dentro del `Pipeline` | El vacío es información, no ruido: imputar con la moda la borraría |
| 6 | Centinelas: "No sabe" (1.695 / 5.966), "No Aplica" (156 / 1.255), "Sin Estrato" (1.561, puntaje 211,2) | Mantenerlos como categorías propias (no convertir a vacío) | Tienen puntajes distintos al resto: llevan información |
| 7 | Estrato, personas y cuartos del hogar son categorías ordenadas guardadas como texto | Convertirlas a números ordenados | Conservar el orden ayuda al modelo y simplifica la app |
| 8 | 4 columnas con un solo valor (`periodo`, `cole_cod_depto_ubicacion`, `cole_depto_ubicacion`, `estu_estudiante`) | Eliminarlas | No aportan información |
| 9 | Las columnas que identifican al colegio (`cole_cod_dane_sede`, `cole_cod_dane_establecimiento`, `cole_codigo_icfes`, `cole_nombre_establecimiento`, `cole_nombre_sede`) tienen 1.071 a 1.807 valores distintos; 30 nombres de sede se repiten en varios códigos | Excluirlas como predictores. `cole_cod_dane_sede` se conserva **solo para agrupar** al partir (decisión 10). Se mantienen los atributos del colegio: naturaleza, jornada, calendario, zona, bilingüe, carácter, género y municipio | En prueba aparecerían colegios nunca vistos, y en entrenamiento el modelo memorizaría el promedio de cada colegio en vez de aprender de sus características; los atributos sí los puede ingresar el usuario de la app para cualquier colegio |
| 10 | La sede explica el 36 % de la variación del puntaje; 1.447 sedes | Partir entrenamiento/prueba y validación cruzada **por sede** (`cole_cod_dane_sede`, `GroupShuffleSplit` / `GroupKFold`) | Mide el error con colegios que el modelo nunca vio, como en la app; partir por estudiante daría un MAE optimista |
| 11 | 235 estudiantes (0,3 %) de calendario "OTRO" en 3 sedes; no hay calendario B | Excluirlos. Alcance: el modelo aplica a estudiantes de **calendario A** | Muy pocos casos para aprender algo confiable; simplifica el modelo y el formulario de la app |

## Qué queda abierto

- **Revisión del grupo** de las decisiones 1 a 9.
- **Identificadores fuera del modelo:** ninguna columna que identifique al colegio (`cole_cod_dane_sede`, `cole_cod_dane_establecimiento`, `cole_codigo_icfes`, `cole_nombre_establecimiento`, `cole_nombre_sede`) ni al
  estudiante (`estu_consecutivo`) entra como predictor. `cole_cod_dane_sede` se usa solo para agrupar en la partición.
  Hay que comprobar en la etapa 3 que ninguna se cuele en el `Pipeline`.
- **Cómo codificar las variables de alta cardinalidad** que sí quedan (municipios del colegio y de residencia): se
  decide en la etapa de features.
- **Equidad:** estrato, naturaleza del colegio, internet y zona se relacionan con el puntaje (estrato 1 ~231 vs.
  estrato 5 ~281). Se revisará el error del modelo por segmento en la validación.
- **La edad es aproximada** (año de la prueba − año de nacimiento).

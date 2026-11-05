# Especificación · Etapa 2 · EDA

> Se llena **antes** de abrir `notebooks/02_eda.ipynb` (las secciones 1 y 2) y se completa **mientras**
> lo ejecutan (3 y 4). El resultado final, con las decisiones, va a `reports/01_eda.md`.
> Guía: `material-del-curso/kit/guia-eda-y-preprocesamiento.md` · Ejemplo: `material-del-curso/ejemplo-creditsight/reports/01_eda.md`.

**Grupo:** _______________   **Fecha:** 30 oct 2026   **Estado:** ☒ borrador  ☐ cerrada

## 1. Qué esperamos encontrar (se escribe ANTES de mirar los datos)

Una hipótesis por pregunta. Si después no se cumple, es un hallazgo: anótenlo.

> Nota honesta: esta sección se escribió después de una primera mirada a los datos (al preparar el caso de negocio ya
> vimos los duplicados y las columnas de puntaje). Lo que ya sabíamos se marca como *(ya observado)*.

| Pregunta | Lo que creemos |
|---|---|
| ¿Qué representa una fila? | Un estudiante que presentó Saber 11 en el periodo 20224 en un colegio de Antioquia. |
| ¿Alguna entidad se repite en varias filas? | El estudiante (`estu_consecutivo`) debería aparecer una sola vez, pero cada fila viene duplicada exactamente *(ya observado: 144.766 filas = 72.383 estudiantes)*. Además, muchos estudiantes comparten **colegio** (`cole_cod_dane_sede`): hay que decidir si la partición se hace por estudiante o por colegio. |
| ¿Qué variable **debería** ser estable y no cambiar? | Dentro de un mismo colegio-sede: municipio, zona, naturaleza (oficial/no oficial), calendario y carácter deberían ser iguales para todos sus estudiantes. |
| ¿Qué significaría un vacío en nuestras columnas clave? | En las variables `fami_` (estrato, educación de los padres, bienes del hogar), un vacío probablemente significa que el estudiante no respondió el formulario socioeconómico; puede no ser al azar (relacionado con el puntaje). En `cole_bilingue`, un vacío puede significar "no reportado". |
| ¿Qué columna solo se conoce **después** de la decisión que queremos apoyar? | Los puntajes por área (`punt_*`), `desemp_ingles` y `estu_estadoinvestigacion` *(ya observado)*. |

## 2. Qué vamos a medir

Marquen lo que aplica a su dataset. Lo que no aplique se tacha **con una razón** (no se deja en blanco).

| Chequeo (guía, sección 3) | ¿Aplica? | Columnas a revisar | Quién lo hace |
|---|---|---|---|
| 3.1 Números guardados como texto | ☒ sí ☐ no: | `fami_cuartoshogar` ("Uno", "Dos"…), `fami_personashogar` ("3 a 4"…), `fami_estratovivienda` ("Estrato 2"…): son categorías ordenadas guardadas como texto | |
| 3.2 Valores centinela (`-1`, `9999`, `?`) | ☒ sí ☐ no: | Respuestas "No sabe", "No Aplica", "Sin Estrato" en `fami_educacionmadre`, `fami_educacionpadre`, `fami_estratovivienda` | |
| 3.3 Valores imposibles (percentiles, negativos) | ☒ sí ☐ no: | `estu_fechanacimiento` (edad al presentar la prueba), `punt_global` (rango 0–500) | |
| 3.4 Constancia por entidad | ☒ sí ☐ no: | Por colegio-sede (`cole_cod_dane_sede`): `cole_mcpio_ubicacion`, `cole_area_ubicacion`, `cole_naturaleza`, `cole_calendario`, `cole_caracter` | |
| 3.5 Vacíos que significan algo | ☒ sí ☐ no: | Todas las `fami_`, `cole_bilingue`, `cole_caracter`; comparar el puntaje de quienes tienen vacío vs. quienes no | |
| 3.6 Duplicados | ☒ sí ☐ no: | Filas completas y `estu_consecutivo` | |
| 3.7 Fechas y orden temporal | ☐ sí ☒ no: un solo periodo (20224), no hay orden temporal entre filas. La única fecha (`estu_fechanacimiento`) se revisa en 3.3 | — | — |
| 3.8 Categorías raras / alta cardinalidad | ☒ sí ☐ no: | Alta cardinalidad: municipios (`cole_mcpio_ubicacion`, `estu_mcpio_reside`), códigos y nombres de colegio/sede. Raras: `estu_nacionalidad`, `estu_tipodocumento`, `cole_jornada` | |
| 3.9 Identidad y datos personales | ☒ sí ☐ no: | `estu_consecutivo`, `estu_fechanacimiento`, `estu_tipodocumento`; columnas constantes sin información (`periodo`, `cole_depto_ubicacion`, `estu_estudiante`) | |

## 3. Lo que medimos (se llena mientras corre el notebook)

- **Filas × columnas:** 144.766 × 51 descargadas; 72.383 filas sin duplicados exactos
- **Unidad de análisis (una frase):** un estudiante que presentó Saber 11 en el periodo 20224 en un colegio de Antioquia.
- **Columna que identifica a la entidad (`ID_COL`):** `estu_consecutivo`   **¿Se repite?** ☐ no ☒ sí, 2 filas por entidad (duplicados exactos de la fuente; 1 al quitarlos). Grupo para partir: `cole_cod_dane_sede` (1.447 sedes; explica el 36 % de la variación del puntaje)
- **Objetivo (`TARGET`):** `punt_global`   **Distribución:** 100–477 puntos, promedio 245,9, mediana 242, desviación 51,6, casi simétrica (asimetría 0,31)
- **Línea base** (regla trivial) y su resultado: predecir siempre la mediana → MAE = 42,8 puntos
- **Vacíos en el objetivo:** 0   **Qué haremos con esas filas:** no aplica
- **Datos personales encontrados:** `estu_consecutivo` (identificador) y `estu_fechanacimiento`
- **Columnas sospechosas de fuga:** `punt_matematicas`, `punt_lectura_critica`, `punt_sociales_ciudadanas`, `punt_c_naturales`, `punt_ingles` (correlación 0,80–0,92), `desemp_ingles`, `estu_estadoinvestigacion` (se miden con y sin ellas en la etapa 4)

## 4. Decisiones (mínimo 5)

> Cada una con **cifra**, acción **concreta** y **motivo**. Se copian tal cual a `reports/01_eda.md`.
> Cada decisión se convierte en una función de `src/proyecto/data/` y en una prueba (ver `03-preprocesamiento.md`).
>
> Todas fueron aprobadas por el grupo el 31 oct 2026, sin cambios; se aplican en
> `notebooks/03_preprocesamiento.ipynb`. Las funciones se definen en la etapa 3 (plan y tareas antes del código).

| # | Hallazgo (con cifra) | Decisión | Motivo | Función que la implementa |
|---|---|---|---|---|
| 1 | 72.383 filas exactamente duplicadas (50 % del archivo) | Eliminar duplicados exactos al cargar | Un mismo estudiante en entrenamiento y prueba haría que la métrica saliera optimista | por definir (etapa 3) |
| 2 | 5 puntajes por área con correlación de 0,80–0,92 con el objetivo; `desemp_ingles` y `estu_estadoinvestigacion` se conocen después del examen | Excluir las 7 columnas | Son la respuesta o información posterior: fuga | por definir (etapa 3) |
| 3 | `estu_consecutivo` identifica al estudiante; `estu_fechanacimiento` es dato personal | Usar `estu_consecutivo` solo para controlar duplicados; convertir la fecha de nacimiento en edad y eliminarla | No exponer datos personales; la edad conserva la información útil | por definir (etapa 3) |
| 4 | 30 estudiantes con edad menor de 13 años | Edad < 13 → vacío (sin borrar la fila) | Imposible a esa edad; borrar filas perdería el resto de su información | por definir (etapa 3) |
| 5 | 10,1 % con algún vacío en `fami_` (~18 puntos menos); `cole_bilingue` 16,4 % vacío (16 puntos menos) | Imputar vacíos como categoría "sin respuesta" dentro del `Pipeline` | El vacío es información, no ruido | por definir (etapa 3) |
| 6 | "No sabe" (1.695 / 5.966), "No Aplica" (156 / 1.255), "Sin Estrato" (1.561, puntaje 211,2) | Mantenerlos como categorías propias | Tienen puntajes distintos al resto: llevan información | por definir (etapa 3) |
| 7 | Estrato, personas y cuartos del hogar: categorías ordenadas guardadas como texto | Convertirlas a números ordenados | Conservar el orden ayuda al modelo y simplifica la app | por definir (etapa 3) |
| 8 | 4 columnas con un solo valor | Eliminarlas | No aportan información | por definir (etapa 3) |
| 9 | Las columnas que identifican al colegio (`cole_cod_dane_sede`, `cole_cod_dane_establecimiento`, `cole_codigo_icfes`, `cole_nombre_establecimiento`, `cole_nombre_sede`) tienen 1.071 a 1.807 valores distintos; 30 nombres de sede se repiten en varios códigos | Excluirlas como predictores. `cole_cod_dane_sede` se conserva **solo para agrupar** al partir (decisión 10). Se mantienen los atributos del colegio: naturaleza, jornada, calendario, zona, bilingüe, carácter, género y municipio | En prueba aparecerían colegios nunca vistos, y en entrenamiento el modelo memorizaría el promedio de cada colegio en vez de aprender de sus características; los atributos sí los puede ingresar el usuario de la app para cualquier colegio  por definir (etapa 3) |
| 10 | La sede explica el 36 % de la variación; 1.447 sedes | Partir y validar **por sede** (`GroupShuffleSplit` / `GroupKFold`) | Mide el error con colegios nunca vistos, como en la app | por definir (etapa 3) |
| 11 | 235 estudiantes (0,3 %) de calendario "OTRO" en 3 sedes; no hay calendario B | Excluirlos; alcance: calendario A | Muy pocos casos para aprender algo confiable | por definir (etapa 3) |

## 5. Criterios de cierre

- ☒ `notebooks/02_eda.ipynb` corre de principio a fin sin errores.
- ☒ Unidad de análisis y `ID_COL` declarados por escrito (sección 3).
- ☒ Al menos **5 decisiones** con cifra, acción y motivo.
- ☒ Datos personales identificados y plan para eliminarlos al cargar.
- ☒ Valores imposibles, centinelas y significado de los vacíos revisados.
- ☒ Fuga sospechada: lista escrita, aunque sea "ninguna, porque…".
- ☒ `reports/01_eda.md` completado.
- ☒ Quien **no** escribió una decisión sabe explicar por qué se tomó (lo explicaron Jennifer Alejandra López Sánchez y
  Raúl Fernando Ossa Ramírez).

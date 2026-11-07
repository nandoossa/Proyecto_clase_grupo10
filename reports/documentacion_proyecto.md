# Documentación del trabajo realizado · Predictor de resultados Saber 11 en Antioquia

> Documentación general del proyecto, en lenguaje sencillo: de qué trata, qué se decidió y cuándo, qué resultados dio cada
> etapa y dónde está el detalle. **Estado al 7 nov 2026: etapas 1 a 9 completas; la app está publicada en Streamlit Community
> Cloud (https://predictorpruebasaber.streamlit.app) y se comprobó en una ventana privada.** Las cifras se copian de los informes de `reports/` y de las salidas de los
> notebooks; no hay cifras nuevas aquí. Este documento no reemplaza al informe técnico final (`reports/informe_tecnico.md`,
> hito H4): sirve de mapa para escribirlo.

**Grupo:** Jennifer Alejandra López Sánchez, Jaime Andrés Úsuga Jiménez, Raúl Fernando Ossa Ramírez, David Andrés Paniagua
Gutiérrez, Sebastián Orozco Giraldo · **Repositorio:** https://github.com/nandoossa/Proyecto_clase_grupo10

---

## Resumen en una página

- **Pregunta de negocio:** ¿qué puntaje global en Saber 11 puede esperar un estudiante de Antioquia según su colegio, su
  perfil y su familia, y qué factores influyen más? La usarán la Secretaría de Educación, rectores y docentes, y estudiantes
  y familias. El modelo orienta; la decisión la toma una persona.
- **Datos:** resultados oficiales del ICFES (datos.gov.co, licencia CC BY-SA 4.0), Antioquia, periodo 2022. Son 72.383
  estudiantes tras quitar duplicados exactos; quedan 72.148 de calendario A.
- **Métrica:** MAE en puntos («se equivoca en promedio ±N puntos»). Los dos errores cuestan lo mismo. Línea base sin modelo
  (predecir la mediana): 42,8. Metas: ≤ 38 (mínima) y ≤ 35 (deseable).
- **Modelo final:** HistGradientBoosting de scikit-learn con parámetros optimizados (pérdida de error absoluto, umbral de
  categorías poco frecuentes del 0,1 %).
- **Resultado en la prueba**, abierta una sola vez con 289 colegios nunca vistos:
  - **MAE 33,32**, con intervalo del 95 % [32,39 ; 34,21];
  - 9,77 puntos menos que no usar modelo, con intervalo de la diferencia [−11,78 ; −7,99];
  - cumple las dos metas;
  - cumple la condición de equidad en los 14 segmentos revisados.
- **Límites principales:**
  - explica el 36 % de la variación del puntaje (R² 0,363);
  - el error es mayor en estrato 5 (39,57), en hombres (35,74 frente a 31,40 en mujeres) y en colegios no oficiales (35,55);
  - aplica solo a calendario A, Antioquia, 2022.

## Estado de las etapas

| Etapa | Estado | Informe |
|---|---|---|
| 1 · Caso de negocio | Completa | `reports/00_caso.md` |
| 2 · Análisis exploratorio | Completa | `reports/01_eda.md` |
| 3 · Preprocesamiento y partición | Completa | `reports/auditoria_etapa3.md` |
| 4 · Variables | Completa | `reports/04_features.md` |
| 5 · Torneo de modelos | Completa | `reports/05_torneo.md` |
| 6 · Optimización con seguimiento | Completa | `reports/06_optimizacion.md` |
| 7 · Validación e interpretación | Completa | `reports/07_validacion.md` |
| 8 · Registro del modelo | Completa | `reports/08_registro.md`, `models/ficha_modelo.md` |
| 9 · Inferencia y app | Completa; app publicada | `reports/09_despliegue.md`, `reports/auditoria_etapa9.md` |
| 10 · Preparación del despliegue | Repositorio listo; hallazgos importantes corregidos; app publicada en https://predictorpruebasaber.streamlit.app y comprobada en una ventana privada (7 nov 2026) | `reports/despliegue_preparacion.md`, `reports/revision_app.md` |

## La variable objetivo y los datos

- **Variable objetivo:** `punt_global`, el puntaje global de Saber 11, de 100 a 477 puntos (promedio 245,9, mediana 242,
  sin vacíos). Es un problema de **regresión**: se estima un número, no una categoría.
- **Fuente:** resultados oficiales del ICFES publicados en datos.gov.co (recurso `kgxf-xxbe`), Antioquia, periodo 20224.
  Licencia CC BY-SA 4.0: hay que dar crédito al ICFES y compartir con la misma licencia los datos modificados que se
  publiquen.
- **Tamaño:** 144.766 filas descargadas, que son 72.383 estudiantes (cada fila venía duplicada); 51 columnas. Tras excluir
  el calendario «OTRO» quedan 72.148 estudiantes de calendario A.
- **Una fila = un estudiante.** La entidad que se repite es la **sede del colegio** (`cole_cod_dane_sede`): todo se parte
  por sede.
- **Predictores:** 21 columnas que se conocen antes del examen. Son 5 numéricas (edad, estrato, marca «Sin Estrato»,
  personas y cuartos del hogar), 14 categóricas (del colegio, del estudiante y de la familia) y 2 códigos de municipio.
- **Excluidas por fuga:** los 5 puntajes por área, `desemp_ingles` y `estu_estadoinvestigacion`.
- **Datos personales:** el identificador del estudiante se usa solo para quitar duplicados, y la fecha de nacimiento se
  convierte en edad y se elimina.

## Decisiones principales con su fecha

Registro completo en `especificacion-proyecto.md`, sección 7.

| Fecha | Decisión | Motivo |
|---|---|---|
| 30 oct 2026 (aprobadas el 31 oct) | Once decisiones del EDA: quitar duplicados, excluir columnas con fuga, convertir la fecha de nacimiento en edad, edad < 13 como vacío, vacíos como «sin respuesta», conservar «No sabe»/«No Aplica»/«Sin Estrato», ordinales como números, quitar columnas constantes, excluir identificadores del colegio, partir por sede, excluir calendario «OTRO» | Evitar fuga, proteger datos personales y medir con colegios no vistos |
| 31 oct 2026 | Metas: MAE ≤ 38 y ≤ 35; condición de equidad por segmento | Mejorar claramente la línea base de 42,8 sin perjudicar a ningún grupo |
| 31 oct 2026 | «Sin Estrato» como vacío más la marca `sin_estrato` | Un 0 inventaría un estrato |
| 31 oct 2026 | Excluir `estu_tipodocumento`, `estu_nacionalidad` y `estu_privado_libertad` | Equidad: indicadores de condición migratoria o datos sensibles |
| 31 oct 2026 | Prueba del 20 % por sede, semilla 42 | Medir con colegios que el modelo no vio |
| 31 oct 2026 | LightGBM reemplazado por HistGradientBoosting | LightGBM no carga en los equipos del grupo |
| 31 oct 2026 | Variables nuevas apagadas; umbral del 1 %, con el 0,1 % como candidato | Ninguna idea superó el ruido entre pliegues |
| 5 nov 2026 | Presupuesto de la optimización (25 + 30 ensayos) y reglas 1 y 2 | Escritas antes de buscar |
| 5 nov 2026 | Modelo elegido: HistGradientBoosting optimizado (pérdida absoluta, umbral 0,1 %) | Regla 1: mejora clara; regla 2: empate con XGBoost |
| 5 nov 2026, 19:53 | Decisiones congeladas para la prueba y regla de equidad con su clasificación | Escritas antes de abrir la prueba |
| 5 nov 2026, 19:55 | Prueba abierta una sola vez | Medición final con 289 sedes nunca vistas |
| 5 nov 2026 | Etapa 8: comprobar que el exportado es el evaluado sin volver a predecir sobre la prueba; rangos válidos (edad 13–80); vacíos aceptados solo donde el entrenamiento los tuvo; categorías nuevas rechazadas salvo municipios | No reabrir la prueba; que la app se niegue a responder con datos imposibles |
| 5 nov 2026, 20:31 | Modelo registrado como `workspace.default.saber11_puntaje_global` versión 1, alias `champion` | Saber qué modelo está en uso y en qué versión |
| 6 nov 2026 | Etapa 9: `predict.py` solo con regresión; formulario en español con edad numérica sin límites (fuera de 13–80 → mensaje), municipios con nombre y código, y «se equivoca en promedio 33 puntos; como referencia, entre X y Y» | Que quien usa la app entienda qué corregir y qué tan preciso es el puntaje, sin confundir la referencia con un intervalo de confianza |
| 6 nov 2026 | El género se mantiene como entrada | Quitarlo exigiría reentrenar y volver a evaluar con la prueba, que ya se abrió; la brecha de error se muestra en la app |
| 6 nov 2026 | Constitución ratificada (versión 1.0.0) con el principio VIII: el modelo orienta, no excluye ni etiqueta; su MAE por segmento de estrato, zona, naturaleza y género debe ser menor que el de la línea base | Regla del grupo que prevalece sobre las demás prácticas |
| 7 nov 2026 | H8 y H11 de la revisión de la app no se aplican | Esas situaciones no ocurren con nuestro esquema y nuestro formulario; aplicarlos cambiaría qué entradas se rechazan |

---

## Cómo se trabajó (reglas que se respetaron en todas las etapas)

| Regla | Cómo se cumplió |
|---|---|
| Constitución del proyecto | `.specify/memory/constitution.md`, versión 1.0.0 (ratificada el 6 nov 2026): principios I a VII del curso, ajustados al proyecto, y el principio VIII del grupo (el modelo orienta, no excluye; equidad por estrato, zona, naturaleza y género). Cada `plan.md` la revisa en su «Constitution Check» |
| Especificación → plan → tareas → código (Spec Kit) | Cada pieza nueva tiene su guía en `especificaciones/` y su `spec.md`, `plan.md` y `tasks.md` en `specs/`; el grupo aprobó plan y tareas antes del código |
| Partir por la unidad correcta | La sede del colegio (`cole_cod_dane_sede`) explica el 36 % de la variación del puntaje: partición, validación cruzada e intervalos se hacen **por sede** |
| La prueba se abre una sola vez | `test.joblib` se abrió solo en la etapa 7, después de congelar las decisiones con fecha y hora |
| Todo preprocesamiento dentro de un `Pipeline` | Imputación, codificación y modelo se ajustan solo con entrenamiento |
| Nada sensible sale del equipo | `.env` ignorado; identificador y fecha de nacimiento del estudiante eliminados; se ocultaron correo y enlaces de Databricks en los notebooks públicos |
| No se inventan cifras | Los informes usan solo cifras impresas por los notebooks |
| Pruebas automáticas | 117 pruebas en `tests/`, todas en verde y ninguna saltada (6 nov 2026) |
| Revisión de fuga | Subagente `auditor-de-fuga` en las etapas 3, 4, 5, 6, 7, 8 y 9 (`reports/auditoria_*.md`) |
| Revisión del grupo con el checklist | Etapas 1 a 5 el 5 nov 2026 (una pieza por integrante) y etapas 6 a 9 el 6 nov 2026 (revisión conjunta de `tuning.py`, `evaluation.py`, `schema.py`, notebook 08, `streamlit_app.py`, `predict.py`, `form.py` y notebook 09), sin problemas encontrados; detalle en `reports/revision_grupo.md` |

---

## Etapa 1 · Caso de negocio

- Ficha en `reports/00_caso.md`.
- **Objetivo:** `punt_global`, de 100 a 477 puntos (promedio 245,9, mediana 242).
- **Línea base:** siempre la mediana da MAE 42,8; siempre el promedio, 42,9; al azar, 58,9.
- **Metas acordadas:** MAE ≤ 38 (11 % mejor que la línea base) y ≤ 35 (18 % mejor), en validación agrupada por sede.
- **Condición de equidad:** el MAE del modelo debe ser menor que el de la línea base en cada segmento de estrato (con «Sin
  Estrato» y vacíos), zona y naturaleza del colegio. Se agrega porque un buen promedio puede esconder un grupo perjudicado.

## Etapa 2 · Análisis exploratorio (EDA)

Detalle en `reports/01_eda.md`. Once decisiones, aprobadas por el grupo el 31 oct 2026:

1. Eliminar los duplicados exactos: 72.383 filas, el 50 % del archivo.
2. Excluir 7 columnas con fuga: los 5 puntajes por área, `desemp_ingles` y `estu_estadoinvestigacion`.
3. Usar el identificador del estudiante solo para quitar duplicados; convertir la fecha de nacimiento en edad y eliminarla.
4. Marcar como vacía la edad menor de 13 (30 estudiantes), sin borrar la fila.
5. Imputar los vacíos como la categoría «sin respuesta». El vacío informa: un 10,1 % en las columnas de la familia, con ~18
   puntos menos.
6. Conservar «No sabe», «No Aplica» y «Sin Estrato» como categorías propias.
7. Convertir estrato, personas y cuartos del hogar a números ordenados.
8. Eliminar las 4 columnas con un solo valor.
9. Excluir los identificadores del colegio como predictores.
10. Partir y validar por sede.
11. Excluir el calendario «OTRO»: 235 estudiantes, el 0,3 %.

Decisiones posteriores del grupo:
- **«Sin Estrato»:** el estrato queda vacío (nunca 0) y la marca `sin_estrato` = 1.
- **Escala de educación de los padres** de 0 a 9.
- **Equidad:** se excluyen como predictores `estu_tipodocumento`, `estu_nacionalidad` y `estu_privado_libertad`, que
  funcionarían como indicadores de condición migratoria o son datos sensibles.

## Etapa 3 · Preprocesamiento y partición

- Código en `src/proyecto/data/`, con `cleaning.py`, `load.py` y `split.py`. Auditoría en `reports/auditoria_etapa3.md`.
- **Partición:** 20 % de prueba **por sede** con `GroupShuffleSplit` y semilla 42. Quedan 57.286 estudiantes y 1.155 sedes
  de entrenamiento, y 14.862 estudiantes y 289 sedes de prueba. Una prueba automática verifica que ninguna sede está en los
  dos lados.
- Los datos procesados (`data/processed/`) no se suben: se regeneran con el notebook 03.

## Etapa 4 · Variables

- Detalle en `reports/04_features.md`. Código en `src/proyecto/features/engineering.py` y `build_pipeline` de `train.py`.
- **Regla escrita antes de medir:** una idea se conserva solo si su mejora supera el ruido entre pliegues (mejora / ruido > 1).
- **Resultado:** ninguna de las 4 variables nuevas supera el ruido. Las 4 eran número de bienes, educación máxima de los
  padres, personas por cuarto y vivir en el municipio del colegio; sus valores de mejora / ruido van de −0,18 a 0,06.
- **Decisión:** las variables nuevas quedan apagadas. Referencia: MAE 33,56 ± 0,24.
- **Umbral de categorías poco frecuentes:** el 0,1 % mejoró 0,17 puntos (0,77 veces el ruido). Pasó como candidato a la
  etapa 6.
- **El modelo usa 21 columnas:** 5 numéricas, 14 categóricas y 2 códigos de municipio.

## Etapa 5 · Torneo de modelos

Detalle en `reports/05_torneo.md`. Comparación en los mismos 5 pliegues por sede:

| Modelo | MAE (± ruido) |
|---|---|
| HistGradientBoosting | 33,56 (± 0,24) |
| XGBoost | 33,66 (± 0,21) |
| Random Forest | 34,75 (± 0,30) |
| Ridge | 34,78 (± 0,21) |
| Línea base (mediana) | 42,83 (± 0,60) |

- **LightGBM se reemplazó** por HistGradientBoosting de scikit-learn, que usa la misma técnica. LightGBM no carga sin el
  Visual C++ Redistributable y el grupo no tiene permisos para instalarlo.
- **Finalistas:** HistGradientBoosting y XGBoost, empatados dentro del ruido (0,095 puntos de diferencia, 0,95 veces el
  ruido). El torneo descarta, no corona.

## Etapa 6 · Optimización con seguimiento

Detalle en `reports/06_optimizacion.md`. Guía en `especificaciones/06-optimizacion.md`. Spec Kit en
`specs/004-hyperparameter-tuning/`. Auditoría en `reports/auditoria_etapa6.md`.

**Qué se construyó**
- `src/proyecto/models/tuning.py`:
  - espacios de búsqueda de los dos finalistas;
  - búsqueda con Optuna que minimiza el MAE;
  - cada ensayo registrado como ejecución anidada en MLflow;
  - estudio que se reanuda si se corta;
  - reserva de sedes;
  - intervalos que remuestrean sedes completas.
- `tests/test_tuning.py`, con 14 pruebas. Incluye las que pidió la auditoría: los pliegues de la búsqueda son por sede y el
  umbral se ajusta dentro de cada pliegue. Se comprobó con una versión con fuga simulada que esa prueba la detecta.

**Decisiones del grupo (antes de ejecutar)**
- **Presupuesto:** 25 ensayos de HistGradientBoosting y 30 de XGBoost, con 3 pliegues por sede.
- **Entra en la búsqueda:** el umbral de poco frecuentes (1 % o 0,1 %) y la pérdida (cuadrática o absoluta).
- **Sedes reservadas:** el 25 % (289 sedes, 13.481 estudiantes) queda fuera de la búsqueda para la comprobación final.
- **Regla 1:** usar los parámetros optimizados solo si todo el intervalo de la mejora queda bajo cero.
- **Regla 2:** si los dos finalistas empatan, elegir HistGradientBoosting, que viene en scikit-learn y simplifica registro y
  despliegue.

**Resultados**

| Modelo | MAE partida → mejor (búsqueda, 3 pliegues) | Sedes reservadas: partida → optimizado | Diferencia [IC 95 %] |
|---|---|---|---|
| HistGradientBoosting | 33,787 → 33,401 | 34,041 → 33,675 | −0,366 [−0,640 ; −0,118] |
| XGBoost | 33,982 → 33,440 | 34,072 → 33,723 | −0,349 [−0,570 ; −0,131] |

- **Regla 1:** optimizados en los dos modelos.
- **Regla 2:** la diferencia HistGradientBoosting − XGBoost es −0,048, con intervalo [−0,222 ; +0,119]. Es un empate, así
  que se elige **HistGradientBoosting**.
- **Parámetros elegidos:**
  - umbral 0,1 %;
  - pérdida de error absoluto;
  - `learning_rate` 0,0301;
  - 587 iteraciones;
  - 16 hojas;
  - mínimo 82 estudiantes por hoja;
  - `l2_regularization` 0,3657;
  - `max_features` 0,6155.
- Las cifras de esta etapa no se comparan directamente con el 33,56 del torneo: usan otros pliegues y otros datos.

**Seguimiento y reproducibilidad**
- **Ejecución con MLflow local:** búsqueda de 27,2 min.
- **Ejecución con Databricks**, experimento `saber11-optimizacion`: 55 ensayos y 2 mediciones de partida. La búsqueda tardó
  31,1 min; el grupo aceptó los 32 min porque la diferencia es el registro por red.
- **Las dos ejecuciones dieron los mismos 55 ensayos, bit a bit:** misma semilla, mismos pliegues y modelos con semilla fija.

## Etapa 7 · Validación final e interpretación

Detalle en `reports/07_validacion.md`. Guía en `especificaciones/07-validacion.md`. Spec Kit en `specs/005-validation/`.
Auditoría en `reports/auditoria_etapa7.md`: sus 8 mejoras menores (H1 a H8) quedaron atendidas; las últimas, H7 y H8, el 6
nov 2026. H8 hace que `permutation_importance_table` permute solo las columnas del modelo, y no cambia la tabla de
importancia de la etapa 7, porque el notebook 07 ya le pasaba esas columnas.

**Qué se construyó**
- `src/proyecto/models/evaluation.py`:
  - segmentos de equidad (estrato con «Sin Estrato» y vacíos, zona, naturaleza, género);
  - tabla de equidad con intervalo por sede;
  - diferencia de métricas con intervalo por sede;
  - importancia por permutación.
- `tests/test_evaluation.py`, con 6 pruebas.

**Cómo se protegió la prueba**
1. Las decisiones se congelaron el 2026-11-05 a las 19:53:16, en `reports/07_decisiones_congeladas.json`. Fueron:
   - el modelo y sus parámetros;
   - la línea base;
   - las metas;
   - la regla de equidad, que el grupo aprobó con su clasificación: «cumple con ventaja clara» si el intervalo de la
     diferencia excluye el cero, y «cumple sin ventaja concluyente» si lo incluye.
2. **Ensayo general** del notebook con una «prueba falsa» sacada de `train.joblib` por sedes. No usó `test.joblib` y sus
   cifras no se usaron para nada.
3. **Apertura única** el 2026-11-05 a las 19:55:52 (`reports/prueba_abierta.txt`). Si se re-ejecuta el notebook, reutiliza
   los resultados guardados y no vuelve a evaluar. No se ajustó nada después de ver la prueba.

**Resultados en la prueba**: 14.862 estudiantes y 289 sedes nunca vistas. Intervalos del 95 % por sedes:

| Métrica | Modelo | Línea base (mediana del entrenamiento, 243) | Diferencia |
|---|---|---|---|
| MAE | **33,32** [32,39 ; 34,21] | 43,09 [41,38 ; 44,98] | **−9,77** [−11,78 ; −7,99] |
| RMSE | 41,46 [40,34 ; 42,50] | 51,97 [49,79 ; 54,37] | −10,51 [−12,74 ; −8,47] |
| R² | 0,363 [0,306 ; 0,414] | −0,001 | +0,364 [0,309 ; 0,421] |

- El modelo mejora a la línea base con confianza: 22,7 % menos error.
- Cumple la meta mínima (≤ 38) y la deseable (≤ 35), incluso con el límite superior del intervalo.
- Es coherente con la validación: 33,56 en el torneo y 33,675 en las sedes reservadas. No hay señal de que la validación
  fuera optimista.

**Equidad.** Los 14 de 14 segmentos cumplen, todos «con ventaja clara».

| Segmento | Estudiantes / sedes | MAE modelo | MAE línea base |
|---|---|---|---|
| Estrato 1 | 3.068 / 245 | 31,92 | 39,17 |
| Estrato 2 | 5.453 / 258 | 33,43 | 40,09 |
| Estrato 3 | 3.637 / 245 | 34,19 | 44,16 |
| Estrato 4 | 800 / 169 | 35,57 | 54,98 |
| Estrato 5 | 325 / 89 | **39,57** | 71,12 |
| Estrato 6 | 127 / 61 | 33,83 | 60,37 |
| Sin Estrato | 285 / 124 | 30,24 | 47,55 |
| Sin dato (vacío) | 1.167 / 197 | 31,12 | 45,14 |
| Rural / Urbano | 2.234 / 130 · 12.628 / 159 | 30,14 · 33,88 | 41,35 · 43,40 |
| No oficial / Oficial | 3.378 / 54 · 11.484 / 235 | 35,55 · 32,66 | 52,71 · 40,26 |
| Mujeres / Hombres | 8.297 / 279 · 6.565 / 271 | 31,40 · **35,74** | 42,06 · 44,39 |

«Cumple» quiere decir que el modelo se equivoca menos que predecir siempre la mediana, no que funcione igual de bien para
todos. Las brechas que se declaran como límite:
- el estrato 5 tiene un MAE por encima de 38;
- los hombres tienen 4,34 puntos más de error que las mujeres;
- los colegios no oficiales tienen más error que los oficiales.

**Qué pesa más en el modelo.** Se midió con importancia por permutación sobre la prueba: cuánto sube el MAE si se
desordena cada columna.
1. **Edad:** +2,48 puntos.
2. **Jornada del colegio:** +2,30 puntos.
3. Muy por detrás: naturaleza del colegio (+0,73), educación de la madre (+0,68), tener computador (+0,66), cuartos del
   hogar, educación del padre e internet (~0,5 cada una).

El estrato aparece en el puesto 12 porque comparte su información con computador, internet y educación de los padres.

Límites de esta medida:
- explica al modelo, no al mundo;
- no indica causas;
- no se usó para cambiar nada.

**Atributos sensibles declarados:** género (puesto 9), estrato, zona, municipios y edad.

## Etapa 8 · Registro del modelo, exportación y esquema

Detalle en `reports/08_registro.md` y `models/ficha_modelo.md`. Guía en `especificaciones/08-registro.md`. Spec Kit en
`specs/006-model-registry/`. Auditoría en `reports/auditoria_etapa8.md`.

**Antes de empezar: candado de la prueba (auditoría de la etapa 7).** El notebook 07 ahora:
- no reescribe las decisiones congeladas si falta su archivo;
- escribe la marca de apertura antes de evaluar;
- guarda huellas SHA-256 de la prueba, el modelo y los resultados (`reports/prueba_huellas.json`);
- carga el modelo evaluado en vez de reentrenarlo;
- comprueba el umbral del preprocesador.

Se volvió a ejecutar sin reevaluar, y los resultados de la etapa 7 quedaron idénticos byte a byte. La auditoría de la
etapa 8 agregó que se detenga también si falta el archivo de huellas.

**Auditoría:** `reports/auditoria_etapa8.md`. Sin fuga de información ni uso indebido de la prueba; 4 hallazgos (1 de
privacidad: un aviso de MLflow imprimió la ruta con el correo en el notebook 08, y se quitó antes de subirlo), todos
atendidos.

**Qué quedó registrado**

| Dato | Valor |
|---|---|
| Dónde | Databricks, Unity Catalog («databricks (token)»); experimento `saber11-modelo-final` |
| Nombre y versión | `workspace.default.saber11_puntaje_global`, **versión 1** |
| Alias | **`champion`** → versión 1 |
| Junto al modelo | Parámetros; métricas de la prueba con sus intervalos (MAE 33,316 [32,394 ; 34,207], RMSE 41,463, R² 0,363) y de la línea base; firma y ejemplo con **solo las 21 columnas** del modelo, tomados del entrenamiento; etiquetas de etapa, fecha y commit |
| Ida y vuelta | El modelo cargado por `@champion` predice **exactamente** igual que el original (500 filas del entrenamiento) |

**Exportación y esquema de entrada**
- **`models/model.joblib`:** exportado desde la versión `champion`. La app lo carga y no consulta Databricks.
- **`models/input_schema.json`:** calculado solo con el entrenamiento. Contiene:
  - las 21 columnas: 5 numéricas y 16 categóricas, con su tipo;
  - los valores válidos de las categóricas;
  - el rango observado y la mediana de las numéricas;
  - el rango **válido**: edad 13–80, estrato 1–6, marca «Sin Estrato» 0–1, personas 1–5, cuartos 1–6;
  - los **12 campos que admiten «sin respuesta»** (los que tenían vacíos en el entrenamiento); los otros 9 son
    obligatorios.
- Los dos archivos se suben al repositorio: ninguno está en `.gitignore`.

**¿El exportado es el evaluado?** Sí, y sin volver a predecir sobre la prueba:
1. La huella del modelo coincide con la del día de la apertura.
2. `model.joblib` predice exactamente igual que el modelo evaluado en las 57.286 filas del entrenamiento.
3. El MAE recalculado con las predicciones guardadas de la prueba es 33,316.

**Predicción que valida antes de responder** (`src/proyecto/inference/`):
- `predict_score` devuelve `puntaje_estimado`, sin redondear ni recortar.
- **Se niega a responder** si:
  - falta una columna;
  - un valor no es número o está fuera del rango válido;
  - un campo obligatorio viene vacío;
  - una categoría de lista cerrada no existe.
- Con municipios no vistos, solo advierte.
- Las funciones de clasificación de la plantilla se quitaron en la etapa 9.
- La mediana del esquema sale solo del entrenamiento y nunca se calcula al predecir (hallazgo 5 de la auditoría de la
  etapa 3, resuelto).

## Etapa 9 · Inferencia y app

Detalle en `reports/09_despliegue.md`. Guía en `especificaciones/09-app.md`. Spec Kit en `specs/007-app-inference/`.
Auditoría en `reports/auditoria_etapa9.md`.

**Predicción solo de regresión.** `src/proyecto/inference/predict.py` quedó con `load_model`, `validate_inputs` y
`predict_score`; las funciones de clasificación de la plantilla se quitaron, con sus pruebas.

**Del formulario al modelo** (`src/proyecto/inference/form.py`, nuevo). La persona elige textos en español y
`form_to_row` los traduce a las 21 columnas del modelo:
- personas («1 a 2» … «9 o más») y cuartos («Uno» … «Seis o más») a los códigos de la etapa 3;
- un solo campo de estrato: «1» a «6», «Sin estrato» (estrato vacío y `sin_estrato` = 1) o «Sin respuesta»;
- «Sin respuesta» solo en los 12 campos que admiten vacío; los otros 9 son obligatorios;
- si la edad no es un entero entre 13 y 80, o falta un dato obligatorio, no hay puntaje: un mensaje dice qué corregir.

**La app** (`app/streamlit_app.py`):
- título «Predictor de resultados Pruebas Saber 11 en Antioquia» y formulario en tres secciones: colegio, estudiante y
  hogar;
- municipios con nombre y código, por ejemplo «MEDELLÍN (5001)». Los nombres se agregaron al esquema
  (`municipality_names`, 139 municipios), calculados solo con el entrenamiento;
- resultado: el puntaje redondeado y «se equivoca en promedio 33 puntos; como referencia, entre X y Y». La app aclara
  que no es un intervalo de confianza;
- aviso de uso responsable siempre visible, con los límites de la ficha: estrato 5 (MAE 39,57) y la brecha por género
  (35,74 frente a 31,40);
- carga `models/model.joblib` desde el repositorio y no consulta Databricks.

**Notebook 09.** Cuatro perfiles inventados, sin Databricks y sin la prueba:

| Perfil (inventado) | Puntaje estimado | Referencia (± 33) |
|---|---|---|
| A · colegio oficial urbano en Medellín, estrato 2 | 250 | 217 a 283 |
| B · colegio no oficial bilingüe en Envigado, estrato 5 | 323 | 290 a 356 |
| C · colegio oficial rural en Turbo, estrato 1, sin computador ni internet | 212 | 179 a 245 |
| D · incompleto: «Sin estrato» y varios «Sin respuesta» (Rionegro) | 247 | 214 a 280 |

Un ejemplo con edad 12 y la jornada sin elegir se rechaza sin puntaje, con un mensaje que nombra los dos datos.

**Pruebas.** `tests/test_app.py` prueba el formulario y la app con AppTest:
- un perfil normal da un puntaje entero;
- «Sin respuesta» no rompe nada;
- una edad inválida o un dato obligatorio vacío muestran un mensaje y ningún puntaje;
- el aviso de uso responsable está visible;
- el código no menciona Databricks.

**Despliegue:** la app está publicada en Streamlit Community Cloud: https://predictorpruebasaber.streamlit.app (enlace agregado el 7 nov 2026 a
`README.md`, `reports/09_despliegue.md` y la presentación). `reports/09_despliegue.md` deja el plan B (app en local) y
los casos probados en local con sus resultados. **El 7 nov 2026 el grupo los repitió en el enlace público, en una
ventana privada:** perfil normal 250; edades 13 y 80 aceptadas; edad 81 rechazada con mensaje; todo «Sin respuesta» sin
errores; se ven el aviso de uso responsable y la atribución.

**Género:** se mantiene como entrada (decisión del grupo, 6 nov 2026); quitarlo exigiría reentrenar y volver a evaluar
con la prueba, que ya se abrió. Anotado en la ficha del modelo.

## Etapa 10 · Preparación del despliegue (sin desplegar)

Detalle en `reports/despliegue_preparacion.md`. Especificación en `specs/008-deploy-readiness/spec.md` (creada con
`/speckit-specify`). Revisión del código en `reports/revision_app.md`.

**El repositorio cumple la lista de la guía de Streamlit Community Cloud** (comprobado el 6 nov 2026):
- el repositorio es público;
- `requirements.txt` está en la raíz con todas las versiones fijadas, iguales a las del entrenamiento;
- `models/model.joblib` (1,17 MB) y `models/input_schema.json` están subidos y no ignorados;
- la app corre en local sin errores y arma sus rutas desde la ubicación del archivo;
- no consulta Databricks: al cargarla no se carga `mlflow` ni `databricks`;
- no hay `.env`, datos de estudiantes, correos, direcciones del espacio de trabajo ni tokens en el repositorio;
- Python 3.12 en el equipo; en la nube se elige en **Advanced settings** al crear la app.

**Revisión del código** (subagente `revisor-de-codigo-ia`): **aceptar con cambios.** Los cuatro hallazgos importantes
**se corrigieron** el 6 nov 2026, a pedido del grupo:
1. **H1:** si el modelo o el esquema no cargan, la app muestra un mensaje claro, sin rutas ni detalles técnicos, y se
   detiene.
2. **H2:** el aviso de uso responsable se muestra arriba, bajo el título, y se ve aunque el modelo no cargue.
3. **H3:** `schema.py` quedó solo para regresión (se quitó el código de clasificación de la plantilla).
4. **H4:** nuevo `app/requirements.txt` con solo las 6 librerías de la app (streamlit, pandas, numpy, scikit-learn, scipy,
   joblib), con las mismas versiones. Streamlit Community Cloud lo usa porque está junto al archivo principal; el de la raíz
   sigue completo. **Comprobado en un entorno limpio:** la app arranca y el perfil de prueba da 250, igual que antes.

De los 7 menores se aplicaron los que no cambian el comportamiento:
- H5: no duplicar `sys.path`;
- H6: la dependencia del modelo con `src/`, anotada en la ficha;
- H7: prueba anti-Databricks más firme;
- parte de H9: una sola constante para el MAE;
- parte de H10: un cambio de forma.

**H8 y H11 no se aplican (decisión del grupo, 7 nov 2026):** la app solo carga nuestro esquema de regresión y el
formulario usa un único campo para el estrato, así que esas situaciones no ocurren; aplicarlos cambiaría qué entradas se
rechazan. Detalle en `reports/revision_app.md`.

**Pruebas:**
- el subagente `escritor-de-pruebas` agregó 8 pruebas de inferencia;
- las correcciones agregaron 2 pruebas de la app y cambiaron 3 de clasificación por 3 de regresión.

Total: **115 pruebas, todas en verde**.

**Logo y atribución de los datos** (6 nov 2026, pedido del grupo):
- La barra lateral muestra el logo `app/assets/icfes_saber11.png`, pequeño (160 píxeles de ancho), y debajo: «Datos: ICFES
  (datos.gov.co, CC BY-SA 4.0). Esta herramienta no es oficial ni está avalada por el ICFES.»
- La ruta se arma desde la carpeta de la app (`Path(__file__).parent / "assets"`), así que funciona igual en local y en
  Streamlit Cloud.
- Si la imagen falta o está dañada, la app muestra solo el texto y sigue funcionando.
- Dos pruebas nuevas lo verifican; total **117 pruebas**. También se comprobó con el entorno mínimo de `app/requirements.txt`.
- ⚠ **Riesgo:** la licencia CC BY-SA 4.0 cubre los datos, no el logo, que es una marca del ICFES. Mostrarlo en una app
  pública puede sugerir una relación oficial aunque el texto la niegue. Si el grupo prefiere evitarlo, basta con borrar la
  imagen: la app queda solo con el texto de atribución.

---

## Uso de Databricks

**Qué se hizo**
- **Seguimiento de experimentos (etapa 6).** La búsqueda de hiperparámetros se registró con MLflow en Databricks, en el
  experimento `saber11-optimizacion`:
  - 55 ensayos: 25 de HistGradientBoosting y 30 de XGBoost;
  - la medición de partida de cada modelo, con sus parámetros del torneo y los mismos pliegues.
- **Registro del modelo (etapa 8).** El modelo final quedó en Unity Catalog como
  `workspace.default.saber11_puntaje_global`:
  - **versión 1**, con el alias **`champion`**;
  - experimento `saber11-modelo-final`.
- **Dónde corrió el cómputo.** El entrenamiento y la búsqueda corrieron en los equipos del grupo; Databricks guardó los
  registros (parámetros, métricas, modelos), no hizo los cálculos.
  - Una ejecución completa con MLflow local dio los mismos 55 ensayos, con los mismos parámetros y el mismo MAE, bit a bit.
  - El registro por red hizo que la búsqueda tardara 31,1 minutos, frente a 27,2 en local.

**Para qué sirvió**
- **Trazabilidad:** cada resultado de la optimización (etapa 6) y del modelo registrado (etapa 8) se puede rastrear
  hasta la ejecución que lo produjo. Las etapas anteriores quedaron en los notebooks y en `reports/`.
- **Comparación de ensayos:** los 55 ensayos y las mediciones de partida quedan uno junto a otro, con sus parámetros y su
  MAE.
- **Registro compartido:** todo el grupo ve los mismos experimentos y el mismo modelo, sin pasarse archivos.
- **Versionado del modelo:** el alias `champion` dice qué versión está vigente. Si aparece una mejor, se mueve el alias.
- **Linaje:** junto al modelo registrado quedaron:
  - sus parámetros;
  - las métricas de la prueba con sus intervalos;
  - la firma y el ejemplo de entrada (solo las 21 columnas, tomadas del entrenamiento);
  - el commit de origen.

**Por qué la app no depende de Databricks**
- La app carga `models/model.joblib` desde el repositorio. Ese archivo se exportó desde la versión `champion`, y se
  comprobó que predice exactamente igual que el modelo evaluado.
- No hay credenciales en la nube: la app no necesita token ni conexión a Databricks. Una prueba automática verifica que
  su código no menciona `mlflow`, `databricks` ni `token`.
- No depende de la cuota ni de la disponibilidad de otra plataforma: si Databricks no está disponible, la app sigue
  funcionando.

Detalle en `reports/06_optimizacion.md` y `reports/08_registro.md`. La ruta completa de los experimentos no se publica
porque incluye el correo de un integrante.

---

## Archivos principales

| Qué | Dónde |
|---|---|
| Caso, EDA, variables, torneo, optimización, validación | `reports/00_caso.md`, `01_eda.md`, `04_features.md`, `05_torneo.md`, `06_optimizacion.md`, `07_validacion.md` |
| Decisiones del grupo con fecha y motivo | `especificacion-proyecto.md`, sección 7 |
| Especificaciones por etapa | `especificaciones/` · `specs/001` a `specs/008` |
| Código reutilizable | `src/proyecto/data/`, `features/`, `models/` (`train.py`, `tuning.py`, `evaluation.py`), `tracking/`, `inference/` |
| Pruebas (117) | `tests/` (datos inventados compartidos en `tests/conftest.py`) |
| Notebooks (solo orquestan) | `notebooks/01` a `09` |
| Auditorías de fuga | `reports/auditoria_etapa3.md`, `auditoria_etapa4.md`, `auditoria_train.md`, `auditoria_etapa6.md`, `auditoria_etapa7.md`, `auditoria_etapa8.md`, `auditoria_etapa9.md` |
| Modelo para la app | `models/model.joblib` (exportado desde `champion`), `models/input_schema.json`, `models/ficha_modelo.md` |
| App e inferencia | `app/streamlit_app.py`, `app/requirements.txt` (librerías de la app), `app/assets/icfes_saber11.png` (logo), `src/proyecto/inference/` (`predict.py`, `form.py`, `schema.py`), `reports/09_despliegue.md` |
| Preparación del despliegue | `reports/despliegue_preparacion.md`, `reports/revision_app.md` |
| Informe técnico | `reports/informe_tecnico.md` (ensamblado el 7 nov 2026 con los informes 00 a 09; asignatura «Laboratorio de análisis avanzado: casos prácticos», Especialización en Analítica de Datos, UNAULA; incluye la nota de que el AUC no aplica porque es regresión) |
| Presentación ejecutiva | `presentacion/ejecutiva.md` (5 diapositivas; pie de página «Laboratorio de análisis avanzado: casos prácticos · Especialización en Analítica de Datos · UNAULA · Grupo 10»; enlace de la app en la diapositiva 4) |
| Registro | `reports/08_registro.md`, `reports/08_registro.json`, `reports/prueba_huellas.json` |
| Resultados en archivos | `reports/06_best_params.json`, `06_comprobacion.csv`, `07_metricas_test.json`, `07_equidad.csv`, `07_importancia.csv` |
| Constancia de la prueba | `reports/07_decisiones_congeladas.json`, `reports/prueba_abierta.txt` |

**Cómo comprobar:** desde la raíz, `python -m pytest -q` debe terminar con `117 passed`, y `streamlit run app/streamlit_app.py`
abre la app en local.

---

## Pendientes

1. **Exposición:** ensayo cronometrado, capturas de pantalla para el plan B y abrir la app 10 minutos antes.
2. **Género como entrada:** se mantiene (6 nov 2026). Cambiarlo exigiría un ciclo nuevo de entrenamiento y validación
   por sede, porque la prueba ya se usó.
3. **Informe técnico** (`reports/informe_tecnico.md`, hito H4, entrega el domingo 15 nov): ensamblado el 7 nov 2026.
   Su lista de comprobación está completa: un compañero siguió el anexo de reproducción desde cero en un PC limpio
   (confirmado por el grupo el 7 nov 2026). La diapositiva 3 de la presentación se corrigió el 7 nov 2026: la línea base es 243, como
   en la prueba.

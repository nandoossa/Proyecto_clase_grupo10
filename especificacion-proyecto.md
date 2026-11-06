# Especificación del proyecto

> Plantilla. Complétenla en el grupo y manténganla actualizada. Claude la lee antes de generar
> código: lo que escriban aquí manda sobre cualquier otra suposición.

## 1. Grupo

| Integrante | Rol (datos / modelado / app / negocio) |
|---|---|
| Jennifer Alejandra López Sánchez | Analista de datos |
| Jaime Andrés Úsuga Jiménez | Analista de datos |
| Raúl Fernando Ossa Ramírez | Analista de datos |
| David Andrés Paniagua Gutiérrez | Analista de datos |
| Sebastián Orozco Giraldo | Analista de datos |

Nombre de la "startup": Predictor de resultados Pruebas Saber 11 en Antioquia   Repositorio (público): https://github.com/nandoossa/Proyecto_clase_grupo10

## 2. Caso de negocio

- **Pregunta de negocio** (una frase, que alguien sin formación técnica entienda): ¿Qué puntaje global en Saber 11 puede
  esperar un estudiante de Antioquia según las características de su colegio, su perfil y su familia, y qué factores
  influyen más en ese puntaje?
- **¿Quién usará el resultado y qué decisión tomará con él?** Una app web donde se ingresa el perfil de un estudiante y se
  obtiene su puntaje estimado. La usan la Secretaría de Educación (a qué colegios o municipios dirigir programas de
  refuerzo antes del examen), rectores y docentes (qué estudiantes de grado 11 necesitan preparación adicional) y
  estudiantes y familias (a qué universidad o beca aspirar y si conviene invertir en preparación). El modelo orienta; la
  decisión final la toma una persona.
- **¿Qué cuesta equivocarse?** (cuál error es peor y por qué): los dos errores cuestan lo mismo (1 a 1). Sobreestimar
  puede dejar sin apoyo a quien lo necesitaba; subestimar dirige recursos a quien no los necesitaba o desanima al
  estudiante. Mismo peso porque la app la usan perfiles distintos y ningún error es claramente más grave para todos; el
  costo crece en proporción a los puntos de error.

## 3. Datos

- **Fuente** (enlace de Kaggle, empresa, etc.): datos.gov.co — Resultados Saber 11 (recurso `kgxf-xxbe`),
  filtrado a periodo 20224 y departamento ANTIOQUIA. Se descarga a `data/raw/saber11_antioquia_2022.csv` con:
  `https://www.datos.gov.co/resource/kgxf-xxbe.csv?$where=periodo=%2720224%27%20AND%20cole_depto_ubicacion=%27ANTIOQUIA%27&$order=estu_consecutivo&$limit=200000`
- **Filas / columnas:** 144.766 filas descargadas = 72.383 estudiantes (cada fila viene duplicada en la fuente) / 51
- **Variable objetivo** (columna que queremos predecir o describir): `punt_global` (100 a 477 puntos). Excluidas por
  fuga: `punt_matematicas`, `punt_lectura_critica`, `punt_sociales_ciudadanas`, `punt_c_naturales`, `punt_ingles`,
  `desemp_ingles` y `estu_estadoinvestigacion`.
- **Tipo de problema:** ☐ clasificación  ☒ regresión  ☐ clusterización
- **¿Una misma entidad (cliente, paciente, empresa) aparece en varias filas?** ☐ no  ☒ sí → la partición
  será por: sede del colegio (`cole_cod_dane_sede`), con `GroupShuffleSplit` y `GroupKFold`. Motivo: cada estudiante
  aparece una vez tras quitar duplicados, pero la sede sola explica el 36 % de la variación del puntaje y la app recibirá
  colegios que el modelo no vio.
- **Datos personales o confidenciales presentes:** ☐ no  ☒ sí → se eliminarán/anonimizarán así: `estu_consecutivo` se
  usa solo para controlar duplicados (nunca como variable ni se muestra); `estu_fechanacimiento` se convierte en edad
  aproximada y se elimina; ningún identificador del estudiante o del colegio entra como predictor.
- **Licencia o permiso de uso de los datos:** CC BY-SA 4.0 (Creative Commons Atribución-CompartirIgual 4.0
  Internacional), según los metadatos del recurso `kgxf-xxbe` en datos.gov.co (consultado el 31 oct 2026). Crédito al
  ICFES; las versiones modificadas de los datos que se publiquen deben usar la misma licencia.

## 4. Métrica

- **Métrica principal:** MAE (error absoluto medio, en puntos).   **Por qué esa y no otra:** los dos errores cuestan lo
  mismo y el costo crece en proporción a los puntos de error, que es lo que mide el MAE; se explica sin formación técnica
  («se equivoca en promedio ±N puntos»); la exactitud no aplica porque es regresión. Meta mínima: MAE ≤ 38 en validación
  agrupada por sede (11 % mejor que la línea base de 42,8); meta deseable: MAE ≤ 35; condición de equidad: en cada
  segmento de estrato, zona y naturaleza del colegio, el MAE del modelo debe ser menor que el de la línea base (tabla en
  `reports/00_caso.md`).
- **Métricas secundarias:** RMSE (revela errores muy grandes que el MAE suaviza) y R² (qué parte de la variación explica
  el modelo).
- **Línea base** (qué resultado obtiene una regla simple o un modelo trivial): predecir siempre la mediana (242 puntos)
  da un MAE de 42,8 (siempre el promedio: 42,9; al azar: 58,9). La línea base por segmento está en `reports/00_caso.md`.

## 5. Riesgos

- Fuga de información posible: las 7 columnas excluidas (`punt_matematicas`, `punt_lectura_critica`,
  `punt_sociales_ciudadanas`, `punt_c_naturales`, `punt_ingles`, `desemp_ingles` y `estu_estadoinvestigacion`) y los
  duplicados exactos (72.383 filas), que se eliminan antes de partir. Los identificadores del colegio quedan fuera de los
  predictores (`cole_cod_dane_sede` se usa solo para agrupar).
- Sesgos o equidad: estrato, zona, naturaleza del colegio e internet se relacionan con el puntaje (estrato 1 ~231 vs.
  estrato 5 ~281). Se exige la condición de equidad por segmento de estrato, zona y naturaleza (sección 4) y se revisa en
  la validación.
- Datos faltantes o de mala calidad: duplicados exactos (50 % del archivo); vacíos no aleatorios en `fami_` (10,1 % de
  los estudiantes, con ~18 puntos menos de promedio); `cole_bilingue` con 16,4 % de vacíos; centinelas «No sabe»,
  «No Aplica» y «Sin Estrato»; 30 edades menores de 13 años; 4 columnas con un solo valor; calendario «OTRO»
  (235 estudiantes, 0,3 %) excluido.
- Límites de lo que el modelo puede decir: aplica a estudiantes de calendario A en Antioquia, periodo 20224 (2022). El
  puntaje estimado orienta; no se usa para excluir ni etiquetar a nadie. La edad es aproximada (año de la prueba − año de
  nacimiento).

## 6. Entregables y fechas

| Hito | Contenido | Fecha |
|---|---|---|
| H1 | Ficha aprobada, EDA y preprocesamiento reproducible | Cierre de la clase 2 (vie 30 oct) |
| H2 | Torneo, optimización con tracking, modelo registrado, repo modular, app local | Cierre de la clase 4 (jue 5 nov) |
| H3 | App desplegada y presentación (≤ 5 diapositivas) | Clase 5 (vie 6 nov) |
| H4 | Informe técnico final (hasta 8 días tras la última clase) | Domingo 15 nov |

## 7. Decisiones tomadas (agréguenlas a medida que avancen)

| Fecha | Decisión | Motivo |
|---|---|---|
| 30 oct 2026 | EDA 1: eliminar duplicados exactos al cargar (72.383 filas, 50 % del archivo). Propuesta en el EDA, aprobada por el grupo el 31 oct 2026 | Un mismo estudiante en entrenamiento y prueba haría que la métrica saliera optimista |
| 30 oct 2026 | EDA 2: excluir las 7 columnas con fuga (5 puntajes por área, `desemp_ingles`, `estu_estadoinvestigacion`). Propuesta en el EDA, aprobada por el grupo el 31 oct 2026 | Son la respuesta o información posterior al examen: fuga |
| 30 oct 2026 | EDA 3: usar `estu_consecutivo` solo para controlar duplicados (nunca como variable); convertir la fecha de nacimiento en edad y eliminarla. Propuesta en el EDA, aprobada por el grupo el 31 oct 2026 | No exponer datos personales; la edad conserva la información útil |
| 30 oct 2026 | EDA 4: edad < 13 → vacío, sin borrar la fila (30 estudiantes). Propuesta en el EDA, aprobada por el grupo el 31 oct 2026 | Es imposible presentar Saber 11 a esa edad; borrar filas perdería el resto de su información |
| 30 oct 2026 | EDA 5: imputar vacíos como categoría propia «sin respuesta» dentro del `Pipeline`. Propuesta en el EDA, aprobada por el grupo el 31 oct 2026 | El vacío es información (10,1 % en `fami_` con ~18 puntos menos; `cole_bilingue` 16,4 % con 16 puntos menos): imputar con la moda la borraría |
| 30 oct 2026 | EDA 6: mantener «No sabe», «No Aplica» y «Sin Estrato» como categorías propias. Propuesta en el EDA, aprobada por el grupo el 31 oct 2026 | Tienen puntajes distintos al resto: llevan información |
| 30 oct 2026 | EDA 7: convertir estrato, personas y cuartos del hogar a números ordenados. Propuesta en el EDA, aprobada por el grupo el 31 oct 2026 | Conservar el orden ayuda al modelo y simplifica la app |
| 30 oct 2026 | EDA 8: eliminar las 4 columnas con un solo valor. Propuesta en el EDA, aprobada por el grupo el 31 oct 2026 | No aportan información |
| 30 oct 2026 | EDA 9: excluir como predictores los identificadores del colegio; `cole_cod_dane_sede` solo para agrupar. Propuesta en el EDA, aprobada por el grupo el 31 oct 2026 | El modelo memorizaría el promedio de cada colegio y en prueba aparecerían colegios nunca vistos; los atributos del colegio sí los puede ingresar el usuario de la app |
| 30 oct 2026 | EDA 10: partir y validar por sede (`cole_cod_dane_sede`, `GroupShuffleSplit` / `GroupKFold`). Propuesta por el grupo, aprobada por el grupo el 31 oct 2026 | La sede explica el 36 % de la variación; mide el error con colegios no vistos, como en la app |
| 30 oct 2026 | EDA 11: excluir calendario «OTRO» (235 estudiantes, 0,3 %); el modelo aplica a calendario A. Propuesta por el grupo, aprobada por el grupo el 31 oct 2026 | Muy pocos casos para aprender algo confiable; simplifica el modelo y el formulario de la app |
| 31 oct 2026 | Meta de éxito: MAE ≤ 38 (mínima) y ≤ 35 (deseable) en validación agrupada por sede | Mejorar claramente la línea base de 42,8 (11 % y 18 %), medida con colegios no vistos |
| 31 oct 2026 | Condición de equidad: MAE del modelo menor que el de la línea base en cada segmento de estrato, zona y naturaleza del colegio | Un MAE promedio bueno puede esconder un grupo en el que el modelo se equivoca más que no usar modelo |
| 31 oct 2026 | Licencia de los datos: CC BY-SA 4.0, verificada en los metadatos de datos.gov.co | Cumplir las condiciones de uso: crédito al ICFES y misma licencia para datos modificados que se publiquen |
| 31 oct 2026 | «Sin Estrato» (opción A): en `fami_estratovivienda` queda vacío, nunca 0, y `sin_estrato` = 1; los vacíos reales quedan vacíos con `sin_estrato` = 0. Aprobada por el grupo | Resuelve el choque entre las decisiones 6 y 7 del EDA: un 0 inventaría un estrato, y la marca aparte conserva la información de «Sin Estrato» |
| 31 oct 2026 | Escala de educación de los padres (0 Ninguno … 9 Postgrado; técnica o tecnológica completa por debajo de profesional incompleta); «No sabe» y «No Aplica» fuera de la escala, como categorías propias. Aprobada por el grupo | Permite calcular el nivel educativo más alto del hogar sin perder los centinelas (decisión 6 del EDA) |
| 31 oct 2026 | `estu_tipodocumento` se excluye como predictor. Aprobada por el grupo | Su información ya está en la edad, y los documentos de extranjeros funcionarían como indicador de condición migratoria, lo que va contra la condición de equidad |
| 31 oct 2026 | `estu_nacionalidad` y `estu_privado_libertad` se excluyen como predictores. Aprobada por el grupo | La nacionalidad es indicador de condición migratoria y estar privado de la libertad es un dato sensible (99,8 % responde «N»); mismo criterio de equidad que `estu_tipodocumento` |
| 31 oct 2026 | Etapa 3: prueba del 20 %, partida por sede con `GroupShuffleSplit`, semilla 42. Aprobada por el grupo | Medir el error con colegios que el modelo no vio (decisión 10 del EDA) |
| 31 oct 2026 | Edad: en la etapa 3 solo se marcan como vacías las menores de 13; la imputación (mediana + indicador) va dentro del `Pipeline` en la etapa 4. Aprobada por el grupo | Imputar fuera del `Pipeline` usaría información de la prueba; el indicador conserva que el dato era imposible |
| 31 oct 2026 | Torneo: LightGBM se reemplaza por `HistGradientBoostingRegressor` de scikit-learn (parámetros equivalentes: `max_iter=300`, `learning_rate=0.05`, `max_leaf_nodes=31`); XGBoost se mantiene. Aprobada por el grupo | LightGBM no carga sin el Visual C++ Redistributable y el grupo no tiene permisos para instalarlo; HistGradientBoosting usa la misma técnica que LightGBM (boosting con histogramas), no requiere instalar nada adicional y funciona en el equipo de todos los integrantes, lo que cuida la reproducibilidad |
| 31 oct 2026 | Municipios: el notebook 04 prueba otros umbrales; si prueba `TargetEncoder`, dentro del `Pipeline` y comparado solo con validación agrupada por sede. Aprobada por el grupo | La validación cruzada interna de `TargetEncoder` no respeta la agrupación por sede |
| 31 oct 2026 | Etapa 4: las 4 variables nuevas (`n_bienes_hogar`, `educacion_max_padres`, `personas_por_cuarto`, `vive_en_mcpio_colegio`) quedan apagadas (`use_engineered=False`); el umbral de poco frecuentes se mantiene en 1 %, y el 0,1 % pasa como candidato a la etapa 6. Aprobada por el grupo | Ninguna supera el ruido entre pliegues (regla: mejora / ruido > 1). Referencia: MAE 33,56 ± 0,24 con HistGradientBoosting y 5 pliegues por sede; mejora / ruido de las variables entre −0,18 y 0,06 (las 4 juntas −0,06). El umbral 0,1 % mejora 0,17 puntos (mejora / ruido 0,77) y el 0,5 % 0,06 (0,26). Detalle en `reports/04_features.md` |
| 5 nov 2026 | Etapa 6: modelo elegido HistGradientBoosting con parámetros optimizados (`min_frequency` 0,1 %, pérdida de error absoluto, `learning_rate` 0,0301, `max_iter` 587, `max_leaf_nodes` 16, `min_samples_leaf` 82, `l2_regularization` 0,3657, `max_features` 0,6155). Reglas aprobadas por el grupo antes de ejecutar | Regla 1: en las 289 sedes reservadas el optimizado mejora a la partida en −0,366 puntos de MAE, IC 95 % por sedes [−0,640 ; −0,118] (XGBoost: −0,349, [−0,570 ; −0,131]). Regla 2: HGB − XGBoost = −0,048, IC [−0,222 ; +0,119], empate → HGB (viene en scikit-learn, simplifica registro y despliegue). 25 + 30 ensayos registrados en Databricks. Detalle en `reports/06_optimizacion.md` |
| 5 nov 2026 | Etapa 7: prueba abierta una sola vez (19:55:52, decisiones congeladas a las 19:53:16). MAE 33,32 [32,39 ; 34,21] frente a 43,09 de la línea base (diferencia −9,77, IC [−11,78 ; −7,99]); cumple las metas de 38 y 35 incluso con el límite superior del IC; equidad: 14 de 14 segmentos cumplen con ventaja clara. Nada se ajustó después de ver la prueba | Medición final con 289 sedes nunca vistas. Límites declarados: MAE 39,57 en estrato 5 (sobre 38), brecha de 4,34 puntos entre hombres (35,74) y mujeres (31,40), R² 0,363. Detalle en `reports/07_validacion.md` |
| 5 nov 2026 | Etapa 8: modelo registrado en Databricks (Unity Catalog) como `workspace.default.saber11_puntaje_global` versión 1, alias `champion`; exportado a `models/model.joblib` y esquema `models/input_schema.json` (edad 13–80; vacíos aceptados solo en los 12 campos que los tenían; categorías nuevas rechazadas salvo municipios). Decisiones del grupo del 5 nov 2026 | Ida y vuelta exacta; el exportado predice igual que el evaluado en las 57.286 filas del entrenamiento y el MAE recalculado con las predicciones guardadas es 33,316, sin volver a predecir sobre la prueba. Detalle en `reports/08_registro.md` |
| 6 nov 2026 | Etapa 9: `predict.py` queda solo con la regresión (`predict_score`); se quitan las funciones de clasificación de la plantilla. El formulario se traduce a las 21 columnas en `src/proyecto/inference/form.py`. Aprobada por el grupo | La plantilla era de clasificación; la traducción vive en `src/` para que la usen la app y el notebook 09 y tenga pruebas |
| 6 nov 2026 | Etapa 9 · app: edad como número entero sin mínimo ni máximo (fuera de 13–80 → mensaje de corrección); municipios con nombre y código (`municipality_names` en el esquema, calculado con el entrenamiento); resultado redondeado con «se equivoca en promedio 33 puntos; como referencia, entre X y Y», aclarando que no es un intervalo de confianza. Aprobada por el grupo | Que quien usa la app vea qué corregir, reconozca su municipio y entienda el error típico (MAE 33,32 en la prueba) sin confundirlo con un intervalo |
| 6 nov 2026 | Etapa 9: el género se mantiene como entrada del modelo. Aprobada por el grupo | Quitarlo exigiría reentrenar y volver a evaluar con la prueba, que ya se abrió; la brecha de error (hombres 35,74 frente a mujeres 31,40) se muestra en el aviso de uso responsable y en la ficha |
| 6 nov 2026 | Constitución del proyecto ratificada, versión 1.0.0 (`.specify/memory/constitution.md`): se conservan los principios I a VII, con la unidad de análisis (un estudiante) y la sede como entidad que se repite, y se agrega el **principio VIII**: el modelo orienta, no excluye ni etiqueta a ningún estudiante, y su MAE en cada segmento de estrato, zona, naturaleza del colegio y género debe ser menor que el de la línea base. Aprobada por el grupo | Dejar por escrito, como regla que prevalece sobre las demás prácticas, el uso responsable y la condición de equidad; el principio VIII agrega el género a los segmentos de la condición de equidad del 31 oct 2026 |

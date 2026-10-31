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
- **Línea base** (qué resultado obtiene una regla simple o un modelo trivial):

## 5. Riesgos

- Fuga de información posible:
- Sesgos o equidad:
- Datos faltantes o de mala calidad:
- Límites de lo que el modelo puede decir:

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
| | | |

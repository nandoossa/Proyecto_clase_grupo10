# Predictor de resultados Pruebas Saber 11 en Antioquia — Constitución

## Principios

### I. Los datos originales no se tocan
`data/raw/` MUST NOT modificarse. Toda limpieza se hace en código (`src/proyecto/data/`) y se guarda en
`data/processed/`, que se regenera desde cero con el notebook de preprocesamiento. *Razón:* sin el original no hay
reproducibilidad.

### II. Se parte por la unidad de análisis
La unidad de análisis de este proyecto es **un estudiante que presentó Saber 11 (una fila, tras quitar los duplicados
exactos)** y la entidad que se repite es **la sede del colegio (`cole_cod_dane_sede`)**. Como una sede aparece en varias
filas, la partición y la validación cruzada MUST hacerse por grupo (`GroupShuffleSplit`, `GroupKFold`,
`StratifiedGroupKFold`), nunca por fila. Una prueba automática MUST verificar que ninguna sede cae en dos particiones.
*Razón:* la sede sola explica el 36 % de la variación del puntaje; partir por fila filtra información e infla la
métrica, y la app recibirá colegios que el modelo no vio.

### III. La prueba se abre una sola vez
El conjunto de prueba MUST NOT usarse para elegir variables, modelo, umbral ni hiperparámetros. Se abre una vez, en la
etapa de validación. Todo preprocesamiento que aprenda de los datos (medias, categorías, escalado) MUST ir dentro de un
`Pipeline` ajustado solo con entrenamiento. *Razón:* es la única medida honesta de cómo se comportará en producción.

### IV. Cada decisión de datos se escribe con su motivo
Cada decisión (qué se limpia, qué se descarta, qué se repara) MUST quedar en `reports/` con la cifra que la respalda y
su motivo, y MUST tener una función en `src/` con al menos una prueba en `tests/`. *Razón:* otra persona debe poder
discutirla sin leer el código.

### V. Nada sensible sale del equipo
`.env`, tokens y datos personales MUST NOT subirse a GitHub (el repositorio es público). Las columnas con datos personales
se eliminan al cargar, antes de cualquier análisis que las imprima. *Razón:* privacidad y seguridad de las cuentas.

### VI. El código es nuestro: lo entendemos
Cada integrante MUST poder explicar el código que generó la IA. Antes de aceptarlo se revisa con
`material-del-curso/kit/checklist-revision-ia.md`. La lógica reutilizable vive en `src/`; los notebooks solo orquestan.
Textos y comentarios en español; nombres de código en inglés. *Razón:* la autoría individual es parte de la evaluación.

### VII. Nunca se inventan datos ni resultados
Ni la IA ni el grupo MUST fabricar cifras, columnas ni métricas. Lo que no se pudo medir se dice. *Razón:* un número
inventado en el informe invalida todo lo demás.

### VIII. El modelo orienta; no excluye ni etiqueta
El puntaje estimado MUST usarse solo para orientar (por ejemplo, a quién ofrecer refuerzos antes del examen) y MUST NOT
usarse para excluir, clasificar ni etiquetar a ningún estudiante o colegio. La app y la ficha del modelo MUST mostrar este
aviso junto con los límites conocidos. El MAE del modelo MUST ser menor que el de la línea base en cada segmento de
**estrato, zona, naturaleza del colegio y género**; se comprueba con validación, y la medición final, una sola vez, con
la prueba. Un segmento que no cumpla MUST declararse en `reports/` y en la ficha antes de usar el modelo. *Razón:* un buen
MAE promedio puede esconder un grupo en el que el modelo se equivoca más que no usar modelo, y una estimación con ±33
puntos de error típico no basta para decidir sobre una persona.

## Restricciones del proyecto

- **Caso:** estimar el puntaje global de Saber 11 (`punt_global`) de un estudiante de Antioquia según su colegio, su
  perfil y su familia, para orientar refuerzos antes del examen · **Métrica principal:** MAE en puntos, porque los dos
  errores (sobreestimar y subestimar) cuestan lo mismo y el costo crece con los puntos de error; meta ≤ 38 (mínima) y
  ≤ 35 (deseable), con validación agrupada por sede (`cole_cod_dane_sede`) · **Tipo de problema:** regresión.
- **Entorno:** Python 3.12; dependencias fijadas en `requirements.txt`. Paquete del proyecto: `proyecto` (`src/proyecto/`).
- **Seguimiento de experimentos:** MLflow en Databricks (o local si no hay conexión); la app **no** consulta Databricks.
- **App:** Streamlit, cargando `models/model.joblib` desde el repositorio.

## Flujo de trabajo

- Cada etapa sigue **especificación → plan → tareas → implementación** (`/speckit-specify`, `/speckit-plan`,
  `/speckit-tasks`, `/speckit-implement`). Los artefactos viven en `specs/`.
- Las guías de etapa de `especificaciones/` se llenan **antes** de pedir una especificación a Spec Kit: son su entrada.
- Los **subagentes** de `.claude/agents/` se usan para revisar (fuga, pruebas, código de la IA) antes de dar una etapa por
  terminada.
- Cada hito MUST tener criterios de aceptación verificables (`especificaciones/`, sección de cierre).

## Gobierno

Esta constitución prevalece sobre otras prácticas del proyecto. Una enmienda se hace con `/speckit-constitution`, se
justifica y se anota en la sección 7 de `especificacion-proyecto.md`. La versión sigue el versionado semántico: MAJOR si
se quita o redefine un principio, MINOR si se agrega un principio o se amplía una guía, PATCH si solo se aclara la
redacción. El cumplimiento se revisa en el «Constitution Check» de cada `plan.md` y en las auditorías de `reports/`. El
instructor puede pedir aclaraciones sobre cualquier principio en los puntos de control.

**Versión**: 1.0.0 | **Ratificada**: 2026-11-06 | **Última enmienda**: 2026-11-06

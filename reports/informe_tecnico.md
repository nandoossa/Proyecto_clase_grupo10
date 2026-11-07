# Informe técnico — Predictor de resultados Pruebas Saber 11 en Antioquia

**Asignatura:** Laboratorio de análisis avanzado: casos prácticos · **Programa:** Especialización en Analítica de Datos ·
**Universidad:** UNAULA (Universidad Autónoma Latinoamericana) · **Grupo 10**

**Grupo:** Jennifer Alejandra López Sánchez, Jaime Andrés Úsuga Jiménez, Raúl Fernando Ossa Ramírez, David Andrés Paniagua
Gutiérrez y Sebastián Orozco Giraldo (todos con rol de analista de datos) · **Repositorio:**
https://github.com/nandoossa/Proyecto_clase_grupo10 · **App:** https://predictorpruebasaber.streamlit.app

> Este informe ensambla los informes de `reports/` (00 a 09). Todas las cifras salen de esos informes; ninguna se calculó
> para este documento. **Regla:** cada decisión va con su motivo.

## Resumen ejecutivo

Hoy el puntaje de Saber 11 solo se conoce después del examen, cuando ya no hay tiempo de actuar. Construimos un modelo
que **estima el puntaje global** de un estudiante de Antioquia a partir de datos de su colegio, su perfil y su familia,
para **orientar** a tiempo a quién ofrecer refuerzo. Medido una sola vez con **289 sedes que el modelo nunca vio**, se
equivoca en promedio **33,3 puntos** por estudiante (MAE 33,32, intervalo del 95 % [32,39 ; 34,21]), **9,8 puntos menos**
que no usar modelo (22,7 %), y cumple las metas mínima (≤ 38) y deseable (≤ 35). Mejora a la línea base en los 14
segmentos de estrato, zona, naturaleza del colegio y género. **Principal límite:** explica el 36 % de la variación del
puntaje (R² 0,363) y su error es mayor en estrato 5 (39,57) y en hombres (35,74 frente a 31,40 en mujeres); por eso
**orienta, no excluye**. La app está publicada en https://predictorpruebasaber.streamlit.app.

> **Nota sobre las métricas.** El **AUC no aplica**: es un problema de **regresión** (se estima un número, el puntaje), no
> de clasificación, así que no hay probabilidades ni clases que ordenar. Por la misma razón no hay calibración, umbral,
> matriz de costos, recall por clase ni F1. Se usan **MAE** (métrica principal, en puntos), **RMSE** (castiga los errores
> grandes) y **R²** (qué parte de la variación explica el modelo).

## 1. Caso de negocio

> Fuente: `reports/00_caso.md` y `especificacion-proyecto.md`.

- **Quién decide y qué decide:**
  - la **Secretaría de Educación**, a qué colegios o municipios dirigir programas de refuerzo;
  - **rectores y docentes**, qué estudiantes de grado 11 necesitan preparación adicional;
  - **estudiantes y familias**, a qué universidad o beca aspirar y si conviene invertir en preparación.

  El modelo orienta; la decisión la toma una persona.
- **Con qué información:** datos del colegio, del estudiante y de su familia que se conocen **antes** del examen.
- **Qué cuesta equivocarse:** lo mismo en las dos direcciones (1 a 1). Sobreestimar puede dejar sin apoyo a quien lo
  necesitaba; subestimar dirige recursos a quien no los necesitaba o desanima al estudiante. **Motivo del peso igual:** la
  app la usan perfiles distintos y ningún error es claramente más grave para todos; el costo crece con los puntos de error.
- **Métrica principal: MAE**, en puntos. **Motivo:** mide justo eso (el costo proporcional a los puntos de error, igual
  hacia arriba y hacia abajo) y se explica sin formación técnica: «se equivoca en promedio ±N puntos».
- **Cómo se midió el éxito** (acordado por el grupo el 31 oct 2026):
  - **línea base:** predecir siempre la mediana da un MAE de **42,8** (siempre el promedio: 42,9; al azar: 58,9);
  - **meta mínima: MAE ≤ 38** (11 % mejor que la línea base) y **deseable: MAE ≤ 35** (18 % mejor), con validación
    agrupada por sede;
  - **condición de equidad:** el MAE del modelo debe ser menor que el de la línea base en cada segmento de estrato, zona y
    naturaleza del colegio. **Motivo:** un buen MAE promedio puede esconder un grupo en el que el modelo se equivoca más
    que no usar modelo. La constitución del proyecto (principio VIII, 6 nov 2026) agregó el género a esos segmentos.

## 2. Datos y limpieza

> Fuente: `reports/01_eda.md`, `src/proyecto/data/` y `notebooks/03_preprocesamiento.ipynb`.

- **Datos:** resultados oficiales del ICFES en datos.gov.co (recurso `kgxf-xxbe`), Antioquia, periodo 20224, licencia
  **CC BY-SA 4.0** (crédito al ICFES). El archivo trae **144.766 filas × 51 columnas**.
- **Objetivo:** `punt_global`, de 100 a 477 puntos; promedio 245,9, mediana 242, desviación 51,6; sin vacíos y casi
  simétrico (asimetría 0,31), así que no se transformó.
- **Unidad de análisis y partición:** una fila es **un estudiante**. La entidad que se repite es la **sede del colegio**
  (`cole_cod_dane_sede`): 1.447 sedes, mediana de 33 estudiantes por sede, y la sede sola explica el **36 %** de la
  variación del puntaje. Por eso la prueba se separó **por sede**: 20 % de las sedes con `GroupShuffleSplit`, semilla 42,
  y toda validación cruzada se hizo con `GroupKFold` por sede. Resultado: **57.286 estudiantes de entrenamiento (1.155
  sedes) y 14.862 de prueba (289 sedes), con 0 sedes compartidas**. **Motivo:** medir el error con colegios que el modelo
  no vio, como pasará en la app; partir por estudiante daría un MAE optimista. Una prueba automática falla si se parte
  por fila (comprobado a mano por el grupo el 5 nov 2026).
- **Hallazgos y decisiones** (las 11 del EDA, aprobadas por el grupo el 31 oct 2026):

| # | Hallazgo | Decisión | Motivo |
|---|---|---|---|
| 1 | 72.383 filas exactamente duplicadas (50 % del archivo) | Quitar duplicados al cargar | Un mismo estudiante en entrenamiento y prueba haría la métrica optimista |
| 2 | 5 puntajes por área con correlación 0,80–0,92 con el objetivo; `desemp_ingles` y `estu_estadoinvestigacion` se conocen después del examen | Excluir las 7 columnas | Son la respuesta o información posterior: fuga |
| 3 | `estu_consecutivo` y `estu_fechanacimiento` son datos personales | El identificador solo controla duplicados; la fecha se convierte en edad y se elimina | No exponer datos personales; la edad conserva lo útil |
| 4 | 30 estudiantes con edad menor de 13 años | Edad < 13 → vacío, sin borrar la fila | Es imposible presentar Saber 11 a esa edad; borrar la fila perdería el resto |
| 5 | 10,1 % con algún vacío en `fami_` (~18 puntos menos); `cole_bilingue` 16,4 % vacío (16 puntos menos) | Vacío como categoría propia «sin respuesta», dentro del `Pipeline` | El vacío es información; imputar con la moda la borraría |
| 6 | Centinelas «No sabe», «No Aplica» y «Sin Estrato» (1.561 estudiantes, promedio 211,2) | Mantenerlos como categorías propias | Tienen puntajes distintos: llevan información |
| 7 | Estrato, personas y cuartos son categorías ordenadas guardadas como texto | Convertirlas a números ordenados; «Sin Estrato» queda vacío con la marca `sin_estrato` = 1 | Conservar el orden; un 0 inventaría un estrato |
| 8 | 4 columnas con un solo valor | Eliminarlas | No aportan información |
| 9 | Los identificadores del colegio tienen de 1.071 a 1.807 valores | Excluirlos como predictores; la sede solo agrupa | El modelo memorizaría el promedio de cada colegio, y en la app llegan colegios nuevos |
| 10 | La sede explica el 36 % de la variación | Partir y validar por sede | Medir con colegios no vistos |
| 11 | 235 estudiantes (0,3 %) de calendario «OTRO» en 3 sedes | Excluirlos; el modelo aplica a calendario A | Muy pocos casos para aprender algo confiable |

- **Exclusiones por equidad** (grupo, 31 oct 2026): `estu_tipodocumento`, `estu_nacionalidad` y `estu_privado_libertad`
  no son predictores. **Motivo:** el tipo de documento y la nacionalidad funcionarían como indicador de condición
  migratoria, y la privación de la libertad es un dato sensible.
- **Datos personales o sensibles y cómo se trataron:** el identificador del estudiante solo se usó para quitar
  duplicados; la fecha de nacimiento se convirtió en edad y se eliminó; ningún identificador del estudiante ni del
  colegio es variable de entrada. `data/raw/`, `data/processed/` y `.env` no se suben al repositorio. Tras limpiar quedan
  **72.148 estudiantes de calendario A** y 21 columnas de entrada.

## 3. Variables

> Fuente: `reports/04_features.md`.

- **Cómo se midió:** `HistGradientBoostingRegressor` con parámetros fijos, los **mismos 5 pliegues por sede** para todas
  las variantes y la regla, escrita antes de medir, de conservar una idea solo si **mejora / ruido > 1**.
- **Referencia:** MAE 33,563 (± 0,244) con las variables base y umbral de poco frecuentes del 1 %.

| Idea | MAE (± ruido) | Mejora / ruido | Decisión |
|---|---|---|---|
| `n_bienes_hogar` (bienes del hogar, 0 a 4) | 33,566 (± 0,256) | −0,01 | Descartada |
| `educacion_max_padres` (nivel más alto, escala 0–9) | 33,614 (± 0,279) | −0,18 | Descartada |
| `personas_por_cuarto` (hacinamiento) | 33,548 (± 0,269) | 0,06 | Descartada |
| `vive_en_mcpio_colegio` | 33,562 (± 0,229) | 0,01 | Descartada |
| Las 4 juntas | 33,579 (± 0,277) | −0,06 | Descartada |
| Umbral de poco frecuentes 0,5 % | 33,503 (± 0,230) | 0,26 | Descartada |
| Umbral de poco frecuentes 0,1 % | 33,390 (± 0,226) | 0,77 | Descartada; candidata para la etapa 6 |

- **Decisión:** las 4 variables nuevas quedan **apagadas** y el umbral en 1 %. **Motivo:** ninguna supera el ruido entre
  pliegues; la información que resumen ya está en las columnas base. El 0,1 % es la mayor mejora (0,17 puntos) y pasa como
  candidato a la optimización.

## 4. Torneo de modelos

> Fuente: `reports/05_torneo.md`.

- **Reglas:** los mismos 57.286 estudiantes y los mismos 5 pliegues `GroupKFold` por sede para todos; variables base;
  MAE como métrica principal y RMSE y R² como técnicas.
- **Candidatos:** línea base (mediana), Ridge, Random Forest, HistGradientBoosting y XGBoost, con parámetros de partida.
  **LightGBM se reemplazó por HistGradientBoosting** (grupo, 31 oct 2026). **Motivo:** LightGBM no carga sin el Visual C++
  Redistributable y el grupo no tiene permisos para instalarlo; HistGradientBoosting usa la misma técnica (boosting con
  histogramas) y funciona en todos los equipos.

| Modelo | MAE (± ruido) | RMSE | R² | Segundos por ajuste |
|---|---|---|---|---|
| HistGradientBoosting | **33,56 (± 0,24)** | 41,50 | 0,349 | 7,8 |
| XGBoost | 33,66 (± 0,21) | 41,62 | 0,345 | 3,3 |
| Random Forest | 34,75 (± 0,30) | 43,03 | 0,299 | 53,1 |
| Ridge | 34,78 (± 0,21) | 42,82 | 0,306 | 1,4 |
| Línea base (mediana) | 42,83 (± 0,60) | 51,71 | −0,011 | 1,5 |

- El mejor por MAE también es el mejor por RMSE y R² (no gana a costa de errores grandes).
- **Finalistas: HistGradientBoosting y XGBoost.** **Motivo:** ganan a Random Forest y a Ridge en los 5 pliegues, con
  diferencias de 5,5 a 10,6 veces el ruido; entre ellos hay un **empate práctico** (0,095 puntos, 0,95 veces el ruido), y
  XGBoost es 2,4 veces más rápido.
- **Descartados:** Random Forest (1,18 puntos peor y el más lento) y Ridge (1,21 puntos peor; el más interpretable, pero
  el caso no exige interpretabilidad por regulación).

## 5. Optimización y seguimiento

> Fuente: `reports/06_optimizacion.md`.

- **Espacio de búsqueda:** rangos alrededor de los parámetros de partida, incluidos los dos pendientes de etapas
  anteriores: el umbral (1 % o 0,1 %) y la pérdida (cuadrática o de error absoluto, alineada con el MAE).
- **Presupuesto** (fijado antes de empezar, 5 nov 2026): **25 ensayos de HistGradientBoosting y 30 de XGBoost** con Optuna
  (semilla 42), 3 pliegues por sede. **Motivo:** cabía en unos 30 minutos con los tiempos medidos.
- **Sedes reservadas:** 25 % de las sedes del entrenamiento (**289 sedes, 13.481 estudiantes**) quedaron fuera de la
  búsqueda para comprobar la mejora. La prueba no se abrió.
- **Comprobación honesta** (sedes reservadas, intervalo del 95 % con 1.000 remuestreos de sedes):

| Modelo | MAE de partida | MAE optimizado | Diferencia | Intervalo 95 % |
|---|---|---|---|---|
| HistGradientBoosting | 34,041 | 33,675 | −0,366 | [−0,640 ; −0,118] |
| XGBoost | 34,072 | 33,723 | −0,349 | [−0,570 ; −0,131] |

- **Regla 1** (escrita antes): usar los parámetros optimizados solo si todo el intervalo está bajo cero. **Se cumple en los
  dos.** La mejora real (0,35–0,37 puntos) es menor que la que sugería la búsqueda, como se esperaba.
- **Regla 2** (escrita antes): si el intervalo entre finalistas incluye el cero, se elige HistGradientBoosting.
  Diferencia −0,048, intervalo [−0,222 ; +0,119]: **empate**, se elige **HistGradientBoosting**. **Motivo del desempate:**
  viene en scikit-learn y no requiere librerías adicionales, lo que simplifica el registro y la app.
- **Modelo elegido:** HistGradientBoosting con umbral 0,1 %, pérdida de error absoluto, `learning_rate` 0,0301,
  `max_iter` 587, `max_leaf_nodes` 16, `min_samples_leaf` 82, `l2_regularization` 0,3657 y `max_features` 0,6155.
- **Seguimiento:** MLflow en **Databricks**, experimento `saber11-optimizacion`: cada uno de los 55 ensayos y las
  mediciones de partida con sus parámetros, MAE, RMSE, R² y etiquetas. Una ejecución completa con MLflow local dio los
  mismos 55 ensayos **bit a bit**. La búsqueda tardó 31,1 minutos (27,2 en local), por el registro por red; el grupo lo
  aceptó.

## 6. Validación e interpretación

> Fuente: `reports/07_validacion.md`.

- **Decisiones congeladas antes de abrir la prueba** (5 nov 2026, 19:53:16): el modelo y sus parámetros, la métrica, la
  línea base (predecir siempre **243**, la mediana del entrenamiento), las metas y la regla de equidad. El modelo final se
  entrenó con todo el entrenamiento (57.286 estudiantes).
- **La prueba se abrió una sola vez** (19:55:52, 2 min 36 s después): **14.862 estudiantes, 289 sedes** nunca vistas. No
  se cambió nada del modelo después de verla.

| Métrica | Modelo | Línea base | Diferencia | Intervalo 95 % (sedes) |
|---|---|---|---|---|
| **MAE** | **33,316** [32,394 ; 34,207] | 43,088 | **−9,772** | [−11,781 ; −7,990] |
| RMSE | 41,463 [40,344 ; 42,496] | 51,971 | −10,509 | [−12,738 ; −8,467] |
| R² | 0,363 [0,306 ; 0,414] | −0,001 | +0,364 | [0,309 ; 0,421] |

- **¿Mejora a la línea base con confianza?** Sí: todo el intervalo de la diferencia está bajo cero. **Metas:** cumple la
  mínima y la deseable, incluso con el límite superior del intervalo (34,21). Frente a las etapas anteriores (torneo
  33,56; sedes reservadas 33,675) no hay señal de que la validación haya sido optimista.
- **Errores por segmento:** cumple la condición de equidad en **14 de 14** segmentos, todos con ventaja clara. Pero el
  error **no es igual para todos:**
  - **estrato 5: MAE 39,57**, el más alto y por encima de la meta mínima (la meta es global);
  - **hombres 35,74 frente a 31,40 en mujeres** (4,34 puntos de brecha);
  - no oficiales 35,55 frente a 32,66 oficiales; urbano 33,88 frente a 30,14 rural.

  «Cumple» significa «se equivoca menos que predecir siempre la mediana», no «funciona igual para todos». Carga de
  trabajo: no aplica, el modelo entrega un puntaje.
- **Interpretación** (importancia por permutación con el MAE): **edad** (+2,48 puntos) y **jornada del colegio** (+2,30)
  son lo que más usa el modelo; muy por detrás (+0,5 a +0,73) siguen naturaleza del colegio, educación de la madre,
  computador, cuartos, educación del padre e internet. **Límite:** explica al modelo, no al mundo; no son causas, y las
  variables relacionadas (estrato, computador, internet, educación de los padres) se reparten el crédito. Se usó solo
  para describir; no cambió nada del modelo.

## 7. Registro del modelo

> Fuente: `reports/08_registro.md` y `models/ficha_modelo.md`.

- **Registro:** Unity Catalog en Databricks, `workspace.default.saber11_puntaje_global`, **versión 1**, alias
  **`champion`**, experimento `saber11-modelo-final`. Junto al modelo: sus parámetros, las métricas de la prueba con sus
  intervalos, la firma y el ejemplo de entrada (solo las 21 columnas, del entrenamiento) y el commit de origen.
  **Motivo del alias:** dice qué versión está vigente; si aparece una mejor, se mueve el alias sin cambiar a quien lo usa.
- **Ida y vuelta:** el modelo recuperado de `@champion` predice **exactamente** igual que el original (500 filas del
  entrenamiento, diferencia máxima 0).
- **Exportación:** `models/model.joblib`, exportado desde `champion`. **¿Es el evaluado?** Sí, sin volver a predecir
  sobre la prueba: su huella coincide con la del día de la apertura, predice exactamente igual que el modelo evaluado en
  las 57.286 filas del entrenamiento y el MAE recalculado con las predicciones guardadas es 33,316.
- **Esquema de entrada** (`models/input_schema.json`, calculado solo con el entrenamiento): las 21 columnas, los rangos
  **válidos** (edad 13–80, estrato 1–6, personas 1–5, cuartos 1–6), los **12 campos que admiten «sin respuesta»** (los que
  tenían vacíos en el entrenamiento; los otros 9 son obligatorios) y los nombres de los 139 municipios. Fuera del rango
  válido o con una categoría nueva en una lista cerrada, la predicción **se niega** y dice qué corregir.

## 8. Despliegue

> Fuente: `reports/09_despliegue.md`, `reports/despliegue_preparacion.md` y `reports/revision_app.md`.

- **Enlace público:** https://predictorpruebasaber.streamlit.app (Streamlit Community Cloud; repositorio
  `nandoossa/Proyecto_clase_grupo10`, rama `main`, archivo `app/streamlit_app.py`, Python 3.12).
- **Decisiones de despliegue y su motivo:**

| Decisión | Motivo |
|---|---|
| La app carga `models/model.joblib` del repositorio y **no consulta Databricks** | Sin credenciales en la nube y sin depender de la cuota de otra plataforma; una prueba automática lo verifica |
| `app/requirements.txt` con solo las 6 librerías de la app, en las mismas versiones | Streamlit Community Cloud instala menos y no instala `mlflow` ni `databricks-sdk`; el modelo se guardó con scikit-learn 1.9.1 |
| Formulario en español con textos, no códigos; municipios con nombre y código | Quien la usa no conoce los códigos internos |
| Edad como número entero sin mínimo ni máximo; fuera de 13–80, mensaje de corrección | Que la persona vea qué corregir |
| Resultado redondeado: «se equivoca en promedio 33 puntos; como referencia, entre X y Y», aclarando que no es un intervalo de confianza | El MAE de la prueba es 33,32; el error típico es un promedio |
| Aviso de uso responsable siempre visible, con estrato 5 y la brecha por género | Principio VIII: el modelo orienta, no excluye |
| Atribución en la barra lateral: «Datos: ICFES (datos.gov.co, CC BY-SA 4.0). Esta herramienta no es oficial ni está avalada por el ICFES.» | La licencia exige dar crédito al ICFES |
| No se subieron `.env`, `data/` ni el modelo intermedio | Credenciales y datos de estudiantes; la app no los necesita |

- **Pruebas del enlace** (el grupo, 7 nov 2026, en una **ventana privada**): perfil normal → **250 puntos**; edades 13 y
  80 → aceptadas; edad 81 → rechazada con mensaje; todo en «sin respuesta» → sin errores; se ven el aviso y la
  atribución. En local, con AppTest, el mismo perfil dio 250 («entre 217 y 283»).
- **Revisión del código de la app** (`reports/revision_app.md`): se corrigieron los 4 hallazgos importantes (H1 a H4) y
  los menores que no cambian el comportamiento. **H8 y H11 no se aplican** (grupo, 7 nov 2026). **Motivo:** la app solo
  carga nuestro esquema de regresión y el formulario usa un único campo para el estrato, así que esas situaciones no
  ocurren; aplicarlos cambiaría qué entradas se rechazan.
- **Plan B:** la app en local (`streamlit run app/streamlit_app.py`) y capturas de pantalla con fecha.
- **Errores de despliegue:** no se registraron en `reports/09_despliegue.md`.
- **Riesgo anotado:** el logo de la barra lateral es una marca del ICFES y no está cubierto por la licencia de los datos.

## 9. Riesgos, límites y siguientes pasos

- **Qué no hace el modelo:** no decide ni excluye; no clasifica ni etiqueta estudiantes o colegios; no explica causas; su
  estimación no es el puntaje real.
- **Límites de los datos:** un solo periodo (2022), Antioquia y calendario A; fuera de eso no se validó. Explica el 36 %
  de la variación (R² 0,363); el resto depende de información que la app no pregunta. La edad es aproximada.
- **Uso responsable:** el error es mayor en estrato 5 (39,57), en hombres (35,74 frente a 31,40) y en colegios no
  oficiales (35,55), y la app lo muestra siempre. **El género se mantiene como entrada** (grupo, 6 nov 2026). **Motivo:**
  quitarlo exigiría reentrenar y volver a evaluar con la prueba, que ya se abrió. Otros atributos de uso cuidadoso: estrato,
  zona, municipios y edad.
- **Lo que no se evaluó:** estabilidad en otros años, deriva de los datos, otros departamentos y la equidad por
  combinaciones de segmentos (por ejemplo, hombres de estrato 5).
- **Mejora concreta:** sumar más años de datos y evaluar, desde el inicio de un ciclo nuevo y con validación por sede, un
  modelo sin género como entrada; además, vigilar el error por grupo en cada cohorte.

## Anexo: cómo reproducir el proyecto

1. **Entorno** (Python 3.12):
   ```bash
   git clone https://github.com/nandoossa/Proyecto_clase_grupo10
   cd Proyecto_clase_grupo10
   uv venv --python 3.12 .venv
   uv pip install --python .venv/Scripts/python.exe -r requirements.txt   # Mac/Linux: .venv/bin/python
   ```
2. **Datos:** el notebook 03 descarga el CSV de datos.gov.co a `data/raw/` la primera vez (la URL está en
   `especificacion-proyecto.md`, sección 3). Si Python no reconoce el certificado del sitio, se puede descargar la misma
   URL con `curl` y guardarla como `data/raw/saber11_antioquia_2022.csv`.
3. **Notebooks, en orden** (en Windows, con `PYTHONUTF8=1`): 03 (limpieza y partición: 57.286 / 14.862 estudiantes,
   0 sedes compartidas) → 04 → 05 → 06 → 07 → 08 → 09.
   - Los notebooks 06 y 08 registran en Databricks: copiar `.env.example` a `.env` y completar la conexión (sin conexión,
     MLflow local).
   - El notebook 07 abre la prueba **una sola vez**: si ya existe su marca de apertura, no vuelve a evaluar.
4. **Pruebas:** `python -m pytest -q` → 117 pruebas en verde.
5. **App:** `streamlit run app/streamlit_app.py` (solo necesita `models/model.joblib` y `models/input_schema.json`, que
   están en el repositorio).

---

### Lista de comprobación antes de entregar

- [x] Las **9 secciones** tienen contenido y **cada decisión lleva su motivo**.
- [x] Las cifras **coinciden** con `reports/07_validacion.md` y con la presentación (la diapositiva 3 se corrigió el 7 nov
      2026: la línea base es 243, la mediana del entrenamiento).
- [x] No hay credenciales, `.env` ni datos personales.
- [x] El enlace de la app abre en una ventana privada (comprobado por el grupo el 7 nov 2026).
- [x] Un tercero puede reproducir el proyecto con el anexo: Raúl Fernando Ossa Ramírez siguió el anexo desde cero en un
      PC limpio el 7 nov 2026.

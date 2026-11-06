# Validación e interpretación

> Resultado de `notebooks/07_validacion_interpretacion.ipynb` (ejecución oficial del 5 nov 2026; todas las cifras salen de
> su salida y de `reports/07_metricas_test.json`, `07_equidad.csv` y `07_importancia.csv`). Reglas aprobadas por el grupo
> antes de abrir la prueba: `especificaciones/07-validacion.md` §1.

## 1. Decisiones congeladas (escritas ANTES de abrir la prueba)

| Decisión | Valor | Cómo se decidió (con qué datos) |
|---|---|---|
| Modelo final | `HistGradientBoostingRegressor`, entrenado con **todo** `train.joblib` (57.286 estudiantes, 1.155 sedes) | Etapa 6, regla 2: empate con XGBoost en sedes reservadas (−0,048, IC [−0,222 ; +0,119]) → HistGradientBoosting por el desempate aprobado |
| Parámetros (optimizados o de partida) | **Optimizados**: `min_frequency` 0,001 (0,1 %), `loss` = error absoluto, `learning_rate` 0,0301, `max_iter` 587, `max_leaf_nodes` 16, `min_samples_leaf` 82, `l2_regularization` 0,3657, `max_features` 0,6155; sin parada temprana, `random_state` 42 | Etapa 6, regla 1: mejora en sedes reservadas con IC [−0,640 ; −0,118], completo bajo cero |
| ¿Calibrar las probabilidades? | **No aplica**: regresión, sin probabilidades | — |
| Métrica principal | MAE (puntos); controles RMSE y R² | `especificacion-proyecto.md` §4 |
| Regla de decisión | **No aplica**: la app muestra el puntaje estimado | Regresión |
| Línea base | Predecir siempre la mediana del entrenamiento: **243 puntos** | La del torneo |
| Metas | MAE ≤ 38 (mínima) y ≤ 35 (deseable) | `especificacion-proyecto.md` §4 |
| Regla de equidad | Cumple si MAE modelo < MAE línea base en el segmento; si cumple, «con ventaja clara» cuando el IC 95 % (sedes) de la diferencia excluye el cero y «sin ventaja concluyente» cuando lo incluye | `reports/00_caso.md`; clasificación aprobada por el grupo el 5 nov 2026 |
| **Fecha y hora en que se congelaron** | **2026-11-05T19:53:16** (`reports/07_decisiones_congeladas.json`) | — |

## 2. Calibración (con entidades reservadas, no con la prueba)

- ¿Se evaluó? ☐ sí  ☒ no → no hace falta: es **regresión**. No hay probabilidades ni umbral; la app muestra el puntaje.

## 3. La prueba, abierta **una sola vez**

- **Fecha y hora en que se abrió:** 2026-11-05T19:55:52 (`reports/prueba_abierta.txt`), 2 min 36 s después de congelar las
  decisiones. **14.862 estudiantes, 289 sedes**, ninguna presente en el entrenamiento (el notebook lo comprueba).
- **¿Se cambió algo del modelo después de verla?** ☒ no  ☐ sí.
- **Transparencia:**
  - `test.joblib` se regeneró el 5 nov 2026 con el notebook 03 (misma partición, semilla 42), sin leerlo.
  - Antes de la ejecución oficial se hizo un **ensayo general** del notebook en una carpeta temporal fuera del repositorio,
    con un entrenamiento y una «prueba» **falsos**, ambos sacados de `train.joblib` con `split_by_group`. El ensayo no usó
    `test.joblib` y sus cifras no se usaron para nada; solo comprobó que el notebook corre completo.
  - Las predicciones y la importancia por permutación quedaron guardadas en `data/processed/prueba_resultados.joblib`: si se
    re-ejecuta el notebook, no vuelve a evaluar con la prueba.

| Métrica | Modelo final | Línea base (mediana) | Diferencia (modelo − línea base) | Intervalo del 95 % (sedes) |
|---|---|---|---|---|
| **MAE** (principal) | **33,316** [32,394 ; 34,207] | 43,088 [41,376 ; 44,980] | **−9,772** | [−11,781 ; −7,990] |
| RMSE (control 1) | 41,463 [40,344 ; 42,496] | 51,971 [49,792 ; 54,367] | −10,509 | [−12,738 ; −8,467] |
| R² (control 2) | 0,363 [0,306 ; 0,414] | −0,001 [−0,020 ; −0,000] | +0,364 | [0,309 ; 0,421] |

Intervalos de cada métrica entre corchetes; 1.000 remuestreos de sedes completas.

**¿Mejora al baseline con confianza?** **Sí.** Todo el intervalo de la diferencia de MAE está bajo cero ([−11,781 ; −7,990]):
el modelo se equivoca **9,77 puntos menos por estudiante** que no usar modelo (22,7 % menos). RMSE y R² mejoran también, con
intervalos que no cruzan el cero.

**Metas:**

| Meta | MAE puntual (33,32) | Límite superior del IC (34,21) |
|---|---|---|
| Mínima (≤ 38) | cumple | cumple |
| Deseable (≤ 35) | cumple | cumple |

**Comparación con las etapas anteriores** (orientativa: otros datos y otra forma de medir): torneo 33,56 (5 pliegues, todo
el entrenamiento, parámetros de partida); etapa 6, 33,675 en las sedes reservadas (que se usaron para decidir). La prueba da
33,32: no hay señal de que la validación haya sido optimista.

## 4. Errores por segmento (condición de equidad)

> En regresión no hay «% que el modelo marca»: se compara el MAE del modelo con el de la línea base en cada segmento. «Dif.»
> = MAE modelo − MAE línea base (negativa: el modelo se equivoca menos).

| Variable | Segmento | Estudiantes | Sedes | MAE modelo | MAE línea base | Dif. | IC 95 % (sedes) | Veredicto |
|---|---|---:|---:|---:|---:|---:|---|---|
| Estrato | Estrato 1 | 3.068 | 245 | 31,92 | 39,17 | −7,25 | [−9,60 ; −5,17] | cumple con ventaja clara |
| Estrato | Estrato 2 | 5.453 | 258 | 33,43 | 40,09 | −6,65 | [−7,83 ; −5,46] | cumple con ventaja clara |
| Estrato | Estrato 3 | 3.637 | 245 | 34,19 | 44,16 | −9,97 | [−12,39 ; −7,54] | cumple con ventaja clara |
| Estrato | Estrato 4 | 800 | 169 | 35,57 | 54,98 | −19,41 | [−24,86 ; −14,31] | cumple con ventaja clara |
| Estrato | Estrato 5 | 325 | 89 | 39,57 | 71,12 | −31,55 | [−41,60 ; −16,93] | cumple con ventaja clara |
| Estrato | Estrato 6 | 127 | 61 | 33,83 | 60,37 | −26,54 | [−35,69 ; −14,73] | cumple con ventaja clara |
| Estrato | Sin Estrato | 285 | 124 | 30,24 | 47,55 | −17,31 | [−22,26 ; −12,56] | cumple con ventaja clara |
| Estrato | Sin dato (vacío) | 1.167 | 197 | 31,12 | 45,14 | −14,02 | [−21,20 ; −7,29] | cumple con ventaja clara |
| Zona | Rural | 2.234 | 130 | 30,14 | 41,35 | −11,21 | [−14,71 ; −8,18] | cumple con ventaja clara |
| Zona | Urbano | 12.628 | 159 | 33,88 | 43,40 | −9,52 | [−11,80 ; −7,45] | cumple con ventaja clara |
| Naturaleza | No oficial | 3.378 | 54 | 35,55 | 52,71 | −17,16 | [−25,26 ; −10,88] | cumple con ventaja clara |
| Naturaleza | Oficial | 11.484 | 235 | 32,66 | 40,26 | −7,60 | [−9,54 ; −5,99] | cumple con ventaja clara |
| Género | F | 8.297 | 279 | 31,40 | 42,06 | −10,66 | [−13,06 ; −8,18] | cumple con ventaja clara |
| Género | M | 6.565 | 271 | 35,74 | 44,39 | −8,65 | [−10,59 ; −6,98] | cumple con ventaja clara |

**Resultado de la condición de equidad:** se cumple en los **14 de 14** segmentos, todos **con ventaja clara** (ningún
intervalo incluye el cero). **Ningún segmento incumple.**

- **¿Hay un segmento al que le va peor? ¿Por qué podría ser?** Sí, aunque todos mejoran a la línea base, el error del
  modelo **no es igual entre grupos**:
  - **Estrato 5: MAE 39,57**, el más alto de todos y **por encima de la meta mínima de 38** (la meta es global, no por
    segmento, pero conviene decirlo). Son 325 estudiantes en 89 sedes; sus puntajes están lejos del centro y el modelo tiene
    pocos ejemplos parecidos. Estratos 4 (35,57) y 6 (33,83, solo 127 estudiantes) también quedan por encima del promedio.
  - **Género: los hombres tienen 4,34 puntos más de error que las mujeres** (35,74 frente a 31,40). Los dos cumplen la
    condición, pero la brecha es real y se informa como límite.
  - **Naturaleza:** no oficial 35,55 frente a oficial 32,66. **Zona:** urbano 33,88 frente a rural 30,14.
  - Las ventajas más grandes del modelo están justo donde la línea base falla más (estratos 4–6, no oficiales).
- **Cómo leer «cumple» (auditoría, H5):** significa «se equivoca menos que predecir siempre la mediana» en ese segmento, no
  «funciona igual de bien para todos». La línea base es una constante, fácil de superar; por eso las brechas de arriba
  importan más que el 14 de 14. Son 14 intervalos sin ajuste por comparaciones múltiples, y los segmentos con pocas sedes
  (estrato 6: 61; estrato 5: 89) tienen intervalos anchos. La regla no se cambia: estaba aprobada antes de abrir la prueba.
- **Carga de trabajo:** no aplica; el modelo no prioriza revisiones, entrega un puntaje.

## 5. Interpretación

Importancia por permutación sobre la prueba con el MAE (cuánto sube el error, en puntos, al desordenar cada columna; 5
repeticiones):

| Puesto | Variable | Aumento del MAE (± desv.) |
|---:|---|---|
| 1 | `edad` | 2,476 (± 0,027) |
| 2 | `cole_jornada` | 2,296 (± 0,084) |
| 3 | `cole_naturaleza` | 0,725 (± 0,059) |
| 4 | `fami_educacionmadre` | 0,682 (± 0,030) |
| 5 | `fami_tienecomputador` | 0,663 (± 0,043) |
| 6 | `fami_cuartoshogar` | 0,551 (± 0,020) |
| 7 | `fami_educacionpadre` | 0,550 (± 0,012) |
| 8 | `fami_tieneinternet` | 0,503 (± 0,041) |
| 9 | `estu_genero` | 0,484 (± 0,045) |
| 10 | `cole_cod_mcpio_ubicacion` | 0,372 (± 0,027) |
| 11–21 | `estu_cod_reside_mcpio` 0,345 · `fami_estratovivienda` 0,334 · `fami_personashogar` 0,291 · `cole_area_ubicacion` 0,240 · `fami_tieneautomovil` 0,212 · `cole_bilingue` 0,156 · `cole_genero` 0,122 · `cole_caracter` 0,099 · `fami_tienelavadora` 0,054 · `sin_estrato` 0,043 · `cole_sede_principal` 0,018 | |

- **Qué pesa más, en palabras simples:**
  - **La edad** es lo que más usa el modelo: si se desordena, el error sube 2,5 puntos. Un estudiante mayor de lo esperado
    para grado 11 suele haber repetido años o interrumpido sus estudios, y el modelo lo asocia con puntajes más bajos.
  - **La jornada del colegio** (mañana, tarde, única, noche, sábados…) es casi igual de importante (2,3 puntos). Distingue,
    por ejemplo, la educación de adultos en jornadas nocturnas o de fin de semana, que se relaciona con la edad.
  - Después, a mucha distancia (0,5–0,7 puntos cada una): **colegio oficial o no**, **educación de la madre y del padre**,
    **tener computador e internet** y el tamaño de la vivienda. Juntas describen el nivel socioeconómico y educativo del
    hogar.
- **Por qué el estrato aparece abajo (puesto 12):** no es que no importe; su información está repartida con computador,
  internet, educación de los padres y naturaleza del colegio. Al desordenar solo el estrato, el modelo la recupera de las
  otras. Por eso esta tabla **no** sirve para decir «el estrato no influye en el puntaje».
- **Uso solo descriptivo (auditoría, R3):** esta importancia se calculó sobre la prueba y no se usó para cambiar nada. Si el
  grupo quisiera quitar variables, tendría que decidirlo con validación por sede en un ciclo nuevo y declarar que la prueba
  ya se usó.
- **Límite de la explicación:** explica **al modelo**, no al mundo. No dice si el modelo acertó, ni que estas variables
  **causen** el puntaje (por ejemplo, darle un computador a un estudiante no sube su puntaje en 0,66 puntos). Las variables
  correlacionadas se reparten el crédito.
- **Atributos sensibles o de uso cuidadoso entre las variables:**
  - **Género** (`estu_genero`), puesto 9 (0,48 puntos).
  - **Estrato** (puesto 12) y la marca «Sin Estrato» (puesto 20).
  - **Zona** (puesto 14).
  - **Municipios** de colegio y de residencia (puestos 10 y 11).
  - **Edad** (puesto 1).

  Qué se hace: se declaran en la ficha del modelo y en la app. La estimación de un estudiante **no** debe usarse para
  etiquetarlo ni excluirlo por estos atributos. Antes de un uso real convendría evaluar con el grupo y con la Secretaría si
  mantener el género como entrada: aporta poco (0,48 puntos) y hay una brecha de error de 4,3 puntos entre hombres y mujeres.
  Esa evaluación sería un trabajo nuevo, con validación y no con esta prueba, que ya se usó.

## 6. Conclusión

- **¿El modelo sirve para la decisión del caso? ¿Con qué condiciones?** Sí, para **orientar**:
  - con sedes que nunca vio se equivoca en promedio **±33,3 puntos** (IC [32,4 ; 34,2]), 9,8 puntos menos que no usar
    modelo, y cumple las dos metas incluso en el peor extremo del intervalo;
  - cumple la condición de equidad en los 14 segmentos, con ventaja clara;
  - condiciones: es una estimación con error típico de ±33 puntos y explica solo el **36 %** de la variación del puntaje
    (R² 0,363); aplica a calendario A en Antioquia, periodo 2022; el error es mayor en estrato 5 (39,6), en hombres (35,7)
    y en colegios no oficiales (35,6), y eso debe mostrarse junto a la estimación.
- **Qué NO debe hacerse con él:**
  - usarlo para excluir, clasificar o etiquetar estudiantes o colegios;
  - tratar la estimación como el puntaje real;
  - leer la importancia de variables como causas;
  - usarlo fuera de Antioquia, en otro calendario o en otro año sin volver a validarlo;
  - abrir de nuevo esta prueba para ajustar el modelo: ya se usó.

# Ficha del modelo · Puntaje global Saber 11 en Antioquia

> Documento corto para leer **antes** de usar el modelo. Cifras de `reports/07_validacion.md`,
> `reports/07_metricas_test.json` y `reports/08_registro.json` (5 nov 2026).

## Qué es

Estima el **puntaje global de Saber 11** (`punt_global`, de 100 a 477 puntos) que puede esperar un estudiante de grado 11
de Antioquia, a partir de 21 datos de su colegio, su perfil y su familia que se conocen antes del examen. Sirve para
**orientar**:
- a la Secretaría de Educación, sobre a qué colegios o municipios dirigir refuerzos;
- a rectores y docentes, sobre qué estudiantes necesitan preparación adicional;
- a estudiantes y familias, sobre su preparación.

La decisión final la toma una persona.

- **Modelo:** `HistGradientBoostingRegressor` de scikit-learn, dentro de un `Pipeline` con el preprocesamiento (imputación,
  codificación de categorías con umbral de poco frecuentes del 0,1 %). Pérdida de error absoluto; `learning_rate` 0,0301,
  587 iteraciones, 16 hojas, mínimo 82 estudiantes por hoja, `l2_regularization` 0,3657, `max_features` 0,6155.
- **Registro:** `workspace.default.saber11_puntaje_global` versión **1**, alias **`champion`**, en Databricks (Unity
  Catalog). Copia para la app: `models/model.joblib`, exportada desde `champion`. Esquema de entrada:
  `models/input_schema.json`.
- **Regla de decisión:** no hay. Es regresión: se muestra el puntaje estimado.

## Datos de entrenamiento

- **Fuente y licencia:** resultados oficiales del ICFES en datos.gov.co (recurso `kgxf-xxbe`), Antioquia, periodo 20224.
  Licencia CC BY-SA 4.0 (crédito al ICFES).
- **Tamaño:** 57.286 estudiantes de 1.155 sedes (entrenamiento). La prueba tiene 14.862 estudiantes de 289 sedes
  distintas.
- **Partición:** por **sede del colegio** (`cole_cod_dane_sede`). La prueba se abrió **una sola vez**, el 5 nov 2026 a las
  19:55, con las decisiones congeladas antes, a las 19:53.
- **Datos personales:** el identificador del estudiante solo se usó para quitar duplicados; la fecha de nacimiento se
  convirtió en edad y se eliminó; ningún identificador del estudiante ni del colegio es variable de entrada. Se excluyeron
  el tipo de documento, la nacionalidad y la privación de la libertad por equidad.

## Rendimiento (prueba, 289 sedes nunca vistas)

Intervalos del 95 % con 1.000 remuestreos de sedes completas.

| Métrica | Modelo | Línea base (predecir siempre 243, la mediana) | Diferencia |
|---|---|---|---|
| **MAE** (puntos) | **33,32** [32,39 ; 34,21] | 43,09 [41,38 ; 44,98] | **−9,77** [−11,78 ; −7,99] |
| RMSE | 41,46 [40,34 ; 42,50] | 51,97 [49,79 ; 54,37] | −10,51 [−12,74 ; −8,47] |
| R² | 0,363 [0,306 ; 0,414] | −0,001 | +0,364 [0,309 ; 0,421] |

- En palabras: con colegios que no vio, el modelo se equivoca en promedio **±33 puntos**, 9,8 puntos menos (22,7 %) que no
  usar modelo.
- Cumple la meta mínima (≤ 38) y la deseable (≤ 35), incluso con el límite superior del intervalo.

**Por segmento** (MAE del modelo frente a la línea base; todos cumplen la condición de equidad con ventaja clara):

| Segmento | MAE modelo | MAE línea base |
|---|---|---|
| Estrato 1 / 2 / 3 | 31,92 / 33,43 / 34,19 | 39,17 / 40,09 / 44,16 |
| Estrato 4 / **5** / 6 | 35,57 / **39,57** / 33,83 | 54,98 / 71,12 / 60,37 |
| Sin Estrato / Sin dato | 30,24 / 31,12 | 47,55 / 45,14 |
| Rural / Urbano | 30,14 / 33,88 | 41,35 / 43,40 |
| No oficial / Oficial | 35,55 / 32,66 | 52,71 / 40,26 |
| Mujeres / **Hombres** | 31,40 / **35,74** | 42,06 / 44,39 |

## Variables que más pesan

Importancia por permutación en la prueba (cuánto sube el MAE si se desordena la columna):
1. **Edad:** +2,48 puntos.
2. **Jornada del colegio:** +2,30 puntos.
3. Muy por detrás (+0,5 a +0,73 cada una): naturaleza del colegio, educación de la madre, tener computador, cuartos del
   hogar, educación del padre e internet.

Explica al modelo, no las causas del puntaje. Las variables relacionadas entre sí, como estrato, computador, internet y
educación de los padres, se reparten el crédito.

## Límites y usos no recomendados

- **Datos con los que se entrenó:** solo calendario A, Antioquia, periodo 2022. Fuera de eso no se ha validado.
- **Precisión limitada:** explica el 36 % de la variación del puntaje (R² 0,363). El error típico es de ±33 puntos y hay
  estudiantes con errores mucho mayores (RMSE 41,5).
- **El error no es igual para todos:**
  - en **estrato 5 el MAE es 39,57**, por encima de la meta de 38;
  - los **hombres tienen 4,34 puntos más de error que las mujeres** (35,74 frente a 31,40);
  - los colegios no oficiales tienen 35,55 frente a 32,66 de los oficiales.

  Esto debe mostrarse junto a la estimación.
- **Supuestos:** las 21 entradas se conocen antes del examen. La edad es aproximada (año de la prueba menos año de
  nacimiento). Un campo vacío se trata como «sin respuesta» solo en los 12 campos que tenían vacíos en el entrenamiento;
  los demás son obligatorios.
- **Atributos sensibles o de uso cuidadoso:** género, estrato, zona, municipios y edad. El género aporta poco (+0,48
  puntos) y tiene la brecha de error descrita. **Decisión del grupo (6 nov 2026): se mantiene como entrada.** Quitarlo
  exigiría reentrenar el modelo y volver a evaluarlo con la prueba, que ya se abrió una vez; una segunda evaluación ya no
  sería una medición limpia. La app pide el género y muestra la brecha de error en el aviso de uso responsable.
- **Qué NO debe hacerse con este modelo:**
  - excluir, clasificar o etiquetar a estudiantes o colegios;
  - tratar la estimación como el puntaje real;
  - leer la importancia de variables como causas;
  - usarlo en otro departamento, calendario o año sin volver a validarlo.

  **Orienta; no excluye.**
- **Lo que no se evaluó:**
  - estabilidad en el tiempo (otros años);
  - deriva de los datos;
  - otros departamentos;
  - la equidad por combinaciones de segmentos (por ejemplo, hombres de estrato 5);
  - comparaciones múltiples entre los 14 segmentos.

## Reproducibilidad

- Código en `src/proyecto/`, pruebas en `tests/` (`python -m pytest -q`) y notebooks 01 a 08 en `notebooks/`.
- El ejemplo de entrada registrado en Databricks son 5 filas reales del entrenamiento, sin identificadores (espacio de
  trabajo privado del grupo).
- El modelo registrado salió del commit `3a75853` (con cambios de la etapa 8 aún sin commit en ese momento) y de la
  ejecución `78b51940c3f74aa8a6d3877b8a4ee739` del experimento `saber11-modelo-final`.
- La copia exportada predice **exactamente** igual que el modelo evaluado en las 57.286 filas del entrenamiento. El MAE
  recalculado con las predicciones guardadas de la prueba es 33,316.
- **Dependencia del código** (revisión de la app, H6): `models/model.joblib` guarda una referencia a la función
  `proyecto.features.engineering._as_text`. Para cargarlo hace falta que `src/` esté en el path, como hace la app, y que ese
  archivo siga en el repositorio con el mismo nombre. Si se mueve o se renombra, el modelo no carga. Es un *pickle*: solo se
  carga este archivo, nunca uno de origen desconocido.
- **Librerías para usarlo:** las de `app/requirements.txt` (streamlit 1.66.0, pandas 3.0.6, numpy 2.5.4, scikit-learn 1.9.1,
  scipy 1.18.1, joblib 1.6.0) con Python 3.12. Comprobado el 6 nov 2026 en un entorno limpio, solo con esas librerías.

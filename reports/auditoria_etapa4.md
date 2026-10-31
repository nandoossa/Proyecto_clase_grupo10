# Auditoría de fuga · Etapa 4 (T024)

- **Fecha:** 31 oct 2026
- **Revisor:** subagente `auditor-de-fuga` (`.claude/agents/auditor-de-fuga.md`), solo lectura.
- **Código auditado:** `src/proyecto/features/engineering.py` y `tests/test_features.py`, versión del commit `1412e46`.
- **Estado:** informe sin correcciones aplicadas. **El grupo decide qué se corrige.** Este informe es un punto de partida
  y no reemplaza que cada integrante entienda el código (`CLAUDE.md`).

> Nota: el auditor no leyó todos los archivos que piden sus instrucciones: le faltaron `.specify/memory/constitution.md`,
> `especificacion-proyecto.md` y `especificaciones/03-preprocesamiento.md`. Consideró que la lista de columnas
> prohibidas ya estaba en `reports/01_eda.md`, `especificaciones/04-features.md` y el contrato. Para auditar la etapa 3
> sí tendrá que leerlos.

## Respuestas a los cuatro puntos

1. **Aprendizaje fuera del `Pipeline`:** no hay.
   - `engineering.py` no contiene `fit`, `mean`, `median` ni `groupby`.
   - La mediana, la escala y las categorías se aprenden solo dentro del `ColumnTransformer`: líneas 151 (`SimpleImputer`
     mediana), 153 (`StandardScaler`), 156 (imputador constante) y 157 (`OneHotEncoder`).
   - `_as_text` (125–135) no aprende nada.
   - `add_features` (92–107) usa solo columnas de la misma fila, sin agregados por sede ni por municipio: la suma por fila
     usa `axis=1` (97), el máximo es por fila (100), la razón se calcula fila a fila (103) y la comparación de municipios
     también (106).
2. **Columnas conocidas después del examen o identificadores:** ninguna.
   - Se compararon `NUMERIC_BASE`, `CATEGORICAL_BASE`, `MUNICIPALITY_CODES` y `NUMERIC_ENGINEERED` (líneas 16–46) con las
     columnas sospechosas del EDA: los 5 puntajes por área, `desemp_ingles` y `estu_estadoinvestigacion`. Ninguna está entre
     los predictores, y tampoco hay identificadores de estudiante o de colegio.
   - Los municipios entran como código de ubicación del colegio y de residencia, datos que el usuario conoce al decidir.
3. **Cobertura de `FORBIDDEN_COLUMNS` (48–67):** cubre las 18 que exigen las especificaciones.
   - Son: los 7 con fuga, los 2 datos personales, los 5 identificadores del colegio, las 3 exclusiones por equidad y
     `punt_global`.
   - `extra_numeric` está bloqueado en las líneas 118–120 (`ValueError`).
   - `remainder="drop"` (164) impide que se cuele cualquier otra columna de la entrada, aunque esa entrada traiga
     `punt_global` y `cole_cod_dane_sede`.
4. **Pruebas:** detectarían los casos más probables, pero tienen huecos (tabla siguiente).

## Hallazgos (ninguno es una fuga confirmada: son debilidades de la red de seguridad)

| # | Hallazgo | Archivo:línea | Por qué importa | Cómo corregirlo (propuesta del auditor) |
|---|---|---|---|---|
| 1 | La prueba solo comprueba explícitamente 6 de las 18 columnas prohibidas | `tests/test_features.py:60-62` | Compara los predictores contra `FORBIDDEN_COLUMNS` (línea 59). Si alguien borra de esa lista, por ejemplo, `desemp_ingles`, `punt_ingles`, `estu_estadoinvestigacion` o `cole_codigo_icfes` y la agrega a `CATEGORICAL_BASE`, la prueba sigue en verde: esas 12 no tienen respaldo independiente | Escribir en la prueba la lista literal de las 18 y exigir que cada una esté en `FORBIDDEN_COLUMNS` y no en `numeric + categorical` |
| 2 | La prueba del preprocesador no cubre todas las columnas que pide la especificación | `tests/test_features.py:76-87` | La sección 6 de `04-features.md` pide verificar `estu_consecutivo`, `estu_fechanacimiento`, `desemp_ingles`, `estu_estadoinvestigacion` y los otros identificadores del colegio, pero `_frame` (18–46) no los trae y la prueba solo revisa 6 nombres (85–86) | Agregar esas columnas a la tabla de prueba y a la lista de nombres que no deben aparecer |
| 3 | `extra_numeric` se valida con una lista de prohibidas, no con una de permitidas | `engineering.py:118` | Una columna que no esté en la lista de prohibidas pasa; por ejemplo, una columna futura calculada con el objetivo (`sede_promedio`). Hoy no existe ninguna así: es un riesgo, no una fuga | Opcional: exigir que `extra_numeric` pertenezca a una lista de columnas permitidas |
| 4 | Ninguna prueba verifica que `add_features` use solo datos de la misma fila | `tests/test_features.py:120-168` | Si alguien agrega un promedio por sede o por municipio, ninguna prueba falla | Agregar una prueba que aplique `add_features` a toda la tabla y a cada fila por separado, y compruebe que el resultado es igual |

## Lo que no pudo comprobar

- **Partición por sede y prueba automática de la partición:** `split.py` y `cleaning.py` todavía no existen. Queda
  pendiente; no es un hallazgo.
- **Ajuste solo con entrenamiento en la práctica:** el código deja el ajuste dentro del `ColumnTransformer`, pero todavía
  no existen `build_pipeline` ni el notebook 04, que son los que llaman a `fit`. Hay que volver a auditarlo cuando existan.
- **Uso de la prueba para decidir:** `notebooks/04_features.ipynb` es una plantilla sin ejecutar y no hay `data/processed/`.
- **Métricas casi perfectas:** todavía no hay resultados.
- **Fuera de alcance:** `src/proyecto/inference/schema.py:77` calcula una mediana sobre la tabla que reciba. Es código de la
  plantilla del ejemplo y no se evaluó como fuga. Conviene revisar con qué datos se llama cuando llegue la etapa de
  despliegue.

## Veredicto

**Sin fuga evidente en `engineering.py`.** Hay que reforzar los huecos de prueba de la tabla, sobre todo el 1 y el 2. La
partición, el ajuste y el uso de la prueba se vuelven a auditar cuando existan las etapas 3 y 5.

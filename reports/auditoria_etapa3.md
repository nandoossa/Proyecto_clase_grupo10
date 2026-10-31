# Auditoría de fuga · Etapa 3 (T034)

- **Fecha:** 31 oct 2026
- **Revisor:** subagente `auditor-de-fuga` (`.claude/agents/auditor-de-fuga.md`), solo lectura.
- **Código auditado:** `src/proyecto/data/cleaning.py`, `src/proyecto/data/split.py`, `notebooks/03_preprocesamiento.ipynb`
  (ejecutado) y sus pruebas, en la versión del commit `b5418c8`.
- **Estado:** informe sin correcciones aplicadas. **El grupo decide qué se corrige.** Este informe es un punto de partida
  y no reemplaza que cada integrante entienda el código (`CLAUDE.md`).

**Archivos que leyó el auditor:** sus instrucciones, `.specify/memory/constitution.md`, `especificacion-proyecto.md`,
`especificaciones/03-preprocesamiento.md`, `reports/01_eda.md`, `cleaning.py`, `split.py`, `load.py`, el notebook 03
(código y salidas), `tests/test_cleaning.py` y `tests/test_split.py`, y partes de los notebooks 04 y 06 para contexto. No
leyó `specs/002-preprocessing/` (no le hizo falta) ni volvió a leer `engineering.py` (ya auditado).

## Respuestas a los seis puntos

1. **Partición por sede en todos los caminos: sí.**
   - `split_by_group` usa `GroupShuffleSplit` con `groups=df[group_col]` (`split.py:18-19`) y verifica de inmediato con
     `assert_disjoint_groups` (`split.py:22`).
   - `group_cv` devuelve `GroupKFold` (`split.py:37-39`).
   - El notebook llama a `split_by_group(clean_df, group_col=ID_COL, test_size=0.2, seed=42)` con
     `ID_COL = "cole_cod_dane_sede"` y vuelve a comprobar que las sedes estén separadas y que no se pierdan filas.
   - La salida coincide: 1.155 + 289 = 1.444 sedes, 0 compartidas (1.447 del EDA menos las 3 sedes que solo tenían
     calendario «OTRO»).
   - En `src/` no hay `train_test_split`, `KFold`, `StratifiedKFold` ni `.sample(`. El único `train_test_split` está en
     `tests/test_split.py:5,43`, a propósito, para mostrar que partir por fila comparte sedes.
2. **La limpieza no aprende de los datos completos.**
   - `cleaning.py` no tiene `fit`, `mean`, `median`, `mode`, `groupby` ni escaladores.
   - La edad es una resta fija, fila por fila (`cleaning.py:50-51`); el umbral de 13 es fijo (`:58`); las ordinales
     usan diccionarios escritos a mano (`:32-34`, aplicados en `:68-71`).
   - Los vacíos se dejan vacíos; medianas y escaladores solo existen dentro del `Pipeline` (`engineering.py:151-156`),
     como pide el principio III.
   - **Quitar duplicados antes de partir no es fuga** (`cleaning.py:39`): solo borra filas idénticas en las 51 columnas,
     incluido `estu_consecutivo`, sin calcular nada a partir de otras filas. Al contrario, si quedaran, las dos copias de
     un estudiante contarían doble. No caerían una a cada lado, porque comparten sede y la sede va entera a un solo lado.
3. **El notebook no usa la prueba para decidir: correcto.** Solo cuenta filas y sedes (`len(test)`,
   `test[ID_COL].nunique()`), calcula la intersección de sedes y la guarda con `joblib.dump`. No usa `punt_global` ni las
   variables de la prueba; no hay métricas, umbrales ni selección.
4. **Las 7 columnas sospechosas quedan fuera.**
   - `LEAKAGE_COLUMNS` (`cleaning.py:12-20`) son exactamente las 7 del EDA, y `drop_leakage_columns` las quita (`:44`).
     El notebook lo comprueba («sin columnas con fuga: True»).
   - Las 36 columnas que quedan se conocen antes del examen.
   - `estu_tipodocumento`, `estu_nacionalidad`, `estu_pais_reside` y `estu_privado_libertad` se conservan en la tabla,
     pero no entran como predictores por equidad; eso es de la etapa 4 y no lo verificó aquí.
5. **Pruebas automáticas que fallan si se parte por fila: sí.**
   - `test_split_never_shares_a_school_between_train_and_test` (`tests/test_split.py:21-25`).
   - `test_split_keeps_each_school_together` (`:28-31`).
   - `test_group_cv_folds_do_not_share_schools` (`:49-52`).
   - `test_assert_disjoint_raises_on_overlap` (`:34-37`).
6. **Métricas casi perfectas:** todavía no hay métricas (el notebook 03 solo cuenta filas, columnas y sedes).

## Hallazgos de fuga

**Ninguno verificado.**

## Debilidades menores (no son fuga)

| # | Debilidad · archivo:línea | Por qué importa | Cómo corregirla (propuesta del auditor) |
|---|---|---|---|
| 1 | Los notebooks 04, 05 y 06 son plantillas con `ID_COL = None`. Con ese valor, el 04 usa `KFold(... shuffle=True)` por fila (`04_features.ipynb:123`; igual en `05_torneo.ipynb:102`) y el 06 usa `train_test_split` por fila (`06_optimizacion.ipynb:160`) | Si el grupo olvida poner `ID_COL = "cole_cod_dane_sede"`, esas etapas partirían por fila sin avisar y el MAE saldría optimista. Hoy no es fuga, porque no se han ejecutado | Al completarlos, poner `ID_COL = "cole_cod_dane_sede"` y quitar la rama por fila; repetir la auditoría en las etapas 5 y 6 |
| 2 | Sigue sin marcar la comprobación a mano «la prueba de partición falla si se cambia a partición por fila» (`especificaciones/03-preprocesamiento.md:98`) | No se pudo confirmar que se hizo | Cambiar temporalmente `split_by_group` a partición por fila, correr `pytest tests/test_split.py`, ver que falle y dejarlo bien |
| 3 | `tests/test_split.py` no prueba con la salida de `clean` que cada sede quede completa; esa comprobación solo es un `assert` del notebook | Riesgo bajo: la prueba sintética ya cubre la lógica | Opcional: una prueba sobre la salida de `clean` con datos de prueba hechos a mano |
| 4 | `cole_cod_dane_sede` sigue como columna en entrenamiento y prueba (`cleaning.py:23`) | Debe quedar fuera del `Pipeline` (etapa 4); aquí no se verificó | Confirmarlo en la auditoría de la etapa 4 (ya cubierto allí: está en `FORBIDDEN_COLUMNS`) |
| 5 | `src/proyecto/inference/schema.py:77` calcula `values.median()` | Fuera de alcance. Si se calcula con todos los datos y se usa para entrenar, sería fuga; si es solo para la app, es normal | Revisarlo cuando se audite la etapa de inferencia |

## Lo que el auditor no pudo comprobar (solo lee; no ejecuta)

- Que las pruebas pasen («52 de 52»).
- Que `data/raw/` no haya cambiado (huella SHA-256).
- Que las cifras del notebook sean reales: están en sus salidas y son coherentes con el EDA (72.148 = 72.383 − 235), pero
  no volvió a ejecutar nada.
- Que `estu_nacionalidad`, `estu_pais_reside` y `estu_privado_libertad` queden fuera del modelo (etapa 4).

### Verificado aparte, el mismo día, ejecutando comandos (fuera del auditor)

- `pytest` desde la raíz: **52 de 52 en verde**, con el `pytest.ini` agregado.
- `data/raw/saber11_antioquia_2022.csv`: **misma huella SHA-256** antes y después de ejecutar el notebook 03.
- Leyendo `data/processed/*.joblib` por fuera del notebook (de la prueba solo se contaron filas y sedes): entrenamiento
  57.286 filas / 1.155 sedes, prueba 14.862 / 289, **0 sedes compartidas**, 72.148 en total.
- Partición por fila simulada en una **copia** del código (no en el repositorio): fallan 3 pruebas de
  `tests/test_split.py` con «132 sedes aparecen en más de una partición». Detalle en la sección «Comprobación a mano» de la
  respuesta al grupo; la comprobación oficial la hace el grupo.

## Veredicto

**Sin fuga evidente** en `cleaning.py`, `split.py` y el notebook 03. Quedan las debilidades menores de la tabla, sobre
todo la 1: las plantillas de los notebooks 04 a 06 con `ID_COL = None`.

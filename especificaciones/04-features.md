# Especificación · Etapa 4 · Variables (features) y preprocesamiento del modelo

> Se llena **antes** de pedirle código a Claude, a partir de `reports/01_eda.md` y de `03-preprocesamiento.md`.
> Claude la lee y la implementa; ustedes revisan que el código haga **exactamente** esto
> (`material-del-curso/kit/checklist-revision-ia.md`).
> Ejemplo de estructura (no de columnas): `material-del-curso/ejemplo-creditsight/src/creditsight/features/engineering.py`.

**Grupo:** Predictor de resultados Pruebas Saber 11 en Antioquia   **Fecha:** 31 oct 2026   **Estado:** ☒ borrador  ☐ cerrada

> Borrador preparado por Claude. Las cifras salen de `reports/01_eda.md` y de `data/raw/` (72.148 estudiantes de
> calendario A, sin duplicados). Lo que está entre **[POR DECIDIR]** lo decide el grupo.

## 1. Entrada y dependencia

- **Entrada:** la tabla que entrega la limpieza de la etapa 3 (`src/proyecto/data/cleaning.py`), ya sin duplicados, sin
  las 7 columnas con fuga, sin datos personales, sin columnas constantes, sin identificadores del colegio (salvo
  `cole_cod_dane_sede`, solo para agrupar) y solo con calendario A.
- **Depende de la etapa 3:** `edad` y las versiones numéricas de `fami_estratovivienda`, `fami_personashogar` y
  `fami_cuartoshogar` las crea la limpieza (decisiones 3 y 7). Mientras `03-preprocesamiento.md` siga en borrador, esta
  etapa asume lo que dice ese borrador. «Sin Estrato» quedó resuelto por el grupo el 31 oct 2026 (regla 7b de la etapa 3):
  estrato 1–6 numérico, «Sin Estrato» → vacío (nunca 0) y `sin_estrato` = 1; vacío real → vacío y `sin_estrato` = 0.
- **Objetivo:** `punt_global` (no entra como predictor).

## 2. Columnas base del modelo

Solo variables `cole_`, `estu_` y `fami_` que se conocen **antes** del examen.

| Tipo | Columnas | Nota |
|---|---|---|
| Numéricas | `edad`, `fami_estratovivienda`, `sin_estrato`, `fami_personashogar`, `fami_cuartoshogar` | Las crea la etapa 3 (ordinales como números) |
| Categóricas | `cole_area_ubicacion`, `cole_bilingue`, `cole_caracter`, `cole_genero`, `cole_jornada`, `cole_naturaleza`, `cole_sede_principal`, `estu_genero`, `estu_nacionalidad`, `estu_privado_libertad`, `fami_educacionmadre`, `fami_educacionpadre`, `fami_tieneautomovil`, `fami_tienecomputador`, `fami_tieneinternet`, `fami_tienelavadora` | La educación de los padres queda como categoría para conservar «No sabe» y «No Aplica» (decisión 6) |
| Categóricas de alta cardinalidad | `cole_cod_mcpio_ubicacion` (125 municipios), `estu_cod_reside_mcpio` (173) | Se usan los **códigos**, no los nombres: ver sección 4 |

**Columnas que quedan fuera, y por qué:**

| Columna(s) | Motivo |
|---|---|
| `cole_cod_dane_sede` | Solo para agrupar en la partición y la validación cruzada (decisiones 9 y 10) |
| `cole_calendario` | Tras la decisión 11 solo queda «A»: no aporta información |
| `cole_mcpio_ubicacion`, `estu_mcpio_reside` | Repiten el código del municipio. En residencia hay 172 nombres para 173 códigos («ARMENIA» corresponde a dos municipios distintos) |
| `estu_depto_reside`, `estu_cod_reside_depto` | Ya están contenidos en el código del municipio de residencia |
| `estu_pais_reside` | Es idéntica a `estu_nacionalidad` en el 100 % de los estudiantes |
| `estu_mcpio_presentacion`, `estu_cod_mcpio_presentacion`, `estu_depto_presentacion`, `estu_cod_depto_presentacion` | Lugar donde se presenta el examen: es logística, repite casi siempre el municipio del colegio o de residencia y el usuario de la app no siempre lo sabe |
| `estu_tipodocumento` | Excluida por el grupo (31 oct 2026): su información ya está en la edad, y los documentos de extranjeros funcionarían como indicador de condición migratoria, lo que va contra la condición de equidad |
| `punt_global` | Es el objetivo |
| Las 7 con fuga, `estu_consecutivo`, `estu_fechanacimiento` y los identificadores del colegio | Ya los quita la etapa 3 (decisiones 2, 3 y 9). Una prueba verifica que no reaparezcan |

## 3. Variables nuevas candidatas

Todas usan solo información que se conoce antes del examen. Por defecto quedan **apagadas** (`use_engineered=False`); el
notebook 04 mide si mejoran el MAE con validación agrupada por sede. Si no lo mejoran, se quedan apagadas, como en el ejemplo.

| Variable | Cálculo | Motivo | Vacío cuando… |
|---|---|---|---|
| `n_bienes_hogar` | Número de «Si» entre `fami_tieneautomovil`, `fami_tienecomputador`, `fami_tieneinternet` y `fami_tienelavadora` (0 a 4) | Resume la situación económica del hogar en una sola cifra, menos ruidosa que cada bien por separado | No respondió ninguna de las 4 (2,6 % de los estudiantes) |
| `educacion_max_padres` | Nivel más alto entre madre y padre, en esta escala: Ninguno 0, Primaria incompleta 1, Primaria completa 2, Secundaria incompleta 3, Secundaria completa 4, Técnica o tecnológica incompleta 5, Técnica o tecnológica completa 6, Educación profesional incompleta 7, Educación profesional completa 8, Postgrado 9 | El nivel educativo del hogar suele importar más que el de cada padre por separado | Ninguno de los dos tiene un nivel conocido («No sabe», «No Aplica» o vacío no cuentan) |
| `personas_por_cuarto` | Personas del hogar ÷ cuartos. Personas por punto medio del rango: «1 a 2» → 1,5; «3 a 4» → 3,5; «5 a 6» → 5,5; «7 a 8» → 7,5; «9 o más» → 9. Cuartos: «Uno» → 1 … «Seis o mas» → 6 | Mide el hacinamiento, que afecta el espacio para estudiar | Falta alguno de los dos datos, o hay 0 cuartos (división por cero → vacío, nunca infinito) |
| `vive_en_mcpio_colegio` | 1 si `estu_cod_reside_mcpio` = `cole_cod_mcpio_ubicacion`; si no, 0 (95,4 % vive en el mismo municipio) | Estudiar en otro municipio implica desplazamiento y suele darse en zonas rurales | Falta alguno de los dos códigos |

> **Escala confirmada por el grupo el 31 oct 2026** (técnica o tecnológica completa por debajo de profesional incompleta).
> «No sabe» y «No Aplica» no entran en la escala: siguen como categorías propias (decisión 6).
>
> `personas_por_cuarto` es **aproximada**: las personas vienen en rangos y «Seis o mas» cuartos se toma como 6.

## 4. Preprocesamiento (dentro del `Pipeline`, ajustado solo con entrenamiento)

| Paso | Regla | Motivo |
|---|---|---|
| Numéricas: vacíos | Mediana del entrenamiento **más** una columna indicadora de vacío (`add_indicator=True`) | El vacío es información (decisión 5: ~18 puntos menos en `fami_`). El indicador la conserva. También cubre `edad` < 13 marcada como vacío (decisión 4) |
| Numéricas: escala | Estandarizar (`StandardScaler`), con opción de apagarlo (`scale=False`) para modelos de árboles | Los modelos lineales lo necesitan; los árboles no |
| Categóricas: vacíos | Categoría constante «sin respuesta» | Decisión 5: imputar con la moda borraría la información del vacío |
| Categóricas: centinelas | «No sabe» y «No Aplica» no se tocan: cada uno queda como su propia categoría. «Sin Estrato» llega como la marca `sin_estrato` (regla 7b de la etapa 3) | Decisión 6: tienen puntajes distintos al resto |
| Categóricas: codificación | One-hot. Las categorías con menos del 1 % de los estudiantes (`min_frequency=0.01`) se agrupan en una sola «poco frecuente»; una categoría nunca vista en entrenamiento va a ese mismo grupo (`handle_unknown="infrequent_if_exist"`) | Evita cientos de columnas casi vacías y que el modelo falle con una categoría nueva en la app |
| Municipios (alta cardinalidad) | Mismo one-hot con agrupación de poco frecuentes: con 1 % quedan 16 municipios de colegio y 15 de residencia con columna propia; el resto va a «poco frecuente». El umbral es un parámetro (`min_frequency`) | Con la partición por sede, muchos municipios pequeños tienen pocas sedes y su promedio no se puede aprender con confianza. **[POR DECIDIR]:** si el notebook 04 prueba un umbral menor o una codificación por objetivo (`TargetEncoder`, que debe ir dentro del `Pipeline` para no filtrar el objetivo) |

> Nada de esto se ajusta con el conjunto de prueba (constitución, principio III).

## 5. Entradas y salidas

| | Ruta |
|---|---|
| Entrada | Salida de la etapa 3: `data/processed/train.joblib`, que es lo que lee el notebook 04 (la prueba no se usa aquí) |
| Código | `src/proyecto/features/engineering.py`: `add_features`, `feature_columns`, `build_preprocessor` |
| Pruebas | `tests/test_features.py` |
| Notebook que orquesta | `notebooks/04_features.ipynb` (solo llama a las funciones y mide el MAE) |

> Fuera de esta pieza: `build_pipeline` (`src/proyecto/models/train.py`), que el notebook 04 también necesita para unir el
> preprocesador con un modelo. Se especifica aparte.

## 6. Pruebas que deben existir

- ☐ **`add_features` no modifica la tabla original.**
- ☐ **Divisiones por cero o con datos faltantes dan vacío, no infinito** (`personas_por_cuarto` con 0 cuartos o sin dato).
- ☐ **Cada variable nueva** con un caso normal y un caso con vacíos hecho a mano (`n_bienes_hogar`,
  `educacion_max_padres`, `personas_por_cuarto`, `vive_en_mcpio_colegio`).
- ☐ **`feature_columns` respeta los interruptores:** con `use_engineered=False` no aparece ninguna variable nueva.
- ☐ **El preprocesador no usa columnas con fuga ni identificadores:** ninguna de las 7 columnas con fuga,
  `estu_consecutivo`, `estu_fechanacimiento`, `cole_cod_dane_sede`, los otros identificadores del colegio,
  `estu_tipodocumento` ni `punt_global` está en las columnas que usa.
- ☐ **El preprocesador soporta vacíos y categorías nuevas:** transformar una fila con una categoría nunca vista y con
  vacíos no produce vacíos en la salida.
- ☐ **Los centinelas sobreviven:** «No sabe» en `fami_educacionmadre` termina en su propia columna, distinta de «sin respuesta».
- ☐ `pytest` en verde desde la raíz del repo.

## 7. Criterios de cierre

- ☐ El notebook 04 compara el MAE **con y sin** variables nuevas, con validación cruzada agrupada por sede (`GroupKFold`)
  solo sobre entrenamiento, y deja escrita la decisión (encendidas o apagadas) con su cifra en `reports/`.
- ☐ La decisión se anota en la sección 7 de `especificacion-proyecto.md`.
- ☐ `pytest` en verde.
- ☐ Revisaron el código de Claude con `checklist-revision-ia.md` y con el subagente `auditor-de-fuga`.
- ☐ Todo subido a GitHub.

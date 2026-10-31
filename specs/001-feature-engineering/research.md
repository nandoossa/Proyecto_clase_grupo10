# Research: Variables y preprocesamiento del modelo (etapa 4)

No quedaron `NEEDS CLARIFICATION` en el contexto técnico. Estas son las decisiones de diseño, con su motivo.

## 1. Vacíos en categóricas

- **Decision**: `SimpleImputer(strategy="constant", fill_value="sin respuesta")` antes del one-hot.
- **Rationale**: decisión 5 del EDA. El vacío lleva información (~18 puntos menos en `fami_`; 16 menos en `cole_bilingue`).
- **Alternatives considered**: imputar con la moda (borra la información); dejar vacío para el modelo (no todos los
  modelos del torneo lo aceptan).

## 2. Vacíos en numéricas

- **Decision**: mediana del entrenamiento con `add_indicator=True`.
- **Rationale**: la mediana no se mueve con valores extremos (adultos de más de 60 años en `edad`). El indicador conserva
  la información de «no respondió» de las ordinales `fami_`, y de «edad imposible» (decisión 4).
- **Alternatives considered**: media (sensible a extremos); categoría «sin respuesta» para numéricas (las convertiría en
  texto y perderían el orden de la decisión 7).

## 3. Centinelas («No sabe», «No Aplica», «Sin Estrato»)

- **Decision**: no se transforman. La educación de los padres queda como categoría, así que cada centinela recibe su
  propia columna en el one-hot.
- **Rationale**: decisión 6 del EDA.
- **Alternatives considered**: convertirlos en vacío (contradice la decisión 6).

## 4. Municipios (alta cardinalidad)

- **Decision**: one-hot con `min_frequency=0.01` y `handle_unknown="infrequent_if_exist"`, sobre los **códigos**
  `cole_cod_mcpio_ubicacion` y `estu_cod_reside_mcpio`. Con 1 % quedan 16 municipios de colegio y 15 de residencia con
  columna propia. `min_frequency` es un parámetro de `build_preprocessor`.
- **Rationale**: es la misma técnica del ejemplo y del resto de categóricas, no filtra el objetivo y soporta municipios
  nuevos en la app. Los códigos evitan homónimos: «ARMENIA» tiene dos códigos de residencia.
- **Alternatives considered**: `TargetEncoder` (más compacto, pero usa el objetivo; si se prueba, debe ir dentro del
  `Pipeline` y queda para el notebook 04, fuera de esta pieza); usar los nombres (homónimos).

## 5. Códigos de municipio como categorías

- **Decision**: los códigos se convierten a texto antes del one-hot.
- **Rationale**: son números (`5001`, `5088`…) que pandas lee como enteros. Sin convertirlos, el preprocesador los
  trataría como cantidades, y Medellín (5001) no es «menos» que Bello (5088).
- **Alternatives considered**: dejarlos como enteros (orden sin sentido).

## 6. Divisiones seguras

- **Decision**: una función `_ratio(num, den)` que devuelve vacío cuando el denominador es 0 o falta, como en el ejemplo.
- **Rationale**: FR-004; los modelos lineales fallan con infinitos.

## 7. Variables nuevas sobre la salida de la etapa 3

- **Decision**: `personas_por_cuarto` usa las versiones **numéricas** de la etapa 3 (personas 1–5, cuartos 1–6) y
  traduce el código de personas a punto medio del rango (1 → 1,5; 2 → 3,5; 3 → 5,5; 4 → 7,5; 5 → 9).
  `educacion_max_padres` y `n_bienes_hogar` usan el texto original de las columnas `fami_`, que la etapa 3 no cambia.
- **Rationale**: `add_features` recibe la tabla ya limpia; así no depende del texto de personas y cuartos.
- **Riesgo**: si la etapa 3 cambia la codificación de la decisión 7, hay que ajustar el mapeo. Una prueba lo detecta.

## Versiones

Python 3.12.10, pandas 3.0.6, scikit-learn 1.9.1 (instaladas y fijadas en `requirements.txt`). `infrequent_if_exist` y
`min_frequency` existen desde scikit-learn 1.1.

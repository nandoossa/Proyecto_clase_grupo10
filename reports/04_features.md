# Informe de variables

> Resultado de `notebooks/04_features.ipynb` (ejecutado el 31 oct 2026; las cifras se copian de su salida). Cada idea de variable es una
> **hipótesis medida** con la misma validación; se conserva solo si la mejora supera el ruido entre
> pliegues. Guía: `material-del-curso/kit/guia-modelado-y-optimizacion.md`, sección 1.

## Cómo se midió

<!-- Modelo con parámetros fijos, métrica principal y de control, número y tipo de pliegues
     (por qué entidad se parte), semilla. Los MISMOS pliegues para todas las variantes. -->

- **Modelo (parámetros fijos):** `HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=31,
  early_stopping=False, random_state=42)`, el boosting del torneo con sus parámetros de partida (equivalentes a LightGBM del
  ejemplo). Dentro de `build_pipeline` (preprocesamiento de la etapa 4 + modelo), ajustado solo con el entrenamiento de
  cada pliegue. Solo cambia el conjunto de variables (`extra_numeric`) o el umbral `min_frequency`.
- **Métrica principal** (y por qué): MAE en puntos, en positivo. Es la métrica del caso: los dos errores cuestan lo mismo
  y el costo crece en proporción a los puntos de error (`especificacion-proyecto.md`, sección 4).
- **Métricas de control:** RMSE y R² (`scoring()` de `train.py`). Se calcularon en la misma validación cruzada, pero la
  tabla del notebook solo muestra el MAE, que es el que decide.
- **Pliegues** (cuántos y partidos por qué entidad): 5 pliegues con `GroupKFold` agrupados por sede
  (`cole_cod_dane_sede`), calculados una sola vez y reutilizados en todas las variantes; el notebook comprueba que
  ninguna sede está en los dos lados de un pliegue. `GroupKFold` no baraja, así que los pliegues son siempre los mismos;
  la semilla 42 es la del modelo. Datos: 57.286 estudiantes de entrenamiento (la prueba no se abrió).
- **Regla de decisión escrita antes de medir:** se conserva una idea solo si **mejora / ruido > 1** y se conoce al
  predecir. Si ninguna la cumple, las variables nuevas quedan apagadas (`use_engineered=False`) y el umbral queda en 1 %.
  Mejora = MAE de la referencia − MAE de la variante (positivo: la variante mejora); ruido = desviación del MAE de la
  variante entre los 5 pliegues.

## Tabla de ideas medidas

> La fila 0 es la **referencia** (las variables actuales). "Mejora / ruido" = mejora de la métrica
> principal dividida por su desviación entre pliegues; menor que ~1 está dentro del ruido.

| # | Idea (variable y cómo se calcula) | ¿Se conoce al predecir? | Métrica (± ruido) | Mejora / ruido | Decisión |
|---|---|---|---|---|---|
| 0 | **Referencia**: variables base, umbral de poco frecuentes `min_frequency` = 1 % | — | 33,563 (± 0,244) | 0 | — |
| 1 | `n_bienes_hogar`: número de «Si» entre automóvil, computador, internet y lavadora (0 a 4) | ☒ sí ☐ no | 33,566 (± 0,256) | −0,01 | ☐ conservar ☒ descartar |
| 2 | `educacion_max_padres`: nivel más alto entre madre y padre (escala 0–9 del grupo) | ☒ sí ☐ no | 33,614 (± 0,279) | −0,18 | ☐ conservar ☒ descartar |
| 3 | `personas_por_cuarto`: punto medio de personas del hogar ÷ cuartos | ☒ sí ☐ no | 33,548 (± 0,269) | 0,06 | ☐ conservar ☒ descartar |
| 4 | `vive_en_mcpio_colegio`: 1 si el municipio de residencia es el del colegio | ☒ sí ☐ no | 33,562 (± 0,229) | 0,01 | ☐ conservar ☒ descartar |
| 5 | Las 4 variables anteriores juntas | ☒ sí ☐ no | 33,579 (± 0,277) | −0,06 | ☐ conservar ☒ descartar |
| 6a | Umbral de poco frecuentes `min_frequency` = 0,5 % (aplica a todas las categóricas) | ☒ sí ☐ no | 33,503 (± 0,230) | 0,26 | ☐ conservar ☒ descartar |
| 6b | Umbral de poco frecuentes `min_frequency` = 0,1 % (aplica a todas las categóricas) | ☒ sí ☐ no | 33,390 (± 0,226) | 0,77 | ☐ conservar ☒ descartar |

MAE en puntos (media de los 5 pliegues por sede); «± ruido» es la desviación entre pliegues.

## Decisiones y motivos

<!-- Una línea por idea: qué decidiste, con qué cifra y por qué. Las ideas descartadas se anotan
     igual: documentan lo que ya probaste. -->

- **Escala de educación de los padres (grupo, 31 oct 2026, antes de medir):** para `educacion_max_padres` se usa
  Ninguno 0, Primaria incompleta 1, Primaria completa 2, Secundaria incompleta 3, Secundaria completa 4, Técnica o
  tecnológica incompleta 5, Técnica o tecnológica completa 6, Educación profesional incompleta 7, Educación profesional
  completa 8, Postgrado 9. «No sabe» y «No Aplica» no entran en la escala: siguen como categorías propias en
  `fami_educacionmadre` y `fami_educacionpadre` (decisión 6 del EDA). Motivo: una escala ordenada permite tomar el nivel
  más alto del hogar; ubicar «técnica completa» por debajo de «profesional incompleta» es una convención del grupo.
- **`estu_tipodocumento` se excluye como predictor (grupo, 31 oct 2026, antes de medir).** Motivo: su información ya está
  en la edad (TI frente a CC), y los documentos de extranjeros (PEP, PPT, CE…) funcionarían como indicador de condición
  migratoria, lo que va contra la condición de equidad.
- **`estu_nacionalidad` y `estu_privado_libertad` se excluyen como predictores (grupo, 31 oct 2026, antes de medir).**
  Motivo: la nacionalidad es indicador de condición migratoria y estar privado de la libertad es un dato sensible
  (además, el 99,8 % responde «N»); mismo criterio de equidad con el que se excluyó `estu_tipodocumento`.
- **Municipios (grupo, 31 oct 2026):** el notebook 04 prueba otros umbrales de agrupación de poco frecuentes. Si se
  prueba `TargetEncoder`, va dentro del `Pipeline` y se compara solo con validación agrupada por sede, porque su
  validación cruzada interna no respeta la agrupación. En este notebook no se probó `TargetEncoder`; solo los umbrales
  0,5 % y 0,1 %.
- **Variables nuevas apagadas (`use_engineered=False`).** Ninguna de las cuatro supera la regla: `n_bienes_hogar` −0,01
  (el MAE sube 0,003 puntos), `educacion_max_padres` −0,18 (sube 0,05), `personas_por_cuarto` 0,06 (baja 0,015),
  `vive_en_mcpio_colegio` 0,01 (baja 0,001) y las 4 juntas −0,06. La información que resumen (bienes, educación del
  hogar, hacinamiento, municipio) ya está en las columnas base.
- **Umbral `min_frequency` = 1 %.** 0,5 % mejora 0,06 puntos (0,26 veces el ruido) y 0,1 % mejora 0,17 puntos (0,77 veces
  el ruido): ninguno llega a 1, así que se mantiene el 1 %. **El 0,1 % queda como candidato** para probarse como
  hiperparámetro en la etapa 6 (optimización), porque es la mejora más grande y va en la dirección esperada (más
  municipios con columna propia).

## Supuestos y riesgos

<!-- Variables que solo valen si cierto dato se conoce al momento de decidir; riesgos de fuga;
     lo que complicaría la app si se conserva. -->

- Todas las ideas usan solo columnas de la misma fila que se conocen antes del examen; `add_features` no aprende nada de
  los datos, así que calcularla una vez fuera de los pliegues no filtra información. La imputación, el escalado y el
  one-hot sí aprenden, y van dentro del `Pipeline`.
- Las diferencias medidas son muy pequeñas (menos de 0,2 puntos de MAE frente a un ruido de ~0,23–0,28): otra semilla o
  otros pliegues podrían cambiar el orden entre variantes. Por eso la regla exige mejora / ruido > 1.
- Bajar el umbral a 0,1 % aumenta las columnas del one-hot en todas las categóricas, no solo en municipios: si se adopta en
  la etapa 6, revisar que la app no reciba categorías raras que el modelo trate de forma inestable.
- Al no conservar variables nuevas, la app no tiene que calcularlas: pide solo las columnas base.

## Qué se lleva el pipeline final

<!-- La lista final de variables, y dónde está el código (`src/<paquete>/features/`). -->

- **Numéricas (5):** `edad`, `fami_estratovivienda`, `sin_estrato`, `fami_personashogar`, `fami_cuartoshogar` (imputación
  con la mediana + indicador de vacío; escaladas solo para Ridge).
- **Categóricas (14):** `cole_area_ubicacion`, `cole_bilingue`, `cole_caracter`, `cole_genero`, `cole_jornada`,
  `cole_naturaleza`, `cole_sede_principal`, `estu_genero`, `fami_educacionmadre`, `fami_educacionpadre`,
  `fami_tieneautomovil`, `fami_tienecomputador`, `fami_tieneinternet`, `fami_tienelavadora` (vacíos → «sin respuesta»;
  one-hot con poco frecuentes < 1 % agrupadas).
- **Códigos de municipio (2, como categóricas):** `cole_cod_mcpio_ubicacion`, `estu_cod_reside_mcpio`.
- **Configuración:** `build_pipeline(modelo, use_engineered=False, min_frequency=0.01)`. `cole_cod_dane_sede` llega al
  `Pipeline` solo para agrupar y el preprocesador la descarta.
- **Código:** `src/proyecto/features/engineering.py` (`build_preprocessor`, `add_features`, listas de columnas) y
  `src/proyecto/models/train.py` (`build_pipeline`).

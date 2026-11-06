# Especificación · Etapa 8 · Registro del modelo, exportación y esquema de entrada

> Se llena **antes** de escribir código, a partir de `reports/07_validacion.md`, `reports/07_metricas_test.json` y la guía
> `material-del-curso/kit/guia-validacion-registro-y-app.md` (secciones 5 a 8). Claude la lee y la implementa; ustedes
> revisan que el código haga **exactamente** esto.

**Grupo:** Predictor de resultados Pruebas Saber 11 en Antioquia   **Fecha:** 5 nov 2026   **Estado:** ☒ borrador (decisiones del grupo del 5 nov 2026 incorporadas)  ☐ cerrada

> Borrador preparado por Claude a partir del pedido del grupo del 5 nov 2026. Ninguna cifra del registro (versión, nombre
> completo) está escrita: salen de la ejecución.

## 1. Entrada

- `models/final_pipeline.joblib`: el pipeline evaluado en la etapa 7. Su huella SHA-256 está en `reports/prueba_huellas.json`
  y se verifica antes de registrarlo. Si no existe en el equipo, el notebook se detiene.
- `reports/07_metricas_test.json` y `reports/07_decisiones_congeladas.json`.
- `data/processed/train.joblib`: **solo** para el ejemplo de entrada, la firma, la comprobación de ida y vuelta y el esquema.

## 2. Registro en MLflow (Unity Catalog)

| Qué | Valor |
|---|---|
| Conexión | `configure_mlflow()`; el notebook confirma que dice «databricks» (si dice «local», se detiene y avisa) |
| Experimento | `saber11-modelo-final` |
| Nombre | `registered_model_name("saber11_puntaje_global")` → `<catálogo>.<esquema>.saber11_puntaje_global` (catálogo y esquema de `.env`) |
| Formato | `serialization_format="cloudpickle"` (un `Pipeline` completo; el formato por defecto lo rechaza) |
| Parámetros | Los de `07_decisiones_congeladas.json` (modelo, 8 hiperparámetros, fijos) |
| Métricas | MAE, RMSE y R² de la prueba, con su intervalo del 95 % por sedes (límites inferior y superior), y los de la línea base |
| Firma y ejemplo de entrada | **Solo las 21 columnas del modelo** (`model_columns()`): sin `cole_cod_dane_sede`, sin identificadores, sin columnas prohibidas y sin `punt_global`. Ejemplo de 5 filas y firma con 200 filas, **del entrenamiento** |
| Etiquetas | `etapa=08_registro`, fecha de registro, commit de Git, fecha de las decisiones congeladas y de la apertura de la prueba, `unidad_de_particion=cole_cod_dane_sede` |
| Alias | `champion` sobre la versión registrada |
| Ida y vuelta | Cargar `models:/<nombre>@champion` y comprobar que predice **exactamente** lo mismo que el original (igualdad exacta) en 500 filas del entrenamiento |

## 3. Exportación y esquema

- `models/model.joblib`: se exporta **desde la versión `champion`** del registro (el registro es la fuente de verdad).
- `models/input_schema.json`, calculado **solo con el entrenamiento**: las 21 columnas, su tipo (numérica / categórica),
  valores válidos de cada categórica, rango observado y mediana de cada numérica, y rango **válido** (lo posible):

| Columna | Rango válido (fuera → se rechaza) | Motivo |
|---|---|---|
| `edad` | 13 a 80 | El rango visto en el entrenamiento (decisión del grupo, 5 nov 2026); menos de 13 es imposible (decisión 4 del EDA) |
| `fami_estratovivienda` | 1 a 6 | Escala de estratos |
| `sin_estrato` | 0 a 1 | Marca |
| `fami_personashogar` | 1 a 5 | Códigos de la etapa 3 |
| `fami_cuartoshogar` | 1 a 6 | Códigos de la etapa 3 |

- **Vacíos (decisión del grupo, 5 nov 2026):** los campos que tenían vacíos en el entrenamiento aceptan «sin respuesta»
  (vacío) en lugar de rechazarse, porque el modelo aprendió a usar esa ausencia; los que nunca tuvieron vacíos lo rechazan.
  `input_schema.json` dice qué campos admiten vacío (`nullable`).
- **Categorías nuevas (decisión del grupo):** se **rechazan** en las 14 categóricas de lista cerrada; en los 2 códigos de
  municipio solo se **advierte** (el modelo los agrupa como «poco frecuente»).
- Ninguno de los dos archivos está en `.gitignore` (comprobado: no lo están); se suben al repositorio para la app.

## 4. Comprobar que el exportado es el evaluado (sin volver a evaluar con la prueba)

**Opción A (decisión del grupo, 5 nov 2026): no se vuelve a predecir sobre la prueba.**
1. La huella SHA-256 de `final_pipeline.joblib` coincide con la de `reports/prueba_huellas.json` (el modelo que produjo las
   predicciones de la prueba).
2. `models/model.joblib` (exportado desde `champion`) predice **exactamente** igual que `final_pipeline.joblib` en las
   57.286 filas del entrenamiento.
3. El MAE 33,316 se recalcula con las predicciones y etiquetas ya guardadas en `data/processed/prueba_resultados.joblib`.

## 5. Inferencia (`src/proyecto/inference/`)

- `schema.py` y `predict.py` son la plantilla de **clasificación**. Se adaptan a regresión:
  - el esquema admite regresión (sin clases ni matriz de costos);
  - una función de predicción de regresión devuelve el puntaje estimado;
  - valida contra el esquema: **rechaza** columnas faltantes, valores no numéricos, valores fuera del rango válido,
    vacíos en campos que no los admiten y categorías nuevas en las listas cerradas; **advierte** en municipios no vistos;
  - la función nueva `predict_score` devuelve la columna `puntaje_estimado`, sin redondear ni recortar (decisión del grupo);
  - las funciones de clasificación de la plantilla (`predict_with_scores`, `decide_min_cost`) se conservan hasta la
    etapa 9 y **se quitarán allí**, cuando la app se adapte a regresión.
- **Mediana de `schema.py:77`** (auditoría de la etapa 3): `build_schema` la calcula con la tabla que recibe, que en el
  notebook es **solo el entrenamiento**; se guarda en el esquema para la app y **nunca** se calcula al predecir. Una prueba
  lo verifica.

## 6. Ficha e informe

- `models/ficha_modelo.md`: qué predice, para quién, datos, MAE en la prueba con su intervalo, resultados por segmento,
  límites (estrato 5 con MAE 39,57; brecha de 4,34 puntos entre hombres y mujeres; R² 0,363) y uso responsable (orienta, no
  excluye). Solo cifras de los reportes.
- `reports/08_registro.md` y `reports/08_registro.json`, sin correos, direcciones del espacio de trabajo ni tokens.

## 7. Pruebas que deben existir

- ☐ El esquema de regresión se guarda y se recarga, con las 21 columnas, sus categorías y rangos.
- ☐ La mediana del esquema sale solo de la tabla que se le pasa, y `predict` no calcula nada de los datos que recibe.
- ☐ `predict` de regresión: rechaza una columna faltante, un valor fuera del rango válido y uno no numérico; acepta una fila
  con vacíos; devuelve un número por fila.
- ☐ Con una fila real del entrenamiento y el modelo exportado, la predicción es un número en un rango plausible.
- ☐ `pytest` en verde.

## 8. Criterios de cierre

- ☐ Modelo registrado con versión y alias `champion` en Databricks; ida y vuelta exacta.
- ☐ `models/model.joblib` exportado desde `champion` y `models/input_schema.json` escritos; ninguno ignorado por Git.
- ☐ Comprobación de que el exportado es el evaluado.
- ☐ Ficha del modelo e informe completos; documentación general actualizada (regla 10 de `CLAUDE.md`).
- ☐ Auditoría con `auditor-de-fuga` en `reports/auditoria_etapa8.md`.
- ☐ Sin correos, direcciones del espacio de trabajo, tokens ni enlaces «View run» en lo que se sube.
- ☐ Todo subido a GitHub.
- ☐ Revisión del código de Claude por el grupo con `material-del-curso/kit/checklist-revision-ia.md`.

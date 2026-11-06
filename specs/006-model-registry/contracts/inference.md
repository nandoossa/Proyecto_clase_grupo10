# Contrato: `src/proyecto/inference/` (extensión a regresión)

| Función | Firma | Devuelve / hace |
|---|---|---|
| `build_schema` | `build_schema(df, numeric, categorical, class_names=None, cost_matrix=None, valid_range=None, labels=None, review_threshold=0.55, path=None, task="classification", warn_only_categories=None)` | Con `task="regression"` no exige clases. Guarda `task`, `numeric`, `categorical`, `categories` (valores válidos), `observed_range`, `median` e `integer_columns` calculados **solo con `df`**, `valid_range`, `warn_only_categories` y `nullable` (columnas con vacíos en `df`) |
| `validate_inputs` | `validate_inputs(df, schema) -> list[str]` | Error si falta una columna, si una numérica no es número o está fuera de `valid_range`, si hay un vacío en una columna que no está en `nullable`, y si una categórica de lista cerrada trae un valor no válido; advertencias para lo fuera del rango observado y para las categorías de `warn_only_categories` no vistas |
| `predict_score` | `predict_score(df, model, schema) -> pd.DataFrame` | Valida y devuelve `puntaje_estimado` (una fila por fila de entrada); advertencias en `attrs["warnings"]`. No calcula nada a partir de `df` |
| `predict_with_scores`, `decide_min_cost` | (sin cambios) | Clasificación de la plantilla; se conservan hasta la etapa 9 y se quitarán allí |

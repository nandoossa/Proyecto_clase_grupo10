# Contrato: `src/proyecto/models/evaluation.py`

| Función | Firma | Devuelve |
|---|---|---|
| `stratum_segment` | `stratum_segment(df) -> pd.Series` | «Estrato 1» … «Estrato 6», «Sin Estrato» (`sin_estrato` = 1), «Sin dato (vacío)» (vacío y `sin_estrato` = 0) |
| `equity_segments` | `equity_segments(df) -> pd.DataFrame` | columnas `estrato`, `zona` (`cole_area_ubicacion`), `naturaleza` (`cole_naturaleza`), `genero` (`estu_genero`); vacío → «Sin dato (vacío)» |
| `bootstrap_metric_difference` | `bootstrap_metric_difference(y_true, pred_a, pred_b, groups, metric_fn, n_boot=1000, seed=42) -> (diff, low, high)` | métrica(A) − métrica(B) e intervalo 95 % remuestreando sedes (mismas sedes para A y B en cada remuestreo) |
| `equity_table` | `equity_table(y_true, pred_model, pred_base, segments, groups, n_boot=1000, seed=42) -> pd.DataFrame` | una fila por (variable, segmento): `estudiantes`, `sedes`, `mae_modelo`, `mae_linea_base`, `diferencia`, `ic_inf`, `ic_sup`, `cumple` (bool: `mae_modelo < mae_linea_base`), `veredicto` («cumple con ventaja clara» si además `ic_sup < 0`; «cumple sin ventaja concluyente» si cumple y el intervalo incluye el cero; «no cumple») |
| `permutation_importance_table` | `permutation_importance_table(pipeline, X, y, columns, n_repeats=5, seed=42) -> pd.DataFrame` | por columna: `aumento_mae` (media), `desviacion`; ordenada de mayor a menor |
| `model_columns` | `model_columns() -> list[str]` | las columnas originales que usa el preprocesador (numéricas + categóricas, sin la sede) |

Los MAE salen en puntos y en positivo.

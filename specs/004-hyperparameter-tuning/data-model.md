# Data model: Optimización

| Entidad | Campos | Reglas |
|---|---|---|
| Parte de búsqueda | filas de `train.joblib` (~75 % de las sedes) | ninguna sede en la reserva |
| Sedes reservadas | filas de `train.joblib` (~25 % de las sedes, semilla 7) | la búsqueda nunca las ve; solo para la comprobación |
| Ensayo | número, parámetros, `mae`, `rmse`, `r2` (media y desviación entre 3 pliegues), `fit_seconds` | una ejecución anidada en MLflow por ensayo |
| Medición de partida | parámetros de `candidates()`, mismas métricas | mismos pliegues que los ensayos |
| Comprobación | modelo, MAE partida y optimizado en la reserva (con IC 95 %), diferencia e IC 95 %, RMSE, R², decisión | IC remuestreando sedes; regla escrita antes |
| `06_best_params.json` | por modelo: parámetros elegidos, MAE de la búsqueda, MAE de partida, run id madre, dónde quedó el tracking, número de ensayos y minutos | se sube a Git |

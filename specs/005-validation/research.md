# Research: Validación final

## 1. Interpretación: permutación y no SHAP

- **Decision**: `sklearn.inspection.permutation_importance` sobre el `Pipeline` completo, con `neg_mean_absolute_error`, 5
  repeticiones, semilla 42, permutando las 21 columnas originales que usa el preprocesador.
- **Rationale**: es lo pedido; se lee en puntos de MAE («si desordeno esta columna, el error sube N puntos»); al permutar la
  columna original, el one-hot de un municipio cuenta como una sola variable. SHAP con `HistGradientBoostingRegressor` y
  one-hot daría importancias por columna codificada, más difíciles de explicar.
- **Alternatives considered**: SHAP (`shap` está en `requirements.txt`): queda como opción para explicar casos individuales
  en la app.

## 2. Intervalos

- **Decision**: MAE con `tuning.bootstrap_metric_ci` y diferencia de MAE con `tuning.bootstrap_mae_difference` (ya probadas);
  RMSE y R² y sus diferencias con una función nueva genérica `bootstrap_metric_difference` (mismos índices de sede para A y
  B en cada remuestreo). 1.000 remuestreos, semilla 42.
- **Rationale**: los estudiantes de una sede no son independientes.

## 3. Apertura única

- **Decision**: decisiones a `reports/07_decisiones_congeladas.json` (fecha y hora) → marca `reports/prueba_abierta.txt` →
  predicciones de modelo y línea base e importancias a `data/processed/prueba_resultados.joblib`. Si la marca y el archivo
  existen, el notebook reutiliza; si existe la marca sin el archivo, se detiene con error (habría que declararlo).
- **Rationale**: patrón del ejemplo; permite re-ejecutar el notebook sin «mirar otra vez».

## 4. Equidad

- **Decision**: regla de `reports/00_caso.md`: cumple si MAE modelo < MAE línea base en el segmento (estricto). Intervalo de
  la diferencia por sedes como información. Género con la misma regla.
- **Rationale**: escrita antes de ver la prueba; el intervalo muestra si la ventaja se distingue del ruido en segmentos
  chicos (estrato 6, «Sin Estrato»).
- **Nota**: la línea base del caso (`reports/00_caso.md`) usó la mediana global 242 sobre los 72.383 estudiantes; aquí la
  línea base es la mediana del entrenamiento evaluada en la prueba, que es la comparación justa.

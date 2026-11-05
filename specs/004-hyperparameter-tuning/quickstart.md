# Quickstart: comprobar la etapa 6

Desde la raíz del repositorio, con el entorno activado y `PYTHONUTF8=1`:

1. **Pruebas:** `python -m pytest tests/test_tuning.py -q` → todas pasan (espacios válidos, bootstrap por sede, reserva sin
   sedes compartidas, reanudación del estudio).
2. **Notebook:** ejecutar `notebooks/06_optimizacion.ipynb` de principio a fin. Debe imprimir: dónde quedó MLflow
   (`databricks (...)` o `local`), sedes de búsqueda y reservadas (0 en común), el MAE de partida y el mejor de cada
   búsqueda, los minutos que tardó y la tabla de comprobación con intervalos.
3. **Tracking:** `mlflow ui --backend-store-uri sqlite:///mlflow_local.db` (si quedó local) → experimento
   `saber11-optimizacion` con `optuna-hist gradient boosting` (25 ensayos anidados + partida) y `optuna-xgboost` (30 + partida).
4. **Reanudación:** volver a ejecutar la celda de la búsqueda → dice que el estudio ya tiene todos los ensayos y no corre más.
5. **Salidas:** `reports/06_best_params.json` y `reports/06_comprobacion.csv` existen; `reports/06_optimizacion.md` usa sus cifras.

# Quickstart: comprobar train.py

1. No hay requisitos de instalación extra: LightGBM se reemplazó por `HistGradientBoostingRegressor` de scikit-learn.

2. Pruebas:

   ```bash
   PYTHONUTF8=1 python -m pytest tests/test_models.py -v
   PYTHONUTF8=1 python -m pytest tests
   ```

   **Esperado:** todo en verde.

3. En el notebook 04 o 05, la importación `from proyecto.models.train import build_pipeline` deja de imprimir el «TODO».

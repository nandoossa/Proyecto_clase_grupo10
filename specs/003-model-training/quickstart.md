# Quickstart: comprobar train.py

1. LightGBM carga (requiere el Visual C++ Redistributable x64 en Windows):

   ```bash
   python -c "import lightgbm; print(lightgbm.__version__)"
   ```

   **Esperado:** `4.7.0`.

2. Pruebas:

   ```bash
   PYTHONUTF8=1 python -m pytest tests/test_models.py -v
   PYTHONUTF8=1 python -m pytest tests
   ```

   **Esperado:** todo en verde.

3. En el notebook 04 o 05, la importación `from proyecto.models.train import build_pipeline` deja de imprimir el «TODO».

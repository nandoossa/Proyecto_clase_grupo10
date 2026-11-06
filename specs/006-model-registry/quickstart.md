# Quickstart: comprobar la etapa 8

1. `python -m pytest tests/test_inference.py -q` → todas pasan.
2. Ejecutar `notebooks/08_registro_modelo.ipynb`: debe decir `MLflow: databricks (...)`, el nombre y la versión registrados,
   «alias champion → versión N», la ida y vuelta exacta y la comprobación de que el exportado es el evaluado (MAE 33,316).
3. `models/model.joblib` y `models/input_schema.json` existen y `git check-ignore` no los ignora.
4. En Databricks, el modelo `saber11_puntaje_global` tiene el alias `champion`.

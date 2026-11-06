# Quickstart: comprobar la etapa 7

Desde la raíz, con el entorno activado y `PYTHONUTF8=1`:

1. `python -m pytest tests/test_evaluation.py -q` → todas pasan.
2. Ejecutar `notebooks/07_validacion_interpretacion.ipynb`. Debe imprimir las decisiones congeladas con fecha **antes** de
   «Prueba abierta ahora», luego métricas con intervalo, metas, tabla de equidad e importancias.
3. `reports/prueba_abierta.txt` existe con fecha y hora; volver a ejecutar el notebook dice «La prueba ya se abrió… se
   reutilizan sus resultados».
4. `reports/07_validacion.md` usa las cifras de `reports/07_metricas_test.json`, `07_equidad.csv` y `07_importancia.csv`.

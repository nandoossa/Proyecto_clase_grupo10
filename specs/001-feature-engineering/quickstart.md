# Quickstart: comprobar la etapa 4

## Requisitos

- Entorno con `requirements.txt` instalado (Python 3.12).
- No hace falta `data/processed/`: las pruebas usan tablas hechas a mano.

## Pasos

1. Desde la raíz del repositorio:

   ```bash
   PYTHONUTF8=1 pytest tests/test_features.py -v
   ```

   **Resultado esperado:** todas las pruebas en verde (ver lista en `tasks.md`).

2. Toda la suite:

   ```bash
   PYTHONUTF8=1 pytest
   ```

   **Resultado esperado:** verde, sin romper las pruebas existentes (`test_data_load.py`, `test_inference.py`,
   `test_tracking.py`).

3. Revisión: pasar el subagente `auditor-de-fuga` sobre `src/proyecto/features/engineering.py` y revisar con
   `material-del-curso/kit/checklist-revision-ia.md`.

## Después (fuera de esta pieza)

Cuando exista `data/processed/train.joblib` (etapa 3) y `build_pipeline` (`src/proyecto/models/train.py`), el notebook 04
compara el MAE con `use_engineered=False` y `True` sobre los mismos 5 pliegues agrupados por sede.

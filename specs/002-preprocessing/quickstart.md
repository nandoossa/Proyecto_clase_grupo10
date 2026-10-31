# Quickstart: comprobar la etapa 3

## Requisitos

- Entorno con `requirements.txt` instalado (Python 3.12).
- `data/raw/saber11_antioquia_2022.csv` (si falta, `load_raw_saber11` lo descarga de datos.gov.co).

## Pasos

1. Pruebas de la etapa (no necesitan los datos reales):

   ```bash
   PYTHONUTF8=1 python -m pytest tests/test_cleaning.py tests/test_split.py -v
   ```

   **Esperado:** todo en verde.

2. Todas las pruebas del proyecto:

   ```bash
   PYTHONUTF8=1 python -m pytest tests
   ```

   **Esperado:** verde (hoy hay 32; se suman las de esta etapa).

3. Regenerar desde cero: borrar `data/processed/` y ejecutar `notebooks/03_preprocesamiento.ipynb` de principio a fin.

   **Esperado:** antes 144.766 filas × 51 → después 72.148 × 36; todas las comprobaciones en `True`; 0 sedes compartidas;
   `data/processed/train.joblib` y `test.joblib` creados.

4. `git status`: `data/raw/` y `data/processed/` no aparecen (ignorados).

5. Revisión: `auditor-de-fuga` sobre `src/proyecto/data/` y el notebook 03; `checklist-revision-ia.md`.

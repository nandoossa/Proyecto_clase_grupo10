# Implementation Plan: Limpieza y partición de los datos (etapa 3)

**Branch**: `002-preprocessing` (trabajo en `main`) | **Date**: 2026-10-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-preprocessing/spec.md` y `especificaciones/03-preprocesamiento.md` (cerrada)

## Summary

Crear `src/proyecto/data/cleaning.py` (una función por regla aprobada y `clean(df)` que las aplica en orden) y
`src/proyecto/data/split.py` (`split_by_group` con `GroupShuffleSplit` 20 % por sede, semilla 42; verificación de sedes
disjuntas; `group_cv` con `GroupKFold`), con la estructura del ejemplo de CreditSight. Completar
`notebooks/03_preprocesamiento.ipynb` para que solo orqueste y guarde `data/processed/train.joblib` y `test.joblib`.
La salida (72.148 filas × 36 columnas) coincide con lo que espera `engineering.py`; una prueba lo verifica.

## Technical Context

**Language/Version**: Python 3.12.10

**Primary Dependencies**: pandas 3.0.6, numpy 2.5.4, scikit-learn 1.9.1, joblib 1.6.0 (fijadas en `requirements.txt`)

**Storage**: archivos: entrada `data/raw/` (solo lectura); salida `data/processed/*.joblib` (ignorada por git)

**Testing**: pytest 9.1.1 con tablas hechas a mano; el notebook se valida con los datos reales

**Target Platform**: Windows local del grupo

**Project Type**: librería interna (`src/proyecto/data/`) + notebook orquestador

**Performance Goals**: limpiar 144.766 filas en segundos (no crítico)

**Constraints**: `data/raw/` nunca se modifica; nada de imputación aquí (va en el `Pipeline` de la etapa 4)

**Scale/Scope**: 2 módulos (~150 líneas), 2 archivos de pruebas (~16 pruebas), 1 notebook

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | ¿Cumple? | Cómo |
|---|---|---|
| I. Los datos originales no se tocan | ✅ | `clean` trabaja sobre copias; solo se escribe en `data/processed/` |
| II. Se parte por la unidad de análisis | ✅ | `GroupShuffleSplit` y `GroupKFold` por `cole_cod_dane_sede`; prueba que falla si una sede cae a los dos lados |
| III. La prueba se abre una sola vez | ✅ | Sin imputación ni escalado aquí; el notebook guarda la prueba sin mirarla (solo cuenta filas) |
| IV. Cada decisión con su motivo | ✅ | Reglas y motivos en `especificaciones/03-preprocesamiento.md`; una función y una prueba por regla |
| V. Nada sensible sale del equipo | ✅ | Personales eliminados en `clean`; `data/processed/` pasa a `.gitignore`; pruebas con datos inventados |
| VI. El código es nuestro | ✅ | Estructura del ejemplo; español en textos, inglés en nombres; revisión con checklist y `auditor-de-fuga` |
| VII. No se inventan datos | ✅ | Cifras verificadas en `data/raw/` el 31 oct 2026 (ver `research.md`) |

**Aviso (igual que en la etapa 4):** la constitución sigue con campos `[entre corchetes]` sin llenar.

**Re-check post-diseño:** sin violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/002-preprocessing/
├── plan.md
├── research.md
├── data-model.md        # columnas de salida y compatibilidad con la etapa 4
├── quickstart.md
├── contracts/
│   └── data.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/proyecto/data/
├── __init__.py              # ya existe
├── load.py                  # ya existe (no se cambia)
├── cleaning.py              # NUEVO
└── split.py                 # NUEVO

tests/
├── test_cleaning.py         # NUEVO
└── test_split.py            # NUEVO

notebooks/03_preprocesamiento.ipynb   # se completa (hoy es plantilla)
data/processed/.gitkeep               # NUEVO
.gitignore                            # se agrega data/processed/*
```

**Structure Decision**: estructura obligatoria de `CLAUDE.md`. No se toca `src/proyecto/features/` (etapa 4).

## Diferencias con la especificación que conviene aprobar

1. **Formato de salida:** `train.joblib` / `test.joblib` en vez de `train.csv` (o `.parquet`). Motivo: es lo que escribe la
   plantilla del notebook 03 y lo que lee el notebook 04; conserva los tipos. Si se aprueba, se corrige la sección 5 de
   `03-preprocesamiento.md`.
2. **`.gitignore`:** se agrega `data/processed/*`. Hoy esa carpeta se subiría a GitHub.
3. **Nombre de la función de partición:** `split_by_group` (lo pide la plantilla del notebook), no `split_by_customer`.

## Riesgos

- El notebook 03 de la plantilla comprueba «no se perdieron filas» (`len(clean_df) == len(df)`); aquí sí se pierden filas a
  propósito (duplicados y calendario «OTRO»). Se reemplaza por las cifras esperadas.
- La prueba de la sección 6 de la especificación «falla si se cambia temporalmente a partición por fila» la hace el grupo
  a mano; además se agrega una prueba automática que muestra que una partición por fila comparte sedes.

## Complexity Tracking

Sin violaciones de la constitución: no aplica.

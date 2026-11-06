# Revisión del grupo (etapas 1 a 9)

> Revisión del código generado con IA usando `material-del-curso/kit/checklist-revision-ia.md`. Fechas: **5 nov 2026** (etapas 1 a 5) y **6 nov 2026** (etapas 6 a 9).

## Asignación

Cada integrante revisó una pieza con el checklist y sabe explicar qué hace y por qué.

| Pieza | Revisó y sabe explicar |
|---|---|
| `src/proyecto/data/cleaning.py` | Jennifer Alejandra López Sánchez |
| `src/proyecto/data/split.py` (incluida la comprobación a mano de la partición) | Raúl Fernando Ossa Ramírez |
| `src/proyecto/features/engineering.py` | Jaime Andrés Úsuga Jiménez |
| `src/proyecto/models/train.py` | David Andrés Paniagua Gutiérrez |
| Notebooks 03 a 05 | Sebastián Orozco Giraldo |

## Resultado

**Sin problemas encontrados.** No se corrigió nada a raíz de esta revisión.

- **Comprobación a mano de la partición** (Raúl Fernando Ossa Ramírez, 5 nov 2026): con `groups=df.index` en `split.py`
  fallaron 3 pruebas de `tests/test_split.py` («132 sedes aparecen en más de una partición»); se revirtió con
  `git checkout`. Detalle en `especificaciones/03-preprocesamiento.md`, sección 6.
- **`pytest`:** 62 de 62 en verde el 5 nov 2026.

## Auditorías de fuga ya hechas

Las hizo el subagente `auditor-de-fuga`; esta revisión no las reemplaza, las complementa.

- `reports/auditoria_etapa3.md`: limpieza y partición (etapa 3).
- `reports/auditoria_etapa4.md`: variables y preprocesamiento (etapa 4).
- `reports/auditoria_train.md`: `train.py` y notebook 05 (etapa 5); veredicto «sin fuga evidente».

## Tareas que cierra

- T024 de `specs/001-feature-engineering/tasks.md`, T034 de `specs/002-preprocessing/tasks.md` y T018 de
  `specs/003-model-training/tasks.md`.
- Las casillas de revisión con el checklist de `especificaciones/03-preprocesamiento.md` y `especificaciones/04-features.md`.

---

## Etapas 6 a 9 (6 nov 2026)

Revisión **conjunta** con `material-del-curso/kit/checklist-revision-ia.md`, hecha el 6 nov 2026 por Jennifer Alejandra
López Sánchez, Jaime Andrés Úsuga Jiménez, Raúl Fernando Ossa Ramírez, David Andrés Paniagua Gutiérrez y Sebastián Orozco
Giraldo.

| Etapa | Qué se revisó |
|---|---|
| 6 · Optimización | `src/proyecto/models/tuning.py` |
| 7 · Validación | `src/proyecto/models/evaluation.py` |
| 8 · Registro | `src/proyecto/inference/schema.py` y `notebooks/08_registro_modelo.ipynb` |
| 9 · App e inferencia | `app/streamlit_app.py` y `src/proyecto/inference/predict.py` |

**Resultado: sin problemas encontrados.** No se corrigió nada a raíz de esta revisión.

**No figuran en esta revisión:** `src/proyecto/inference/form.py` (traducción del formulario a las 21 columnas) y
`notebooks/09_inferencia.ipynb`, ambos de la etapa 9.

**Auditorías de fuga de estas etapas:** `reports/auditoria_etapa6.md`, `auditoria_etapa7.md`, `auditoria_etapa8.md` y
`auditoria_etapa9.md`.

**Casillas que cierra:** la de revisión con el checklist en `especificaciones/06-optimizacion.md`, `07-validacion.md`,
`08-registro.md` y `09-app.md`.

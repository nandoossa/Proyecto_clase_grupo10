# Implementation Plan: Variables y preprocesamiento del modelo (etapa 4)

**Branch**: `001-feature-engineering` (trabajo en `main`) | **Date**: 2026-10-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-feature-engineering/spec.md` y `especificaciones/04-features.md`

## Summary

Crear `src/proyecto/features/engineering.py` con la estructura del ejemplo de CreditSight (`add_features`,
`feature_columns`, `build_preprocessor`) pero con las columnas de Saber 11: 5 numéricas, 14 categóricas y 2 códigos de
municipio como predictores base; 4 variables nuevas apagadas por defecto; vacíos categóricos → «sin respuesta», numéricos
→ mediana + indicador; centinelas como categorías propias; municipios con one-hot y agrupación de poco frecuentes (1 %).
Una lista de columnas prohibidas garantiza que nada con fuga, ningún identificador ni `estu_tipodocumento`, `estu_nacionalidad`
o `estu_privado_libertad` (excluidas por el grupo por equidad) entre como predictor. Las pruebas van
en `tests/test_features.py` y usan tablas hechas a mano, así que no dependen de que la etapa 3 esté terminada.

## Technical Context

**Language/Version**: Python 3.12.10

**Primary Dependencies**: pandas 3.0.6, numpy 2.5.4, scikit-learn 1.9.1 (fijadas en `requirements.txt`)

**Storage**: N/A (funciones en memoria; los datos los carga el notebook 04)

**Testing**: pytest 9.1.1, con tablas pequeñas hechas a mano

**Target Platform**: Windows local (grupo) y Streamlit Community Cloud (app, más adelante)

**Project Type**: librería interna (`src/proyecto/`) usada por notebooks y por la app

**Performance Goals**: ajustar el preprocesador sobre ~58.000 filas de entrenamiento en pocos segundos (no crítico)

**Constraints**: todo lo que aprende de los datos va dentro del `Pipeline`; nada se ajusta con la prueba

**Scale/Scope**: 1 módulo (~150 líneas), 1 archivo de pruebas (~10 pruebas)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | ¿Cumple? | Cómo |
|---|---|---|
| I. Los datos originales no se tocan | ✅ | Solo lee la tabla limpia; no escribe en `data/` |
| II. Se parte por la unidad de análisis | ✅ | `cole_cod_dane_sede` se deja fuera de los predictores para que el notebook 04 agrupe por ella; esta pieza no parte |
| III. La prueba se abre una sola vez | ✅ | El preprocesador es un `ColumnTransformer` que se ajusta dentro del `Pipeline`, solo con entrenamiento |
| IV. Cada decisión con su motivo | ✅ | Motivos en `especificaciones/04-features.md` y `research.md`; cada función con prueba. La decisión de encender o no las variables nuevas se escribe en `reports/` en el notebook 04 |
| V. Nada sensible sale del equipo | ✅ | `estu_consecutivo` y `estu_fechanacimiento` están en la lista prohibida; las pruebas usan datos inventados para la prueba, no filas reales |
| VI. El código es nuestro | ✅ | Estructura igual a la del ejemplo; comentarios en español, nombres en inglés; revisión con checklist y `auditor-de-fuga` |
| VII. No se inventan datos | ✅ | Cifras tomadas de `reports/01_eda.md` y de `data/raw/` |

**Aviso:** la constitución sigue con campos `[entre corchetes]` sin llenar (nombre, caso, unidad de análisis). No bloquea
esta pieza, pero conviene ajustarla con `/speckit-constitution`.

**Re-check post-diseño:** sin cambios; no hay violaciones que justificar.

## Project Structure

### Documentation (this feature)

```text
specs/001-feature-engineering/
├── plan.md              # este archivo
├── research.md          # decisiones de diseño
├── data-model.md        # columnas de entrada, variables nuevas, prohibidas
├── quickstart.md        # cómo comprobarlo
├── contracts/
│   └── engineering.md   # firmas de las funciones públicas
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
src/proyecto/features/
├── __init__.py          # ya existe
└── engineering.py       # NUEVO

tests/
└── test_features.py     # NUEVO
```

**Structure Decision**: se usa la estructura obligatoria de `CLAUDE.md` (`src/proyecto/features/`, `tests/`). No se
toca `src/proyecto/data/` (etapa 3) ni `src/proyecto/models/` (`build_pipeline`, pieza aparte).

## Riesgos y dependencias

- **Depende de la etapa 3** (borrador): nombres y codificación de `edad`, `sin_estrato` y las ordinales. «Sin Estrato»
  ya está decidido (regla 7b, 31 oct 2026). Si la etapa 3 cambia la codificación de personas o cuartos, se ajusta el
  mapeo de `personas_por_cuarto`; una prueba lo detecta.
- **Decisiones del grupo del 31 oct 2026 incorporadas:** opción A de «Sin Estrato», escala de educación confirmada y
  `estu_tipodocumento` fuera de los predictores. Ajustes de la aprobación: `estu_nacionalidad` y `estu_privado_libertad`
  también fuera (equidad); `fami_estratovivienda` conserva su nombre.
- **Notebook 04 (fuera de esta pieza):** prueba otros umbrales de municipios; `TargetEncoder`, si se prueba, dentro del
  `Pipeline` y comparado solo con validación agrupada por sede.
- **Equidad:** `estu_genero`, estrato y naturaleza entran como predictores. La condición de equidad por segmento se
  verifica en la validación (etapa 7), no aquí.

## Complexity Tracking

Sin violaciones de la constitución: no aplica.

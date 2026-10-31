# Informe de variables

> Plantilla en blanco. Resultado de `notebooks/04_features.ipynb`. Cada idea de variable es una
> **hipótesis medida** con la misma validación; se conserva solo si la mejora supera el ruido entre
> pliegues. Guía: `material-del-curso/kit/guia-modelado-y-optimizacion.md`, sección 1.

## Cómo se midió

<!-- Modelo con parámetros fijos, métrica principal y de control, número y tipo de pliegues
     (por qué entidad se parte), semilla. Los MISMOS pliegues para todas las variantes. -->

- **Modelo (parámetros fijos):**
- **Métrica principal** (y por qué):
- **Métricas de control:**
- **Pliegues** (cuántos y partidos por qué entidad):
- **Regla de decisión escrita antes de medir:**

## Tabla de ideas medidas

> La fila 0 es la **referencia** (las variables actuales). "Mejora / ruido" = mejora de la métrica
> principal dividida por su desviación entre pliegues; menor que ~1 está dentro del ruido.

| # | Idea (variable y cómo se calcula) | ¿Se conoce al predecir? | Métrica (± ruido) | Mejora / ruido | Decisión |
|---|---|---|---|---|---|
| 0 | **Referencia** | — | | 0 | — |
| 1 | | ☐ sí ☐ no | | | ☐ conservar ☐ descartar |
| 2 | | ☐ sí ☐ no | | | ☐ conservar ☐ descartar |
| 3 | | ☐ sí ☐ no | | | ☐ conservar ☐ descartar |

## Decisiones y motivos

<!-- Una línea por idea: qué decidiste, con qué cifra y por qué. Las ideas descartadas se anotan
     igual: documentan lo que ya probaste. -->

- **Escala de educación de los padres (grupo, 31 oct 2026, antes de medir):** para `educacion_max_padres` se usa
  Ninguno 0, Primaria incompleta 1, Primaria completa 2, Secundaria incompleta 3, Secundaria completa 4, Técnica o
  tecnológica incompleta 5, Técnica o tecnológica completa 6, Educación profesional incompleta 7, Educación profesional
  completa 8, Postgrado 9. «No sabe» y «No Aplica» no entran en la escala: siguen como categorías propias en
  `fami_educacionmadre` y `fami_educacionpadre` (decisión 6 del EDA). Motivo: una escala ordenada permite tomar el nivel
  más alto del hogar; ubicar «técnica completa» por debajo de «profesional incompleta» es una convención del grupo.
- **`estu_tipodocumento` se excluye como predictor (grupo, 31 oct 2026, antes de medir).** Motivo: su información ya está
  en la edad (TI frente a CC), y los documentos de extranjeros (PEP, PPT, CE…) funcionarían como indicador de condición
  migratoria, lo que va contra la condición de equidad.
-

## Supuestos y riesgos

<!-- Variables que solo valen si cierto dato se conoce al momento de decidir; riesgos de fuga;
     lo que complicaría la app si se conserva. -->

-

## Qué se lleva el pipeline final

<!-- La lista final de variables, y dónde está el código (`src/<paquete>/features/`). -->

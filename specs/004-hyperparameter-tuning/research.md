# Research: Optimización de los finalistas

## 1. Herramienta de búsqueda

- **Decision**: Optuna con muestreador TPE (semilla 42), como el ejemplo.
- **Rationale**: ya está en `requirements.txt`; con pocos ensayos explora mejor que la rejilla y permite parámetros
  categóricos (`min_frequency`, pérdida) junto con continuos. Guarda el estudio en sqlite y se reanuda.
- **Alternatives considered**: `GridSearchCV`/`RandomizedSearchCV` de scikit-learn (no reanudan, y el registro anidado en
  MLflow por ensayo es más incómodo).

## 2. Métrica y dirección

- **Decision**: minimizar el MAE medio de los pliegues (en positivo, con `evaluate_folds` de `train.py`); registrar RMSE y R²
  con su desviación.
- **Rationale**: es la métrica del caso; `evaluate_folds` ya devuelve las métricas en positivo, así que la dirección es
  `minimize` sin cambios de signo.
- **Alternatives considered**: maximizar `neg_mean_absolute_error` (equivalente, pero confunde al leer).

## 3. Presupuesto y pliegues

- **Decision**: 25 ensayos de HGB y 30 de XGBoost; 3 pliegues `GroupKFold` por sede sobre la parte de búsqueda.
- **Rationale**: tiempos medidos el 5 nov 2026 en este equipo (un ajuste sobre ~29.000 estudiantes, 300 árboles): HGB 4,0 s
  (umbral 1 %) y 9,8 s (0,1 %); XGB 2,3 s y 2,9 s; la pérdida absoluta casi no cambia el tiempo. Con hasta 600 árboles y 3
  pliegues se estima ~15–20 min en total. XGBoost recibe más ensayos porque es ~3 veces más rápido y tiene un parámetro más.
  La guía pide 12–20 por modelo como orden de magnitud; se sube un poco porque hay dos parámetros categóricos nuevos.
- **Alternatives considered**: 5 pliegues (como el torneo): ~1,7 veces más lento, superaría el límite con este presupuesto.

## 4. Medición de los parámetros de partida

- **Decision**: medir los parámetros de partida de `candidates()` con los mismos pliegues de la búsqueda y registrarlos como
  ejecución `<modelo>-partida`, fuera del estudio de Optuna.
- **Rationale**: es el «antes» comparable. No se encola como ensayo porque `l2_regularization=0` (HGB) no cabe en un rango
  logarítmico.

## 5. Reserva y bootstrap

- **Decision**: `split_by_group(train, test_size=0.25, seed=7)`; intervalo del 95 % con 1.000 remuestreos de sedes; la
  diferencia de MAE se calcula como suma de (|error A| − |error B|) de las sedes elegidas ÷ número de estudiantes de esas
  sedes (igual que `intervalo_por_entidad` de la guía).
- **Rationale**: los estudiantes de una sede no son independientes (la sede explica el 36 % de la variación); remuestrear
  filas daría un intervalo demasiado estrecho.

## 6. Seguimiento

- **Decision**: `configure_mlflow()` sin forzar local (clase 4: Databricks si conecta) y `set_experiment("saber11-optimizacion")`;
  ejecución madre `optuna-<modelo>` con los ensayos anidados `<modelo>-ensayo-NN`.
- **Rationale**: lo pide la regla 7 de `CLAUDE.md`; si Databricks falla, `configure_mlflow` cae solo a sqlite y lo avisa.

## 7. Paralelismo

- **Decision**: ensayos en serie (`n_jobs=1` en Optuna); HGB usa los núcleos por OpenMP y XGB `n_jobs=2` como en el torneo.
- **Rationale**: ensayos en paralelo complican el registro anidado en MLflow y la reproducibilidad del TPE.

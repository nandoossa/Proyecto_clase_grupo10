# Research: Registro del modelo

## 1. Firma con columnas enteras y vacíos
- **Decision**: convertir las 5 numéricas a `float64` en el ejemplo y la firma; las categóricas como texto (los códigos de
  municipio, que son enteros, se pasan como texto porque el preprocesador los trata como categorías).
- **Rationale**: MLflow no admite enteros con vacíos en la firma (patrón del ejemplo CreditSight).

## 2. Ida y vuelta
- **Decision**: igualdad exacta (`np.array_equal`) en 500 filas del entrenamiento, no `allclose`.
- **Rationale**: el pedido exige «exactamente lo mismo»; con `cloudpickle` el objeto es el mismo y debe dar bits iguales.

## 3. Exportación
- **Decision**: `mlflow.sklearn.load_model("models:/<nombre>@champion")` → `joblib.dump` a `models/model.joblib`.
- **Rationale**: el registro es la fuente de verdad (guía §6).

## 4. Esquema para regresión
- **Decision**: extender `build_schema` con `task="regression"` (sin clases ni matriz de costos); agregar `predict_score`.
  Conservar las funciones de clasificación hasta la etapa 9.
- **Rationale**: no romper la app de plantilla ni sus pruebas mientras no se adapte.

## 5. Datos sensibles
- **Decision**: no imprimir la ruta del experimento (incluye el correo), quitar los «View run» de las salidas del notebook y
  buscar correos, dirección del espacio de trabajo y tokens en todo lo que se sube.

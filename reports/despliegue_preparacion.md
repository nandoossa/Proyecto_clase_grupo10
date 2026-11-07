# Preparación del despliegue (etapa 10, clase 5)

> 6 nov 2026. **No se desplegó**: el despliegue lo hace el grupo. Este informe deja la evidencia de que el repositorio
> cumple la lista de `material-del-curso/guias/streamlit-despliegue.md`, los hallazgos de la revisión del código y lo
> que falta. Especificación: `specs/008-deploy-readiness/spec.md`. Revisión del código: `reports/revision_app.md`.

## 1. Lista de la guía: requisitos del repositorio

| Requisito | ¿Cumple? | Evidencia (comando → resultado) |
|---|---|---|
| Repo **público** en GitHub | ☒ sí | `curl https://api.github.com/repos/nandoossa/Proyecto_clase_grupo10` sin sesión → HTTP 200 |
| `requirements.txt` en la **raíz** | ☒ sí | `git ls-files requirements.txt` → `requirements.txt` |
| Versiones **fijadas** (`nombre==versión`) | ☒ sí | 0 líneas sin `==`; las 18 versiones fijadas coinciden con las instaladas en el equipo donde se entrenó (`scikit-learn 1.9.1`, `pandas 3.0.6`, `numpy 2.5.4`, `joblib 1.6.0`, `streamlit 1.66.0`, …) |
| `requirements.txt` cubre lo que importa la app | ☒ sí | Al importar la app y cargar el modelo se cargan solo `streamlit`, `pandas`, `numpy`, `scikit-learn`, `scipy` y `joblib`. **`app/requirements.txt`** (H4) trae solo esas 6, con las versiones de la raíz; Streamlit Community Cloud lo usa porque está junto al archivo principal. Comprobado en un entorno limpio: la app arranca y estima 250 con el perfil de prueba |
| `models/model.joblib` **dentro** del repo | ☒ sí | `git ls-files models/` lo lista; `git check-ignore` no lo ignora; tamaño 1,17 MB |
| `models/input_schema.json` dentro del repo | ☒ sí | Versionado y no ignorado; 11,2 KB |
| Python **3.12** | ☒ sí (se elige al desplegar) | Entorno local: Python 3.12.10. No hay `runtime.txt`: la versión se elige en **Advanced settings → Python 3.12** al crear la app |
| La app corre en local sin errores | ☒ sí | `streamlit run app/streamlit_app.py --server.headless true` desde la raíz → chequeo de salud `/_stcore/health` responde `ok`, sin errores en el registro |
| Sin `.env` ni datos personales en el repo | ☒ sí | `git ls-files` no lista `.env`, `.db` ni archivos de `data/raw` o `data/processed`; `git grep` de correos, direcciones de espacio de trabajo de Databricks y tokens → ninguna coincidencia |
| La app **no** consulta Databricks | ☒ sí | Ningún `mlflow`, `databricks`, `dotenv` ni `token` en `app/` ni en `src/proyecto/inference/`; al importar la app no se carga `mlflow` ni `databricks` |
| Rutas armadas desde la ubicación del archivo | ☒ sí | `app/streamlit_app.py:16`: `ROOT = Path(__file__).resolve().parents[1]`; sin `Path.cwd()` ni `os.getcwd()` |

**Datos para crear la app** (los usa el grupo al desplegar): repo `nandoossa/Proyecto_clase_grupo10`, rama `main`, archivo
principal `app/streamlit_app.py`, Python 3.12.

## 2. Revisión del código (subagente `revisor-de-codigo-ia`)

Informe completo en `reports/revision_app.md`. **Veredicto: aceptar con cambios.**

| # | Gravedad | Hallazgo | Riesgo en el despliegue |
|---|---|---|---|
| H1 | Importante | Si el modelo o el esquema no cargan (archivo dañado, otra versión de scikit-learn), el usuario ve un error técnico en vez de un mensaje claro | Es el fallo típico en la nube (guía §8) |
| H2 | Importante | El aviso de uso responsable se muestra al final de la página y no aparece si faltan los archivos | La app dice «siempre visible» y no lo es |
| H3 | Importante | `schema.py` conserva el código de clasificación de la plantilla, que la etapa 8 dijo que se quitaría en la etapa 9; bug latente si se pasa `cost_matrix` con `task="regression"` | Código muerto que contradice la documentación |
| H4 | Importante | `requirements.txt` instala librerías que la app no usa (`mlflow`, `databricks-sdk`, `optuna`, `shap`, `nbconvert`…) | Despliegue más lento y más puntos de falla; decisión del grupo (CLAUDE.md pide un solo `requirements.txt`) |
| H5–H11 | Menores | `sys.path` duplicado; el pickle depende de `src/proyecto/features/engineering.py`; prueba anti-Databricks débil; `form.py` sin defensa ante un esquema viejo; cifras del aviso escritas en tres sitios; datos del esquema sin uso; sin control de coherencia estrato / «Sin estrato» fuera de la app | Bajo |

**Aplicados el 6 nov 2026** (pedido del grupo): H1 a H4, y de los menores los que no cambian el comportamiento (H5, H6,
H7, parte de H9 y de H10). H8 y H11 no se aplicaron porque cambiarían qué entradas se rechazan. Detalle en la tabla
«Qué se hizo con cada hallazgo» de `reports/revision_app.md`. Pruebas: 115 de 115.

## 3. Pruebas faltantes (subagente `escritor-de-pruebas`)

El revisor encontró funciones públicas sin prueba directa. Las que limpian o transforman datos (`form_to_row`,
`reference_range`, `display_value`, `build_schema`) ya tenían prueba, así que la regla 9 de `CLAUDE.md` se cumplía. Aun así,
el subagente `escritor-de-pruebas` agregó **8 pruebas** al final de `tests/test_inference.py`, sin tocar `src/` ni `app/`:

1. `test_options_offers_sin_respuesta_only_for_nullable_fields`
2. `test_options_stratum_offers_sin_estrato`
3. `test_options_stratum_without_blank_when_not_nullable`
4. `test_load_model_missing_path_raises_file_not_found`
5. `test_validate_inputs_valid_row_returns_no_warnings`
6. `test_validate_inputs_outside_observed_but_inside_valid_range_only_warns`
7. `test_validate_inputs_unseen_municipality_only_warns`
8. `test_save_schema_then_load_schema_gives_same_dict`

**Resultado:** `tests/test_inference.py` pasó de 15 a 23 pruebas y el proyecto completo de 105 a **113, todas en verde y
ninguna saltada** (`PYTHONUTF8=1 python -m pytest -q -rs`).

**Comportamientos que vio** (no son errores con el esquema actual; se anotan): `options()` lanza `KeyError` si el esquema
no trae la clave `nullable` (mismo punto que el hallazgo H8 del revisor), mientras que `validate_inputs` sí la trata como
opcional.

**No probado:** el fallo de carga del modelo dentro de la app (depende de corregir antes el hallazgo H1).

## 4. Lista de verificación antes de la exposición (guía §11)

- [x] El enlace abre en una ventana privada y muestra el formulario (7 nov 2026; detalle en `reports/09_despliegue.md`, apartado 3).
- [x] Un caso de prueba conocido da una predicción coherente (perfil del apartado 3 de `reports/09_despliegue.md`: 250,
      «como referencia, entre 217 y 283»). En el enlace público dio 250 (7 nov 2026).
- [x] Un dato inválido muestra un mensaje claro, no un error (edad 81; comprobado en el enlace público el 7 nov 2026).
- [x] No hay token, `.env` ni datos personales en el repo (comprobado el 6 nov 2026, apartado 1).
- [x] Abrir la app 10 minutos antes y comprobar que está despierta (se abrió antes de la exposición del 7 nov 2026).
- [x] Plan B listo: app en local (`streamlit run app/streamlit_app.py` desde la raíz) y capturas de pantalla con fecha
      (listo para la exposición del 7 nov 2026).

## 5. Plan B

Si la app falla en vivo, seguir los pasos del apartado 4 de `reports/09_despliegue.md`:
1. Abrir la app en local con `streamlit run app/streamlit_app.py` desde la raíz del repositorio.
2. Si tampoco funciona, mostrar las capturas de pantalla (pendientes de tomar el día de la presentación).

Si el despliegue falla, leer el registro de la app de abajo hacia arriba y comparar con la tabla de errores comunes de la
guía (§8).

# Auditoría de fuga y datos sensibles · Etapa 9 (app e inferencia)

> Informe del subagente `auditor-de-fuga` (6 nov 2026), con sus instrucciones de `.claude/agents/auditor-de-fuga.md`, en
> modo solo lectura. Se corrió como agente general, porque la sesión de Claude Code estaba abierta en la carpeta padre y
> no cargaba los subagentes del proyecto. Se guarda tal cual; la nota final la agregó Claude y no es parte del informe.

Fecha: 6 nov 2026

Archivos revisados: `src/proyecto/inference/predict.py`, `src/proyecto/inference/form.py`, `src/proyecto/inference/schema.py`, `app/streamlit_app.py`, `notebooks/09_inferencia.ipynb` (código y salidas), `tests/test_app.py`, `tests/test_inference.py` (solo la parte final, líneas 180-203), `models/input_schema.json`, `models/ficha_modelo.md`, `reports/09_despliegue.md`, `.gitignore`, y búsquedas de texto en `src/` y en todo el proyecto. No leí `constitution.md`, `especificacion-proyecto.md`, `CLAUDE.md`, `especificaciones/09-app.md`, `specs/007-app-inference/plan.md` ni `src/proyecto/data/cleaning.py`; el criterio de qué columnas no deben entrar salió de la ficha del modelo y del esquema.

| Hallazgo | Archivo:línea | Por qué importa | Cómo corregirlo | Estado |
|---|---|---|---|---|
| La app, el notebook 09 y `src/` no leen la prueba. Búsqueda de `test.joblib`, `prueba_resultados`, `X_test` y `y_test` en `app/`: sin resultados. En `src/` solo aparece `models/evaluation.py:3`, un comentario que dice que ese módulo no abre la prueba. El notebook 09 solo carga `model.joblib`, `input_schema.json` y `train.joblib` (celdas `c70c1fbb` y `ade2772e`). | `app/`, `src/`, `notebooks/09_inferencia.ipynb` | La prueba debe quedar cerrada en esta etapa. | Ninguna. | Sin problema |
| `predict_score` no calcula nada con los datos que recibe. Valida contra el esquema y llama a `model.predict`. `validate_inputs` solo compara con listas y rangos ya guardados. La prueba `test_predict_score_does_not_learn_from_input` (`tests/test_inference.py:180-187`) comprueba que el esquema no cambia y que una fila no cambia por las otras del lote. | `predict.py:78-88`, `predict.py:36-75` | Medianas o categorías calculadas al predecir serían fuga. | Ninguna. | Sin problema |
| `form_to_row` solo traduce textos a códigos fijos (`HOUSEHOLD_SIZE_CODES`, `ROOM_CODES`) y usa el esquema para rangos y vacíos permitidos. No calcula cifras a partir de los datos. | `form.py:120-148` | Misma razón que el punto anterior. | Ninguna. | Sin problema |
| La app solo carga el modelo y el esquema desde archivos del repositorio. No usa datos de estudiantes. | `streamlit_app.py:31-32`, `streamlit_app.py:49-56` | Ninguna lectura de datos reales en la app. | Ninguna. | Sin problema |
| `municipality_names` se calcula solo con `train.joblib` y no cambia el resto del esquema. El código hace `pd.concat` de las columnas de municipio de `train`, quita duplicados, exige un nombre único por código, y se queda solo con códigos del esquema. Luego compara el esquema anterior con el nuevo sin esa clave y lanza error si algo cambió. Salida: «139 municipios con nombre; por ejemplo 5001 → MEDELLÍN». El JSON tiene la clave con códigos y nombres de municipios, sin datos de personas. | Notebook, celda `ade2772e`; `input_schema.json:451-591` | Nombres calculados con la prueba serían fuga; un cambio al esquema podría alterar la validación. | Ninguna. | Sin problema |
| Un archivo de tests lee una fila real del entrenamiento, `train.joblib` `.head(1)`, solo para ver que el rango del puntaje es 100-477. No la imprime, no la guarda y se salta si falta el archivo. Es entrenamiento, no prueba. | `tests/test_inference.py:200` | Mantiene los datos reales dentro de la prueba y no los deja en ningún archivo. | Opcional: usar una fila inventada, como en `test_app.py`. | Sin problema (menor) |
| La fila que arma `form_to_row` tiene exactamente las 21 columnas del esquema (5 numéricas y 16 categóricas, línea 147). No entran `cole_cod_dane_sede`, identificadores, puntajes por área ni datos personales. Las únicas columnas de localización son los dos códigos de municipio, que están en el esquema desde la etapa 8 y la ficha. | `form.py:147`, `input_schema.json:2-27` | Evita que sede, identificadores o puntajes entren como predictor. | Ninguna. | Sin problema |
| La app no consulta Databricks: `app/streamlit_app.py` y `form.py` no contienen `mlflow`, `databricks`, `token` ni credenciales. La prueba `test_app_code_does_not_use_databricks` (`tests/test_app.py:201-204`) lo verifica con esas tres palabras. | `streamlit_app.py`, `form.py`; `tests/test_app.py:201` | Regla 8: no hay credenciales en la nube. | Ninguna. | Sin problema |
| Salidas del notebook 09: solo perfiles inventados (celda `4c2197a6`, perfiles A-D), la edad rechazada de la celda `ea7d60be` y nombres de municipios. No hay filas reales, identificadores ni nombres de estudiantes. `del train` en `ade2772e` cierra el uso de los datos. | Notebook, celdas `ade2772e`, `4c2197a6`, `ea7d60be` | Evita subir datos reales en las salidas. | Ninguna. | Sin problema |
| Tokens, URLs de Databricks y rutas de usuario: solo aparecen marcadores de ejemplo en `.env.example:13,14,21` (`TU-WORKSPACE`, `pega-aqui-tu-token-personal`, `/Users/tu-correo/...`) y `tests/test_tracking.py:33` (`/Users/alguien/carpeta`). No hay URLs reales `*.cloud.databricks.com` ni `adb-*.azuredatabricks.net`, ni correos o tokens reales en el proyecto fuera de `material-del-curso/`, que excluí de la búsqueda. | `.env.example`, `tests/test_tracking.py` | Evita filtrar credenciales o direcciones. | Ninguna. | Sin problema |
| `.gitignore` excluye `.env` (línea 2), `data/raw/*` (15), `data/processed/*` (39-40, con excepción de `.gitkeep`), `mlruns/`, `mlflow_local.db`, `models/final_pipeline.joblib` y `saber11_antioquia_2022.csv`. Existe un `.env` local, que queda ignorado; no lo abrí. | `.gitignore` | Impide subir credenciales y datos de estudiantes. | Ninguna. | Sin problema |
| Cifras del aviso de la app (`streamlit_app.py:36-46`, líneas 77-81): R² 0,363, 36 %, estrato 5 con 39,57, hombres 35,74 y mujeres 31,40, no oficiales 35,55 y oficiales 32,66, MAE 33,3, 289 sedes, calendario A, 2022. Todas coinciden con `ficha_modelo.md:37-60,75-80`. `TYPICAL_ERROR = 33` (`form.py:19`) coincide con MAE 33,32. | `streamlit_app.py`, `form.py:19` | Cifras inventadas serían engañosas. | Ninguna. | Sin problema |
| `reports/09_despliegue.md` coincide con la ficha: R² 0,363, 39,57, 35,74 y 31,40, MAE 33,32, 12 campos que admiten «Sin respuesta». Sus «139 municipios» coinciden con la salida del notebook. El perfil A da 250 con «entre 217 y 283», igual que la celda `4c2197a6` del notebook. | `09_despliegue.md:29-33,43`; ficha; notebook | Evita cifras sin respaldo. | Ninguna. | Sin problema |
| `reports/09_despliegue.md:14,58` menciona el repo `nandoossa/Proyecto_clase_grupo10`, que parece un usuario personal de GitHub. No es un secreto, pero revela una cuenta. | `reports/09_despliegue.md:14,58` | Dato de identidad en un informe que se sube. | Confirmar que el grupo acepta mostrarlo; si no, dejar «repositorio del grupo». | Menor, a criterio del grupo |
| `ficha_modelo.md:110-111` incluye el commit `3a75853` y el id de ejecución `78b51940c3f74aa8a6d3877b8a4ee739`. `ficha_modelo.md:20` incluye el nombre del modelo registrado `workspace.default.saber11_puntaje_global`. No son credenciales ni URLs. | `ficha_modelo.md:20,110-111` | Referencias internas sin acceso por sí solas. | Ninguna. | Sin problema |

## Qué no pude comprobar

- **Los otros casos de `09_despliegue.md`:** los puntajes 271 (edad 13), 210 (edad 80) y 225 (todos los campos «Sin respuesta»). El notebook no los muestra y no podía ejecutar nada. Solo comprobé el caso normal, 250 con 217-283.
- **`model.joblib`:** no pude abrirlo, así que no verifiqué que sea el Pipeline exportado de `champion` ni que se haya entrenado sin la prueba (eso corresponde a la auditoría de la etapa 8).
- **`.env` local:** no lo abrí; solo confirmé que existe y que `.gitignore` lo excluye.
- **`requirements.txt`:** no lo leí, así que no verifiqué las versiones fijadas ni que no incluya librerías de Databricks que la app no necesita.
- **Documentos de especificación y reglas:** no leí `constitution.md`, `especificacion-proyecto.md`, `CLAUDE.md`, `especificaciones/09-app.md` ni `specs/007-app-inference/plan.md`. Tampoco `src/proyecto/data/cleaning.py`; solo vi lo que importa `form.py` de ahí.
- **Autoría de `municipality_names`:** el JSON actual tiene 139 códigos que coinciden con la salida del notebook, pero no verifiqué los nombres uno por uno contra `train.joblib`.
- **Archivos de `material-del-curso/` y otros notebooks (01 a 08):** no los revisé en esta pasada.

## Veredicto

Sin fuga evidente: no encontré ningún problema que corregir antes de seguir. Quedan solo dos puntos menores, a criterio del grupo: el nombre de usuario de GitHub en `reports/09_despliegue.md`, y tres cifras de `reports/09_despliegue.md` (271, 210 y 225) que no pude comprobar.

---

**Nota de Claude (no es parte del informe del auditor):**

- **Cifras 271, 210 y 225:** salen de una ejecución con AppTest sobre `app/streamlit_app.py` el 6 nov 2026, con el perfil
  inventado de `tests/test_app.py` y edad 13, edad 80 y los 12 campos en «Sin respuesta», respectivamente. Esa ejecución
  no queda guardada en un archivo. Las pruebas automáticas comprueban esos casos (puntaje entero entre 100 y 477), pero
  no el valor exacto.
- **Repositorio `nandoossa/Proyecto_clase_grupo10`:** ya figuraba como repositorio público del grupo en
  `especificacion-proyecto.md` y en `reports/documentacion_proyecto.md`; no se cambió. Queda a criterio del grupo.
- **Nada se corrigió** a raíz de esta auditoría.

# Despliegue de la app

> Etapa 9 (6 nov 2026; enlace agregado el 7 nov 2026). **La app está publicada en Streamlit Community Cloud:**
> https://predictorpruebasaber.streamlit.app. Falta comprobar el enlace en una ventana privada con los casos del apartado 3.
> Este informe deja escritas las decisiones, las pruebas hechas en local con sus resultados reales y el plan de
> despliegue. Guías: `material-del-curso/guias/streamlit-despliegue.md` y
> `material-del-curso/kit/guia-despliegue-y-presentacion.md`. Especificación: `especificaciones/09-app.md`.

## 1. Enlace y estado

| Dato | Valor |
|---|---|
| Enlace público de la app | https://predictorpruebasaber.streamlit.app |
| Plataforma | Streamlit Community Cloud |
| Repo, rama y archivo principal | `nandoossa/Proyecto_clase_grupo10`, rama `main`, `app/streamlit_app.py` |
| Versión de Python elegida | ☒ 3.12  ☐ otra |
| ¿Se comprobó en una **ventana privada**? | ☐ sí  ☐ no → pendiente: abrirlo sin sesión iniciada y repetir los casos del apartado 3 |
| ¿Se desplegó? | ☒ sí  ☐ no |
| ¿Corre en local? | Sí: `streamlit run app/streamlit_app.py` arranca y responde (comprobado el 6 nov 2026) |

## 2. Decisiones de despliegue y su motivo

| Decisión | Motivo |
|---|---|
| La app carga `models/model.joblib` desde el repo y **no consulta Databricks** | Regla 8 de `CLAUDE.md`: no se ponen credenciales en la nube y la app no depende de la cuota de otra plataforma. Una prueba verifica que el código no menciona `mlflow`, `databricks` ni `token` |
| Versiones fijadas en `requirements.txt` (Python 3.12, `streamlit==1.66.0`, `scikit-learn==1.9.1`) | El modelo se guardó con scikit-learn 1.9.1; otra versión podría no cargarlo o predecir distinto |
| Logo `app/assets/icfes_saber11.png` y atribución en la barra lateral (6 nov 2026): «Datos: ICFES (datos.gov.co, CC BY-SA 4.0). Esta herramienta no es oficial ni está avalada por el ICFES.» | La licencia exige dar crédito al ICFES. Ruta relativa a la carpeta de la app; si la imagen falta, se muestra solo el texto. ⚠ El logo es una marca del ICFES, no está cubierto por la licencia de los datos |
| `app/requirements.txt` con solo las 6 librerías de la app (6 nov 2026, revisión de la app H4) | Streamlit Community Cloud lo usa porque está junto a `app/streamlit_app.py`: instala menos y no instala `mlflow` ni `databricks-sdk`. Comprobado en un entorno limpio |
| Qué NO se subió al repo (y por qué) | `.env` (credenciales), `data/raw/` y `data/processed/` (datos de estudiantes; se regeneran con el notebook 03), `models/final_pipeline.joblib` (intermedio). La app no los necesita |
| Formulario en español con textos, no códigos | Quien la usa no conoce los códigos de la etapa 3: elige «3 a 4» o «Dos» y la app los traduce (`src/proyecto/inference/form.py`) |
| Edad: campo numérico entero sin mínimo ni máximo (decisión del grupo, 6 nov 2026) | Si se escribe un valor fuera de 13–80, la app muestra el mensaje de corrección en lugar de impedir escribirlo |
| Municipios con nombre y código, p. ej. «MEDELLÍN (5001)» (decisión del grupo) | Clave `municipality_names` en `models/input_schema.json`, calculada solo con el entrenamiento (139 municipios; cada código tiene un único nombre) |
| Resultado: puntaje redondeado y «se equivoca en promedio 33 puntos; como referencia, entre X y Y» (decisión del grupo) | El MAE de la prueba es 33,32. La referencia es la estimación ± 33, recortada a 100–477; la app aclara que **no** es un intervalo de confianza |
| «Sin respuesta» solo en los 12 campos que tenían vacíos en el entrenamiento | El modelo aprendió a usar esa ausencia; los otros 9 campos son obligatorios |
| Género como entrada (decisión del grupo) | El modelo lo usa; quitarlo exigiría reentrenar y volver a evaluar con la prueba, que ya se abrió. La brecha de error por género se muestra en el aviso |
| Aviso de uso responsable siempre visible | Con los límites de `models/ficha_modelo.md`: orienta y no excluye; calendario A, Antioquia, 2022; R² 0,363; estrato 5 (MAE 39,57); hombres 35,74 frente a mujeres 31,40 |

## 3. Pruebas (en local, no en un enlace público)

Hechas con `streamlit.testing.v1.AppTest` sobre `app/streamlit_app.py` el 6 nov 2026, con un perfil **inventado**: colegio
oficial urbano de Medellín, jornada mañana, 17 años, mujer, estrato 2, hogar de «3 a 4» personas y «Tres» cuartos.
Las mismas comprobaciones quedan como pruebas automáticas en `tests/test_app.py`.

| Caso | Datos usados | Resultado esperado | Resultado real |
|---|---|---|---|
| Normal | El perfil inventado | Un puntaje entero y la referencia ± 33 | **250**, «como referencia, entre 217 y 283» |
| Límite (bordes de la edad) | El mismo perfil con edad 13 y con edad 80 | Se aceptan los dos | **271** (entre 238 y 304) y **210** (entre 177 y 243) |
| Inválido (debe rechazarse con un mensaje claro) | Edad 81 | Mensaje de corrección y ningún puntaje | Sin puntaje: «Revisa estos datos: Edad (años cumplidos): escribe un número entero entre 13 y 80, o marca «Sin respuesta».» |
| Con todos los campos posibles en «Sin respuesta» | Los 12 campos que lo admiten | Responde igual | **225**, «como referencia, entre 192 y 258» |

También se comprobó que un campo obligatorio sin elegir (jornada del colegio) da un mensaje que lo nombra y ningún
puntaje. En regresión no hay «decisión» que cambie en el límite; por eso el caso límite usa los bordes del rango válido.

## 4. Problemas encontrados y plan B

- **Errores de despliegue:** pendiente de anotar por el grupo (este informe no registra cómo fue el despliegue). En
  local la app arrancó sin errores y respondió el chequeo de salud de Streamlit.
- **Plan de despliegue** (pasos de `material-del-curso/guias/streamlit-despliegue.md`):
  1. Confirmar en GitHub que están `requirements.txt` (en la raíz), `models/model.joblib`, `models/input_schema.json` y
     `src/proyecto/`.
  2. En Streamlit Community Cloud: repo `nandoossa/Proyecto_clase_grupo10`, rama `main`, archivo
     `app/streamlit_app.py`, Python 3.12.
  3. Abrir el enlace en una **ventana privada** y repetir los 4 casos del apartado 3. **Pendiente.**
  4. Pegar el enlace en `README.md` y en el apartado 1 de este informe. **Hecho el 7 nov 2026.**
  5. Si falla, leer el registro de abajo hacia arriba y anotar aquí el mensaje y la corrección.
- **Plan B** (si la app falla en vivo): app en local con `streamlit run app/streamlit_app.py` desde la raíz del repo, y
  captura de pantalla con fecha y repo (pendiente de tomar el día de la presentación).

## 5. Ensayo cronometrado (clase 5)

Pendiente: se llena durante el ensayo, con los tiempos reales.

| Parte | Tiempo previsto | Tiempo real |
|---|---|---|
| Caso de negocio | 2 min | |
| App (demo en vivo) | 4 min | |
| Resultados | 3 min | |
| Cierre | 1 min | |
| **Total** | **10 min** | |

- ¿Se pasó de 10 minutos? ☐ no  ☐ sí → qué se recortó: _______________
- Retroalimentación recibida (lo mejor y la corrección que propusieron): _______________
- **Corrección concreta que hicimos por ella:** _______________
- Quién habla de qué y quién responde las preguntas técnicas: _______________

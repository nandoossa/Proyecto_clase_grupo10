---
marp: true
theme: default
paginate: true
header: "Presentación ejecutiva · Predictor de resultados Pruebas Saber 11 en Antioquia"
footer: "Casos Avanzados · Maestría en Ingeniería Analítica · Grupo 10"
---

# 1 · Hoy el puntaje llega cuando ya no hay tiempo de actuar

- **¿Quién decide?** Secretaría de Educación, rectores y docentes, y las propias familias.
- **¿Qué decide?** A qué colegios llevar refuerzo, qué estudiantes de grado 11 necesitan preparación adicional, a qué universidad o beca aspirar.
- **¿Cuánto cuesta equivocarse?** Lo mismo en las dos direcciones: sobreestimar deja sin apoyo a quien lo necesitaba; subestimar gasta recursos donde no hacían falta. El costo crece con cada punto de error.

> **Anticipar el puntaje de Saber 11 de cada estudiante, antes del examen, para orientar el apoyo a tiempo.**

<!--
NOTAS (2 min) · Gancho: "El ICFES nos dice quién necesitaba ayuda... cuando la prueba ya pasó."
- Presentar a quién servimos y qué decisión mejora.
- Explicar por qué los dos errores cuestan igual: esa es la razón de la métrica (no la nombren todavía).
- Cerrar con el titular de la diapositiva.
-->

---

# 2 · Aprendimos de 72.000 estudiantes y medimos con colegios que el modelo nunca vio

- **Los datos:** resultados oficiales del ICFES (datos.gov.co, licencia CC BY-SA 4.0), Antioquia 2022: 144.766 filas, de las que la **mitad eran duplicados**. Quedan **72.148 estudiantes** de calendario A, con datos de su colegio, su perfil y su familia.
- **Validación honesta:** partimos por **sede del colegio**, porque la sede sola explica el 36 % de la variación del puntaje. Así el error se mide con colegios no vistos, como pasará en la app. La prueba se abrió **una sola vez**.
- **Qué comparamos:** 5 modelos frente a "decir siempre la mediana". Ganó **HistGradientBoosting**, optimizado con 55 ensayos registrados en Databricks.
- **Qué descartamos:** los puntajes por área (serían darle la respuesta al modelo) y 4 variables nuevas que **no mejoraron** el error.

<!--
NOTAS (1 min, dentro de "Resultados" o al final del caso) · Mensaje: "no hicimos trampa".
- La frase clave: "si un colegio estaba en entrenamiento, nunca aparecía en la prueba".
- Mencionar lo descartado da credibilidad: no todo lo que probamos funcionó.
- Lo técnico (Optuna, pliegues, bootstrap) se deja para las preguntas.
-->

---

# 3 · El modelo se equivoca 10 puntos menos por estudiante

| | Sin el modelo (decir siempre 242) | Con el modelo |
|---|---|---|
| Error promedio por estudiante | **43,1 puntos** | **33,3 puntos** |
| Cohorte de Antioquia (≈ 72.000 estudiantes al año) | Cada estudiante, ±43 puntos en promedio | Cada estudiante, ±33 puntos en promedio |

- **Mejora:** 9,8 puntos menos de error por estudiante (22,7 %), intervalo del 95 % entre **8,0 y 11,8 puntos**. Cumple la meta mínima (≤ 38) y la deseable (≤ 35).
- **Para todos los grupos:** mejora el punto de partida en los **14 segmentos** de estrato, zona, tipo de colegio y género.
- *Nota técnica: MAE 33,32 [32,39 ; 34,21]; RMSE 41,5; R² 0,36.*

<!--
NOTAS (2 min) · Cifra protagonista: "10 puntos menos de error por estudiante".
- Explicar el MAE en una frase: "en promedio, el puntaje estimado se aleja 33 puntos del real, en una escala de 0 a 500".
- Subrayar que el resultado viene de la prueba abierta una sola vez, y que las cifras previas (33,6 y 33,7) no eran optimistas.
- Si preguntan por el R²: explica algo más de un tercio de la variación; el resto depende de factores que no están en los datos.
-->

---

# 4 · Véanlo funcionar

**Enlace:** _(pegar el enlace público de Streamlit; abrirlo 10 minutos antes)_

1. **Caso normal:** colegio oficial urbano de Medellín, jornada mañana, 17 años, estrato 2, hogar de 3 a 4 personas → **250 puntos** (como referencia, entre 217 y 283).
2. **Caso límite:** el mismo perfil con edad 13 y con edad 80, los bordes del rango válido → se aceptan los dos (**271** y **210**).
3. **Dato inválido:** edad 81 → la app **no da puntaje** y explica qué corregir.

> Plan B: la app en local (`streamlit run app/streamlit_app.py`) y una captura con fecha.

<!--
NOTAS (4 min) · Demo en vivo, sin leer la diapositiva.
- Quien maneja la app narra en voz alta qué elige y qué espera.
- Señalar el aviso de uso responsable que la app siempre muestra.
- Si la app tarda (puede estar "dormida"), pasar al plan B sin perder tiempo.
-->

---

# 5 · Lo que el modelo no hace, y lo que haríamos con más tiempo

- **No decide:** orienta a quién ofrecer apoyo; **no excluye ni etiqueta** a ningún estudiante. Explica relaciones, no causas.
- **Límites de los datos:** un solo periodo (2022), Antioquia y calendario A. Explica algo más de un tercio de la variación del puntaje.
- **Uso responsable:** el error es mayor en estrato 5 (39,6 puntos) y con los hombres (35,7 frente a 31,4 con las mujeres). La app lo advierte siempre.
- **Siguientes pasos:** sumar más años de datos, vigilar el error por grupo cada cohorte y reentrenar cuando cambie.
- **Una decisión que cambiaríamos:** evaluar desde el inicio un modelo sin género como entrada.

<!--
NOTAS (1 min) · Cierre honesto: la diapositiva que más credibilidad da.
- "Este modelo es una linterna, no un juez."
- Explicar por qué el género se mantuvo: quitarlo exigiría reentrenar y volver a evaluar con una prueba que ya se usó.
- Terminar con la frase del siguiente paso y dar las gracias.
-->

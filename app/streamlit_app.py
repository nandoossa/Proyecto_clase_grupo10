"""App: Predictor de resultados Pruebas Saber 11 en Antioquia (etapa 9).

- Carga `models/model.joblib` y `models/input_schema.json` desde ESTE repositorio. No se conecta a ninguna plataforma
  externa ni lleva credenciales.
- La persona llena un formulario en español; `proyecto.inference.form` lo traduce a las 21 columnas del modelo y
  `predict_score` valida contra el esquema. Si un dato es inválido, se explica qué corregir y no se muestra ningún puntaje.
- El aviso de uso responsable está siempre visible, con los límites de `models/ficha_modelo.md`.

Ejecutar en local (desde la raíz del repositorio):  streamlit run app/streamlit_app.py
"""
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proyecto.inference.form import (  # noqa: E402  (después de agregar src/ al path)
    SECTIONS,
    SIN_RESPUESTA,
    TYPICAL_ERROR,
    display_value,
    form_to_row,
    options,
    reference_range,
)
from proyecto.inference.predict import InputValidationError, load_model, predict_score  # noqa: E402
from proyecto.inference.schema import load_schema  # noqa: E402

MODEL_PATH = ROOT / "models" / "model.joblib"
SCHEMA_PATH = ROOT / "models" / "input_schema.json"
TITLE = "Predictor de resultados Pruebas Saber 11 en Antioquia"

# Cifras de models/ficha_modelo.md (prueba con 289 sedes nunca vistas, 5 nov 2026).
RESPONSIBLE_USE = """
**Uso responsable.** Esta estimación **orienta; no excluye**. La decisión final la toma una persona.

- **No** la uses para excluir, clasificar o etiquetar a estudiantes o colegios, ni la trates como el puntaje real.
- Solo vale para estudiantes de **calendario A en Antioquia**, con datos de **2022**. Fuera de eso no se ha validado.
- El modelo explica el **36 %** de la variación del puntaje (R² 0,363): hay estudiantes con errores mucho mayores que el
  típico.
- **El error no es igual para todos:** en **estrato 5** se equivoca en promedio **39,57 puntos**; en **hombres 35,74**
  frente a **31,40 en mujeres**; en colegios no oficiales 35,55 frente a 32,66 en los oficiales.
- Lo que más pesa en la estimación (edad, jornada del colegio) no es la causa del puntaje.
"""


@st.cache_resource
def get_model():
    return load_model(MODEL_PATH)


@st.cache_data
def get_schema() -> dict:
    return load_schema(SCHEMA_PATH)


def ask(field: str, label: str, schema: dict):
    """Un campo del formulario. Listas sin opción elegida al inicio, para notar si falta un dato obligatorio."""
    if field == "edad":
        age = st.number_input(label, value=None, step=1, placeholder="Por ejemplo, 17", key="edad")
        no_answer = st.checkbox(f"{SIN_RESPUESTA} (edad)", key="edad_sin_respuesta")
        return SIN_RESPUESTA if no_answer else age
    return st.selectbox(
        label,
        options(field, schema),
        index=None,
        placeholder="Elige una opción",
        format_func=lambda value: display_value(field, value, schema),
        key=field,
    )


def show_result(score: float, warnings: list[str]) -> None:
    low, high = reference_range(score)
    st.metric("Puntaje global estimado", f"{round(score)}")
    st.markdown(
        f"El modelo **se equivoca en promedio {TYPICAL_ERROR} puntos; como referencia, entre {low} y {high}** "
        "(MAE 33,3 con colegios que el modelo no vio)."
    )
    st.caption(
        "Ese rango no es un intervalo de confianza: el error típico es un promedio, y para algunos estudiantes el "
        "puntaje real queda fuera de él."
    )
    for message in warnings:
        st.warning(message)


def main() -> None:
    st.set_page_config(page_title=TITLE, page_icon="🎓", layout="wide")
    st.title(TITLE)
    st.caption("Estima el puntaje global de Saber 11 a partir de datos del colegio, del estudiante y del hogar.")

    if not MODEL_PATH.exists() or not SCHEMA_PATH.exists():
        st.error("Falta `models/model.joblib` o `models/input_schema.json`. Se generan en el notebook 08_registro_modelo.")
        st.stop()
    model, schema = get_model(), get_schema()

    with st.form("perfil"):
        answers = {}
        for column, (section, fields) in zip(st.columns(3), SECTIONS.items()):
            with column:
                st.subheader(section)
                for field, label in fields.items():
                    answers[field] = ask(field, label, schema)
        submitted = st.form_submit_button("Estimar", type="primary")

    if submitted:
        try:
            row = form_to_row(answers, schema)
            result = predict_score(row, model, schema)
        except InputValidationError as error:
            st.error(f"Revisa estos datos: {error}")
        else:
            show_result(float(result["puntaje_estimado"].iloc[0]), result.attrs.get("warnings", []))
    else:
        st.info(f"Completa los datos y pulsa **Estimar**. Si no conoces un dato, elige «{SIN_RESPUESTA}» donde aparece.")

    st.markdown(RESPONSIBLE_USE)


if __name__ == "__main__":  # `streamlit run` ejecuta el archivo como programa principal
    main()

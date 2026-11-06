# Feature Specification: Preparación del despliegue de la app (etapa 10)

**Feature Branch**: `008-deploy-readiness` (se trabaja en `main`)

**Created**: 2026-11-06

**Status**: Draft

**Input**: User description: "Preparación del despliegue de la app en Streamlit Community Cloud (etapa 10, clase 5), sin
desplegar todavía. Entradas: `material-del-curso/guias/streamlit-despliegue.md` y `reports/09_despliegue.md`. Cubre: lista de
requisitos del repo (repo público, `requirements.txt` en la raíz con versiones fijadas, `models/model.joblib` y
`models/input_schema.json` subidos, Python 3.12, sin `.env` ni datos personales), la app no consulta Databricks, rutas armadas
con `Path(__file__)`, revisión del código de la app y de `src/proyecto/inference/` con el subagente revisor-de-codigo-ia,
pruebas faltantes con escritor-de-pruebas, lista de verificación antes de la exposición y plan B. El despliegue real lo hace
el grupo después."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Saber si el repositorio está listo para publicarse (Priority: P1)

Antes de pulsar «Deploy», el grupo necesita una lista comprobada, punto por punto, de lo que la plataforma exige: que el
repositorio sea público, que el archivo de librerías esté en la raíz con versiones fijas, que el modelo y su esquema estén
subidos, que la versión de Python sea la misma del entrenamiento y que no haya credenciales ni datos personales.

**Why this priority**: si falta uno de esos puntos, el despliegue falla o expone información; es lo primero que se revisa.

**Independent Test**: cada punto de la lista tiene un comando o una comprobación que da «cumple» o «no cumple», sin
desplegar.

**Acceptance Scenarios**:

1. **Given** el repositorio en `main`, **When** se revisa la lista, **Then** cada requisito queda marcado como cumple / no
   cumple con la evidencia (comando y salida).
2. **Given** un archivo que la app necesita, **When** se revisa si Git lo ignora, **Then** se confirma que se sube.
3. **Given** el repositorio público, **When** se buscan correos, direcciones del espacio de trabajo, tokens y `.env`,
   **Then** no aparece ninguno.

---

### User Story 2 - Confiar en el código que se va a publicar (Priority: P1)

El grupo debe poder explicar y defender el código de la app y de la inferencia, saber si depende de la carpeta desde donde
se ejecuta, si intenta conectarse a Databricks y qué funciones no tienen prueba.

**Why this priority**: un error que en local no se ve (una ruta relativa, un import que en la nube no existe) rompe la app
en vivo.

**Independent Test**: el informe del revisor lista hallazgos con archivo y línea y las funciones sin prueba; las pruebas
nuevas pasan.

**Acceptance Scenarios**:

1. **Given** el código de la app, **When** se revisa, **Then** las rutas se arman desde la ubicación del archivo y no hay
   ninguna llamada a Databricks.
2. **Given** una función que limpia o transforma datos sin prueba, **When** se detecta, **Then** se escribe su prueba y pasa.

---

### User Story 3 - Llegar preparados a la exposición (Priority: P2)

El grupo necesita una lista de verificación para el día de la exposición y un plan B si la app falla en vivo.

**Independent Test**: la lista y el plan B están escritos en el informe de despliegue y cada punto se puede marcar.

### Edge Cases

- El modelo pesa más de lo que la plataforma o GitHub aceptan: se anota el tamaño y el límite.
- Una librería que la app importa no está en el archivo de librerías: el despliegue fallaría con «ModuleNotFoundError».
- La versión de la librería de modelos en la nube no coincide con la del entrenamiento: el modelo podría no cargar.
- La app «se duerme» por inactividad: se abre unos minutos antes de exponer.
- Faltan los datos procesados en la nube: la app no debe necesitarlos.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Comprobar, con evidencia, cada requisito de la guía: repositorio público; archivo de librerías en la raíz con
  versiones fijadas; modelo y esquema dentro del repositorio y no ignorados; Python 3.12; sin `.env` ni datos personales.
- **FR-002**: Comprobar que el archivo de librerías incluye todo lo que importan la app y la inferencia, con las mismas
  versiones del entrenamiento.
- **FR-003**: Comprobar que la app no consulta Databricks y que arma sus rutas desde la ubicación del archivo.
- **FR-004**: Revisar la app y la inferencia con el subagente revisor-de-codigo-ia y registrar sus hallazgos.
- **FR-005**: Escribir con el subagente escritor-de-pruebas las pruebas de las funciones que limpian o transforman datos y
  no tienen prueba; todas las pruebas deben pasar.
- **FR-006**: Comprobar que la app arranca en local desde la raíz del repositorio.
- **FR-007**: Dejar en el informe de despliegue la lista de verificación antes de la exposición y el plan B.
- **FR-008**: No desplegar: el despliegue real lo hace el grupo.
- **FR-009**: Actualizar la documentación general con el estado de la preparación.

### Key Entities

- **Requisito de despliegue**: nombre, evidencia (comando y resultado), cumple / no cumple, acción si no cumple.
- **Hallazgo de revisión**: archivo, línea, gravedad, descripción, corrección.

## Success Criteria *(mandatory)*

- **SC-001**: El 100 % de los requisitos de la guía tiene evidencia y veredicto.
- **SC-002**: 0 credenciales, correos, direcciones del espacio de trabajo o archivos `.env` en el repositorio público.
- **SC-003**: 0 funciones que limpian o transforman datos sin prueba; todas las pruebas pasan.
- **SC-004**: La app arranca en local sin errores.
- **SC-005**: La lista de verificación y el plan B están escritos antes de la exposición.

## Assumptions

- La plataforma es Streamlit Community Cloud (gratuita), con el repositorio `nandoossa/Proyecto_clase_grupo10`, rama
  `main`, archivo `app/streamlit_app.py`.
- La app de la etapa 9 (`specs/007-app-inference`) ya está construida y probada en local.
- El despliegue, el enlace público y la prueba en ventana privada los hace el grupo después.
- Los límites de tamaño de archivos de GitHub y de la plataforma se consultan en su documentación oficial.

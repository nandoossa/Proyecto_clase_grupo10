# Especificación del proyecto

> Plantilla. Complétenla en el grupo y manténganla actualizada. Claude la lee antes de generar
> código: lo que escriban aquí manda sobre cualquier otra suposición.

## 1. Grupo

| Integrante | Rol (datos / modelado / app / negocio) |
|---|---|
| | |
| | |
| | |

Nombre de la "startup": _______________   Repositorio (público): _______________

## 2. Caso de negocio

- **Pregunta de negocio** (una frase, que alguien sin formación técnica entienda):
- **¿Quién usará el resultado y qué decisión tomará con él?**
- **¿Qué cuesta equivocarse?** (cuál error es peor y por qué):

## 3. Datos

- **Fuente** (enlace de Kaggle, empresa, etc.): datos.gov.co — Resultados Saber 11 (recurso `kgxf-xxbe`),
  filtrado a periodo 20224 y departamento ANTIOQUIA. Se descarga a `data/raw/saber11_antioquia_2022.csv` con:
  `https://www.datos.gov.co/resource/kgxf-xxbe.csv?$where=periodo=%2720224%27%20AND%20cole_depto_ubicacion=%27ANTIOQUIA%27&$order=estu_consecutivo&$limit=200000`
- **Filas / columnas:** 144.766 filas descargadas = 72.383 estudiantes (cada fila viene duplicada en la fuente) / 51
- **Variable objetivo** (columna que queremos predecir o describir):
- **Tipo de problema:** ☐ clasificación  ☐ regresión  ☐ clusterización
- **¿Una misma entidad (cliente, paciente, empresa) aparece en varias filas?** ☐ no  ☐ sí → la partición
  será por: _______________
- **Datos personales o confidenciales presentes:** ☐ no  ☐ sí → se eliminarán/anonimizarán así:
- **Licencia o permiso de uso de los datos:** CC BY-SA 4.0 (Creative Commons Atribución-CompartirIgual 4.0
  Internacional), según los metadatos del recurso `kgxf-xxbe` en datos.gov.co (consultado el 31 oct 2026). Crédito al
  ICFES; las versiones modificadas de los datos que se publiquen deben usar la misma licencia.

## 4. Métrica

- **Métrica principal:** _______________   **Por qué esa y no otra:**
- **Métricas secundarias:**
- **Línea base** (qué resultado obtiene una regla simple o un modelo trivial):

## 5. Riesgos

- Fuga de información posible:
- Sesgos o equidad:
- Datos faltantes o de mala calidad:
- Límites de lo que el modelo puede decir:

## 6. Entregables y fechas

| Hito | Contenido | Fecha |
|---|---|---|
| H1 | Ficha aprobada, EDA y preprocesamiento reproducible | Cierre de la clase 2 (vie 30 oct) |
| H2 | Torneo, optimización con tracking, modelo registrado, repo modular, app local | Cierre de la clase 4 (jue 5 nov) |
| H3 | App desplegada y presentación (≤ 5 diapositivas) | Clase 5 (vie 6 nov) |
| H4 | Informe técnico final (hasta 8 días tras la última clase) | Domingo 15 nov |

## 7. Decisiones tomadas (agréguenlas a medida que avancen)

| Fecha | Decisión | Motivo |
|---|---|---|
| | | |

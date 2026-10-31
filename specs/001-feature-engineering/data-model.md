# Data Model: Variables y preprocesamiento del modelo (etapa 4)

## Entrada: tabla limpia (salida de la etapa 3)

Una fila = un estudiante de calendario A, Antioquia, periodo 20224. Columnas que usa esta etapa:

| Columna | Tipo | Valores |
|---|---|---|
| `edad` | número | años aproximados; vacío si < 13 (decisión 4) |
| `fami_estratovivienda` | número | 1–6; vacío (nunca 0) si «Sin Estrato» o sin dato (regla 7b, aprobada 31 oct 2026) |
| `sin_estrato` | número 0/1 | 1 si respondió «Sin Estrato»; 0 si respondió un estrato o no respondió |
| `fami_personashogar` | número | 1–5 («1 a 2» … «9 o más»); vacío si sin dato |
| `fami_cuartoshogar` | número | 1–6 («Uno» … «Seis o mas»); vacío si sin dato |
| `cole_area_ubicacion`, `cole_bilingue`, `cole_caracter`, `cole_genero`, `cole_jornada`, `cole_naturaleza`, `cole_sede_principal` | texto | categorías del colegio; `cole_bilingue` y `cole_caracter` con vacíos |
| `estu_genero`, `estu_nacionalidad`, `estu_privado_libertad` | texto | categorías del estudiante |
| `estu_tipodocumento` | texto | puede venir en la tabla, pero **nunca es predictor** (decisión del grupo, equidad) |
| `fami_educacionmadre`, `fami_educacionpadre` | texto | 10 niveles + «No sabe», «No Aplica»; vacíos |
| `fami_tieneautomovil`, `fami_tienecomputador`, `fami_tieneinternet`, `fami_tienelavadora` | texto | «Si», «No»; vacíos |
| `cole_cod_mcpio_ubicacion`, `estu_cod_reside_mcpio` | código (entero en el CSV) | 125 y 173 municipios |
| `cole_cod_dane_sede` | código | solo para agrupar; **nunca predictor** |
| `punt_global` | número | objetivo, 100–477; **nunca predictor** |

## Variables nuevas (`add_features`)

| Variable | Tipo | Regla | Vacío cuando |
|---|---|---|---|
| `n_bienes_hogar` | número 0–4 | cuenta de «Si» en las 4 columnas `fami_tiene*` | las 4 están vacías |
| `educacion_max_padres` | número 0–9 | máximo de la escala de `especificaciones/04-features.md`, sección 3 («No sabe» y «No Aplica» no cuentan) | ninguno de los dos tiene nivel conocido |
| `personas_por_cuarto` | número > 0 | punto medio de personas ÷ cuartos | falta un dato o cuartos = 0 |
| `vive_en_mcpio_colegio` | número 0/1 | 1 si los dos códigos de municipio son iguales | falta un código |

## Salida del preprocesador (`build_preprocessor`)

Matriz numérica sin vacíos ni infinitos:
- numéricas imputadas (mediana) + indicadores de vacío, opcionalmente estandarizadas;
- one-hot de categóricas, con columnas «sin respuesta» y «poco frecuente» cuando aplica.

## Columnas prohibidas como predictor

`punt_global`, `punt_matematicas`, `punt_lectura_critica`, `punt_sociales_ciudadanas`, `punt_c_naturales`, `punt_ingles`,
`desemp_ingles`, `estu_estadoinvestigacion`, `estu_consecutivo`, `estu_fechanacimiento`, `cole_cod_dane_sede`,
`cole_cod_dane_establecimiento`, `cole_codigo_icfes`, `cole_nombre_establecimiento`, `cole_nombre_sede`,
`estu_tipodocumento` (16 columnas).

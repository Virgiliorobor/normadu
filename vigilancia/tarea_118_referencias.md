# Tarea: 118 referencias a entradas que no existen en el corpus

**Fecha:** 22-10-2026 · **Quién lo pidió:** el owner (respuesta C3 a la propuesta de vigilancia, vía dev-os) · **Estado:** diagnóstico, sin corregir.

`scripts/verificar.py` avisa (sin fallar) de 118 referencias `{ord, art}` cuyo destino `ORD-art` no es un id de `data/`. Todas estaban antes del 22-10-2026, salvo una (grupo F). Se revisaron una por una contra la correlación o el texto de origen.

| Grupo | Cuántas | Qué pasa | Origen del error | Corrección propuesta |
|---|---|---|---|---|
| A | 89 | RGCE → anexos 4–21, 23, 25–29 de las RGCE | No es error: esos anexos no están cargados (solo 1, 2, 22, 24 y 30) | `verificar.py`: separar como «anexo no cargado» y no contarlo como roto. El visor ya puede mostrarlos como chip gris |
| B | 15 | RLA-204 → LA-204, … RLA-235 → LA-235 | `extraer_referencias.py` toma el encabezado propio «Artículo 204.» y, como la frase dice después «de la Ley», lo manda a la LA (la LA termina en el art. 203) | Ignorar el encabezado «Artículo N.» al inicio del texto de cada entrada |
| C | 4 | RGCE-1.3.1 → RGCE-3 y RGCE-6; RGCE-1.12.5 → RGCE-2019; RGCE-3.1.38 → RGCE-22 | `parse_rgce.parse_correlaciones`: «Capítulo 3.6.» se parte en 3 y 6; «RGCE para 2019 1.4.13.» toma el año como regla; «1.9.17. Anexo 22» (sin coma en la fuente) da RGCE-22 | Reconocer «Capítulo N.N.» (sin referencia o con referencia al capítulo); «RGCE para AAAA» → EXT; buscar «Anexo» dentro del mismo trozo |
| D | 2 | RGCE-4.2.2 → RLA-1.2.1 y RLA-1.2.2 | La fuente omite la coma: «Reglamento 100, 102, 152 RGCE 1.2.1.»; el token RGCE queda a media pieza y los números siguen como del Reglamento | Detectar un token de ordenamiento (RGCE, CFF, Ley…) en cualquier posición del trozo, no solo al inicio |
| E | 2 | RGCE-1.6.16 → RGCE-anexo-III y RGCE-anexo-I | «Resolución de la Decisión 2.2.3., Anexo III, artículo 14» y «Resolución del TLCAELC …, Anexo I, artículo 15»: son anexos de esas resoluciones de tratados, no de las RGCE | Tras un ordenamiento externo nombrado, «Anexo N» y «artículo N» pertenecen a ese externo (EXT) |
| F | 1 | RGCE-3.1.25 → IMMEX-42 | **Regresión del 22-10-2026** (corrección de «Decreto IMMEX N»): en «Decreto IMMEX Anexo I-II, Reglamento, 42» el «Reglamento» sin número ya no cambia de ordenamiento y el 42 se atribuye al Decreto IMMEX. Antes se perdía; debe ser RLA-42 | Un token de ordenamiento sin número («Reglamento,») también cambia `ord_actual` |
| G | 2 | RGCE-4.2.20 → LA-137-bis; RGCE-4.5.27 → LA-121-I | Normalización: «137 Bis-7» queda como `137-bis` (el id es `LA-137-bis-7`); «121-I» es art. 121, fracción I | `_num_norm`: conservar el número tras Bis; quitar fracción romana tras guion cuando el artículo existe sin ella |
| H | 1 | LA-203 → LA-95-A | El texto cita «los artículos 95 y 95-A de la Ley que se abroga» (ley de 1981) | En `extraer_referencias.py`, «de la Ley que se abroga» no apunta a la LA vigente (EXT o nada) |
| I | 2 | RCSE-2.4.11 → RCSE-3.7.3 y RCSE-3.7.5 | «reglas 3.7.3. y 3.7.5, de las Reglas del SAT»: son reglas de las RGCE | En RCSE, «de las Reglas del SAT» → RGCE |

Total: 89 + 15 + 4 + 2 + 2 + 1 + 2 + 1 + 2 = 118.

## Orden propuesto

1. F primero (regresión de hoy; una línea en `parse_rgce.py`).
2. B, C, D, E, G, H, I: cambios en `parse_rgce.py` y `extraer_referencias.py`, cada uno con una prueba de la correlación que lo causó.
3. A: en `verificar.py`, reportar aparte las referencias a anexos no cargados.
4. Correr `python scripts/actualizar.py`. Resultado esperado: 0 referencias rotas y 89 a anexos no cargados. Ningún texto cambia, solo `referencias`, así que la verificación de historial no se afecta.

Es trabajo de una sesión, en rama y sin merge hasta que el owner lo apruebe.

# Registro de fuentes externas — memo trato preferencial T-MEC (transferencias virtuales de desperdicio)

**Fecha de descarga:** 21 de agosto de 2026
**Contexto:** el memo `opiniones/2026-08-20_memo_trato_preferencial_virtuales_desperdicio.md` cita varios ordenamientos externos al corpus *normadu*, marcados "(externo — verificar)". Este registro documenta las fuentes originales descargadas a `fuentes/`, lo que ya quedó verificado y lo que queda pendiente para un agente futuro.

---

## Archivos agregados

| Archivo | Contenido | Fuente original |
|---|---|---|
| `tmec_cap04_reglas_origen.pdf` | T-MEC, Capítulo 4 (Reglas de Origen), texto en español | https://www.economia.gob.mx/files/IV_%20Reglas%20de%20Origen.pdf |
| `lisr.pdf` | Ley del Impuesto Sobre la Renta, texto vigente completo | https://www.diputados.gob.mx/LeyesBiblio/pdf/LISR.pdf |
| `resolucion_tmec_dof_20200630.html` / `.txt` | Resolución en materia aduanera del T-MEC, publicación original (5 títulos, 87 reglas) | https://dof.gob.mx/nota_detalle.php?codigo=5595797&fecha=30/06/2020 |
| `extracto_resolucion_tmec_reglas_17a21.txt` | Texto íntegro de las reglas 17.- a 21.- (misma condición; originarias fuera del art. 2.5; transferencias IMMEX) | extraído del archivo anterior |
| `resolucion_tmec_mod_dof_20231222.html` / `.txt` | Resolución que modifica la Resolución T-MEC (certificación de origen por el importador, reglas 25.3, 30, 33, 42, 63, 85, 87, Anexo 1) | https://dof.gob.mx/nota_detalle.php?codigo=5712299&fecha=22/12/2023 |
| `reglamentaciones_uniformes_tmec_mod_dof_20210813.pdf` | Modificación a las Reglamentaciones Uniformes del T-MEC (capítulos 4-7), DOF 13-08-2021 | https://www.e-casa.com.mx/dof/2021/ago/13082021_ru_4567_tmec.pdf |
| `decreto_tigie_dof_20251229.html` / `.txt` | Decreto que reforma 1,463 fracciones arancelarias de la TIGIE (vigente 01-01-2026) | https://www.dof.gob.mx/nota_detalle.php?codigo=5777376&fecha=29/12/2025 |

Nota de numeración: las reglas de la Resolución T-MEC usan el formato `17.-` (número, punto y guion); búsquedas por `regla 17` o `\n17\.` no las encuentran.

## Verificaciones ya realizadas (21-08-2026)

1. **Decreto TIGIE 29-12-2025.** Las fracciones de chatarra quedaron al 35% de arancel de importación: 7204.10.01 ("Desperdicios y desechos, de fundición"), 7204.29.99, 7204.30.01, 7204.41.01, 7204.49.99 y 7204.50.01. La fracción 9807.00.01 **no** aparece en el decreto — su tasa (exenta) no fue modificada. Firmado el 23-12-2025, publicado el 29-12-2025.
2. **Resolución T-MEC, regla 17.-** Implementa el artículo 2.5(6)(b) del Tratado: mercancías retornadas o exportadas "en la misma condición" quedan fuera del artículo 2.5; enumera las operaciones que no alteran materialmente la mercancía (limpieza, corte, empaque, etiquetado, etc.).
3. **Resolución T-MEC, regla 18.-** Implementa el artículo 2.5(6)(e): la restricción del artículo 2.5 **no aplica a mercancías originarias** introducidas bajo programas de diferimiento cuando sean (I) retornadas o exportadas a EUA/Canadá, (II) **utilizadas como material en la producción de otra mercancía posteriormente retornada o exportada**, o (III) sustituidas por idéntica o similar. Condiciones: cumplir la regla de origen al ingreso, declarar a nivel de fracción arancelaria que califica como originaria (claves de país de origen del Anexo 22), certificación de origen válida y, en drawback, tasa preferencial aplicada. Incluye plazo de cura de 1 año (art. 5.11 del Tratado). La fracción II de esta regla cubre con exactitud el tramo de la empresa receptora: desperdicio originario importado temporalmente (virtual) y usado como materia prima de mercancía que después se retorna.
4. La modificación DOF 22-12-2023 **no** tocó las reglas 17.- a 21.-; se centró en la certificación de origen por el importador.

## Pendientes para el siguiente agente

1. **T-MEC arts. 4.2 y 4.3(h):** verificar la cita textual del memo (sección A) contra `tmec_cap04_reglas_origen.pdf` — en particular la letra exacta del inciso de desechos y desperdicios (confirmar si es (h) y su redacción en la versión oficial en español).
2. **LISR arts. 181 y 182:** verificar contra `lisr.pdf` lo afirmado en la sección E del memo: fracc. I (mercancías suministradas por el residente en el extranjero, importación temporal, retorno "incluso mediante operaciones virtuales"; tolerancia de mercancías nacionales condicionada a exportarse conjuntamente), fracc. IV (30% de maquinaria y equipo propiedad del residente en el extranjero), art. 182 (porcentajes 6.9% de activos / 6.5% de costos y gastos) y la eliminación de la opción de resolución particular (reforma DOF 12-11-2021).
3. **Reglas 19.- a 21.-:** revisar el texto completo en `extracto_resolucion_tmec_reglas_17a21.txt` contra lo que el memo afirma de las reglas 19 (transferencias entre IMMEX con exención) y 20-21 (diferimiento y proporción), citadas por las reglas 1.6.13 y 1.6.17 de las RGCE.
4. **Reglamentaciones Uniformes originales** (DOF 30-06-2020): solo se tiene la modificación del 13-08-2021. Conseguir la publicación original y verificar las secciones 1 y 3 que cita CAAAREM y la sección de mercancías totalmente obtenidas.
5. **Modificaciones adicionales a la Resolución T-MEC:** confirmar si entre 2020 y 2026 hubo otras resoluciones modificatorias además de la del 22-12-2023, y compilar el texto vigente.
6. **Integración al corpus (opcional):** decidir si la Resolución T-MEC se parsea a `data/` con el esquema del corpus (un JSON por ordenamiento, id sugerido `RTMEC`) y se registra en `data/index.json`. Los PDF (T-MEC cap. 4, LISR) quedarían como fuentes de consulta sin parsear, salvo decisión en contrario.
7. **Actualizar el memo:** con las verificaciones hechas, sustituir los "(externo — verificar)" ya resueltos por citas con fecha de publicación en el DOF, y añadir al cuadro de fundamentos la regla 18.-, fracción II (es el sustento más exacto para el tramo de la receptora).

**Advertencia:** estos archivos son copias de trabajo. Para sustentar legalmente actos o resoluciones debe utilizarse la publicación del Diario Oficial de la Federación.

---

# Registro de fuentes externas — aviso de adición de fracciones al Registro CIVA (ITT Cannon, 2026-10-08)

**Fecha de descarga:** 8 de octubre de 2026
**Quién lo pidió y para qué:** el owner (confirmado en la sesión principal: "si guardalas"), para el asunto ITT Cannon de México, CIVA rubro AA, sobre el aviso de adición de fracciones (regla 7.2.1, fr. X; ficha 62/LA). Documento que las cita: `C:\Users\Jaime V. Rob\Dev\customs-work\work\itt\CIVA\2026-10-08_comparativo-adicion\fundamentos.md`. Descargadas por el agente `normativa`; copiadas aquí byte por byte (hash verificado) por la sesión principal.

## Archivos agregados

| Archivo | Contenido | Fuente original | Publicación |
|---|---|---|---|
| `rgce2026_anexo2_dof_20260112.pdf` / `.txt` / `_layout.txt` | Anexo 2 de las RGCE 2026 (Trámites de comercio exterior), versión original; ficha 62/LA en `.txt` línea 8197 y en `_layout.txt` línea 10444 | https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2026/rgce/anexos/Anexo2delasRGCEpara2026.pdf (copia del minisitio SAT; el servidor marca Last-Modified 06-10-2026, pero el contenido es la publicación del DOF 12-01-2026, sin la 2a RM) | DOF 12-01-2026 |
| `rgce2026_2rm_anexos_1_2_22_dof_20260922.doc` / `.txt` | Segunda Resolución de Modificaciones a las RGCE 2026 y anexos 1, 2 y 22. Incluye la Primera Modificación al Anexo 2 (ficha 62/LA vigente en las líneas 638-696 del `.txt`). Resolutivo PRIMERO en la línea 5; Título 7 en las líneas 54-82; TERCERO y Transitorios en las líneas 88-94 | https://sidof.segob.gob.mx/notas/getDoc/5799243 (ficha: https://sidof.segob.gob.mx/notas/5799243) | DOF 22-09-2026; en vigor el 23-09-2026 (Transitorio Primero) |

## Verificado (08-10-2026)

1. La 2a RM reforma, en el Título 7, solo la 7.1.4 (quinto párrafo), la 7.1.5 (tercer párrafo) y la 7.2.1 (tercer párrafo fr. I y cuarto párrafo fr. IV). La 7.2.1 fr. X y el último párrafo no cambian.
2. Ficha 62/LA: la adición de fracciones pasa de la fr. X a la IX. El plazo "al menos un mes previo" es igual. Requisitos iguales (listado de fracciones con descripción y diagrama de flujo con 5 contenidos). "Plazo máximo para cumplir con la información solicitada" pasa de "Veinte días." a "No aplica.". El documento pasa de "Acuses de recepción de trámite y de aceptación." a "Acuse de recibo.". Se elimina la fr. II de "Información adicional" (requerimiento de 20 días y cancelación).

## Pendiente

1. Cotejar contra la imagen o el PDF del DOF del 22-09-2026 (las tablas del .doc pueden verse mal; el campo de seguimiento aparece como "No aplica.").
2. Localizar la URL de la nota del DOF del Anexo 2 original (12-01-2026).
3. Verificar si la ficha 62/LA reformada se anticipó en el Portal del SAT (2a versión anticipada del 04-06-2026, según fuente secundaria) y su efecto conforme a la regla 1.1.2.
4. Revisar si hay resoluciones de modificaciones posteriores al 22-09-2026.
5. Integrar a `data\` (aplicar la 2a RM a rgce.json según README "Cómo actualizar"): solo cuando el owner lo pida.

**Advertencia:** copias de trabajo. El sustento legal es la publicación del DOF.

---

# Registro de fuentes externas — actualización del corpus: 2a RM RGCE 2026, Anexos 1 y 2, IMMEX (2026-10-16)

**Fecha de descarga:** 16 de octubre de 2026
**Quién lo pidió y para qué:** el owner, vía dev-os (respuesta A1 en el gate de la especificación normadu-mcp, 16-10-2026, y respuestas a/b/c retransmitidas por dev-os-8c): poner al día el corpus de `data\`: aplicar la 2a RM (reglas, Glosario, Anexos 1, 2 y 22) con historial; cargar los Anexos 1 y 2; buscar en DOF y SAT resoluciones posteriores al 22-09-2026 (aprobada su descarga de fuente oficial); llenar el Anexo I BIS del Decreto IMMEX con su texto real.
**Estado:** integradas a `data\` (rama `worktree-rgce-2a-rm`), salvo la 3a RM anticipada (ver abajo).

## Archivos agregados

| Archivo | Contenido | Fuente original | Publicación | SHA-256 (original) |
|---|---|---|---|---|
| `rgce2026_anexo1_dof_20260108.pdf` / `.txt` / `_layout.txt` | Anexo 1 de las RGCE 2026 (Formatos y modelos), versión original. `.txt` = pdftotext; `_layout.txt` = pdftotext -layout (el que usa `parse_anexos.py`) | https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2026/rgce/anexos/Anexo1delasRGCEpara2026.pdf | DOF 08-01-2026 | 89f10ba7…fa830 |
| `rgce2026_anexo1_dof_20260108.doc` | La misma publicación descargada del DOF; solo contiene imágenes de página (por eso el texto se toma del PDF del SAT) | https://sidof.segob.gob.mx/notas/getDoc/5777997 | DOF 08-01-2026 | f098a1b1…0e742 |
| `rgce2026_2rm_anexo1_mod1_dof_20260922.pdf` / `.txt` / `_layout.txt` | Primera Modificación al Anexo 1 (2a RM): Contenido (E15; F1, F3), I-a)-3 derogado, formatos E15 (nuevo), F1 y F3 | https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2026/rgce/anexos/1raModificacionAnexo1delasRGCE2026.pdf | DOF 22-09-2026 | 3cb2a736…67d78 |
| `rgce2026_2rm_anexo2_mod1_dof_20260922.pdf` / `.txt` | Primera Modificación al Anexo 2 (2a RM): I-a)-3 derogado y 37 fichas reformadas (12, 20, 53, 55, 56, 58, 61, 62, 65, 66, 67, 68, 73, 75, 77, 80, 81, 82, 91–96, 98–102, 104, 108, 109, 111, 114, 119, 144 y 147/LA) | https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2026/rgce/anexos/1raModificacionAnexo2delasRGCE2026.pdf | DOF 22-09-2026 | 160bc761…fd79bd |
| `rgce2026_2rm_anexo22_mod2_dof_20260922.pdf` / `.txt` | Segunda Modificación al Anexo 22 (2a RM): apéndices 6, 8 (AO, EX, GA), 9 (C1) y 13 | https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2026/rgce/anexos/2daModificacionAnexo22delasRGCE2026.pdf | DOF 22-09-2026 | 7093c4ba…fd61d41 |
| `rgce2026_2rm_anexos_1_2_22_dof_20260922_celdas.txt` | Nueva extracción del `.doc` del DOF ya registrado (Word, texto sin formato cp1252 → UTF-8): una celda de tabla por línea. La usa `aplicar_modificaciones.py` para reglas, Glosario, Transitorio y Anexo 22. El `.txt` anterior no se tocó | (mismo `.doc`, SIDOF 5799243) | DOF 22-09-2026 | — |
| `rgce2026_3rm_anticipada1_sat_20260930.pdf` / `.txt` | **3a RM RGCE 2026, primera versión anticipada** (Portal del SAT, regla 1.1.2): reforma el Transitorio Décimo Primero (plazo al 31-10-2026 y calendario por régimen de la manifestación de valor, del 01-11-2026 al 15-01-2027) y anuncia la 3a Modificación al Anexo 22 | https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2026/rgce/anticipadas/3aRMRGCE_2026_PrimeraAnticipada.pdf | Portal SAT 30-09-2026; **no publicada en el DOF** al 15-10-2026 | 01df68a8…7bf120 |
| `rgce2026_3rm_anexo22_mod3_anticipada1_sat_20260930.pdf` / `.txt` | 3a Modificación al Anexo 22, primera versión anticipada: apéndice 9, STPS, clave CL "Certificado Laboral para la Agroexportación" | https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2026/rgce/anticipadas/3raModificacionAnexo22_3raRMRGCE_2026_PrimeraVersionAnticipada.pdf | Portal SAT 30-09-2026; no publicada en el DOF | 88866771…e067d78 |
| `immex_dof_20160106.doc` / `.txt` | Decreto por el que se modifica el diverso para el Fomento de la IMMEX. Artículo SEGUNDO: reforma los Anexos I y II y deroga los Anexos I BIS, I TER y III | https://sidof.segob.gob.mx/notas/getDoc/5422211 (ficha: https://sidof.segob.gob.mx/notas/5422211) | DOF 06-01-2016 | a6d8e2bc…2d415ad |

## Verificado (16-10-2026)

1. **Resoluciones posteriores al 22-09-2026.** En el DOF no hay 3a RM de las RGCE 2026 al 15-10-2026 (índice de publicaciones DOF de SNICE, consultado el 16-10-2026: lo último de SHCP en la materia es la 2a RM del 22-09-2026). El minisitio del SAT solo tiene la 3a RM como primera versión anticipada (30-09-2026). Se descargó y registró, pero **no se aplicó a `data\`**: no es publicación del DOF; surte efectos solo en términos de la regla 1.1.2.
2. **Cotejo de lo aplicado contra los compilados del SAT** (Compilado 2a RM RGCE, Compilado Anexo 2 y Compilado Anexo 22, 22-09-2026; descargados solo para cotejo, no guardados aquí). Las 10 reglas, el Glosario III-40 y el Transitorio Décimo Primero coinciden palabra por palabra (las únicas diferencias son de paginación). Las 37 fichas reformadas del Anexo 2 coinciden salvo URLs y teléfonos partidos por renglón. Las otras 113 fichas también coinciden con el compilado (no se omitió ninguna reforma). Anexo 22: el apéndice 13 coincide celda por celda; la clave AO queda antes de AP, igual que en el compilado; C1 coincide; las celdas que se quitaron del apéndice 6 ya no aparecen en el compilado. El compilado del Anexo 1 no está disponible (la liga del minisitio da error).
3. **IMMEX, Anexo I BIS.** Texto vigente: "Se deroga." Derogado (junto con I TER y III) por el Artículo SEGUNDO del Decreto DOF 06-01-2016 (cotejado en el `.doc` del DOF); el compilado SNICE lo anota como "DOF 01-01-2016". Del Anexo IV, el compilado solo dice "Se deroga." sin nota del decreto.

## Pendiente

1. Cuando el DOF publique la 3a RM, descargarla del DOF y aplicarla con el mismo procedimiento (Transitorio Décimo Primero y apéndice 9 del Anexo 22, clave CL).
2. Anexo 1: varios formatos están publicados como imagen (D2–D5, D7; y los rótulos de B7, B14, B15, B17, C1, D1, D9, E2 y E14 no salen en el texto del PDF). Su entrada en `rgce.json` lleva `nota_fuente`; para esos formatos debe consultarse el PDF.
3. Anexo 1: la tabla del Contenido conserva su texto original; los renglones E15, F1 y F3 reformados se consignan en `notas_reforma` de la entrada "Anexo 1".
4. La clave C1 del apéndice 9 del Anexo 22 entra en vigor en términos del Transitorio Único del Acuerdo SE del DOF 28-05-2026 (Transitorio Segundo de la 2a RM); confirmar su fecha de vigencia.
5. Identificar el decreto que derogó el Anexo IV del Decreto IMMEX.

**Advertencia:** copias de trabajo. El sustento legal es la publicación del DOF.

---

# Registro de fuentes externas — puesta al día del corpus y vigilancia (2026-10-22)

**Fecha de descarga:** 22 de octubre de 2026
**Quién lo pidió y para qué:** el owner, vía dev-os (tarea del 22-10-2026): revisar el DOF para cada ordenamiento de `data\index.json`, poner al día el corpus con historial (al menos RCSE, Acuerdo SE del 28-09-2026 y 3a RM RGCE solo si está en el DOF) y proponer un proceso de vigilancia.
**Estado:** los tres Acuerdos SE se integraron a `data\reglas_se.json` en la rama `corpus-update-2026-10-22` (sin merge). Ninguna otra publicación del DOF reforma los ordenamientos del corpus.

## Archivos agregados

| Archivo | Contenido | Fuente original | Publicación | SHA-256 (.doc) |
|---|---|---|---|---|
| `reglas_se_mod_dof_20260528.doc` / `.txt` | Acuerdo que modifica las Reglas y criterios SE: adiciona 2.2.4 fr. VI, regla 2.2.19 BIS (permiso previo de importación de azúcar), Anexo 2.2.1 numeral 8 TER y Anexo 2.2.2 numeral 8. `.txt` = Word, texto sin formato cp1252 → UTF-8 | https://sidof.segob.gob.mx/notas/getDoc/5788843 (nota: https://www.dof.gob.mx/nota_detalle.php?codigo=5788843&fecha=28/05/2026) | DOF 28-05-2026; en vigor cuando la DGFCCE comunique en el SNICE la liberación del trámite en la Ventanilla Digital (Transitorio Único) | 65617249…36c0781 |
| `reglas_se_mod_dof_20260529.doc` / `.txt` | Acuerdo que modifica las Reglas y criterios SE: 1.2.1 (adiciona XLVI BIS PLATIICA, deroga LXXI SINEC), 2.4.3 segundo párrafo, 2.4.6 fr. I y párrafos 2o y 3o, 2.4.11 fr. IX y IX BIS segundo párrafo; Anexo 2.4.1 numerales 1 y 3 (y elimina 8413.60.01) | https://sidof.segob.gob.mx/notas/getDoc/5788992 (nota: https://www.dof.gob.mx/nota_detalle.php?codigo=5788992&fecha=29/05/2026) | DOF 29-05-2026; en vigor el 30-05-2026 | bde62b94…4771289451 |
| `reglas_se_mod_dof_20260928.doc` / `.txt` | Acuerdo que modifica las Reglas y criterios SE: solo el numeral 1 del Anexo 2.4.1 | https://sidof.segob.gob.mx/notas/getDoc/5799697 (nota: https://www.dof.gob.mx/nota_detalle.php?codigo=5799697&fecha=28/09/2026) | DOF 28-09-2026; en vigor el 29-09-2026, salvo NOM-221-SCFI-2017 y NOM-221/2-SCFI-2018 (30 días hábiles) | aca12abd…2d6147e3 |

## Verificado (22-10-2026)

1. **DOF revisado día por día** con `scripts\vigilar_dof.py` (API pública de SIDOF), desde la última reforma de cada ordenamiento hasta el 22-10-2026: LA desde 19-11-2025, RLA desde 23-02-2026, RGCE desde 22-09-2026, RCSE desde 02-04-2026, IMMEX desde 28-08-2025. Reporte: `vigilancia\ultimo_reporte.md`.
2. **RGCE:** no hay publicación en el DOF posterior a la 2a RM (22-09-2026). La 3a RM sigue solo como primera versión anticipada del SAT (30-09-2026); el minisitio no tiene versiones anticipadas nuevas al 22-10-2026.
3. **LA y RLA:** la portada de los PDF de LeyesBiblio dice "Última reforma publicada DOF 19-11-2025" (LA; cantidades actualizadas por RGCE DOF 27-12-2025) y "DOF 23-02-2026" (RLA), igual que el corpus. El Acuerdo de Lineamientos del art. 159 bis LA (DOF 31-03-2026) no reforma la Ley.
4. **IMMEX:** el Decreto DOF 26-03-2026 (nota 5783297) solo adiciona la fracción 7302.10.02 al artículo Décimo Cuarto (arancel-cupo) del Decreto DOF 18-11-2022; no reforma el texto del Decreto IMMEX. Los avisos de programas cancelados o suspendidos no son reformas.
5. **RCSE:** los textos nuevos se tomaron del `.txt` del DOF; las tablas de los anexos del Acuerdo no se cargan en `data\` (como antes) y sus cambios solo quedan en `data\modificaciones.json`.

## Pendiente

1. Confirmar en el SNICE el comunicado de liberación del trámite de permiso previo de azúcar (fija la entrada en vigor de 2.2.4 fr. VI, 2.2.19 BIS y, por remisión del Transitorio Segundo de la 2a RM, la clave C1 del apéndice 9 del Anexo 22). Fuentes secundarias (prensa y consultoras, no verificadas, 22-10-2026) mencionan un boletín SNICE del 21-08-2026 con inicio el 28-09-2026 y transición para la 2106.90.99 hasta el 02-11-2026. No se descargó ni se aplicó: falta el documento oficial.
2. Cuando SNICE publique un compilado de las Reglas SE posterior al 28-09-2026, cotejarlo con lo aplicado y reemplazar el compilado.
3. Cotejar contra la imagen o el PDF del DOF las tablas de los `.doc` (el Word puede desordenar tablas).

**Advertencia:** copias de trabajo. El sustento legal es la publicación del DOF.

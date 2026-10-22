# Normadu — Normativa Aduanera Mexicana

Directorio consultable de las disposiciones legales aplicables al comercio exterior mexicano, con referencias cruzadas entre ordenamientos. Visor 100% estático: abre `normativa.html` en el navegador, sin servidor ni dependencias.

## Ordenamientos integrados

| Id | Ordenamiento | Fuente | Vigencia |
|----|--------------|--------|----------|
| LA | Ley Aduanera (277 artículos) | Cámara de Diputados (LeyesBiblio) | últ. reforma DOF 19-11-2025 |
| RLA | Reglamento de la Ley Aduanera (282 artículos) | Cámara de Diputados (LeyesBiblio) | últ. reforma DOF 23-02-2026 |
| RGCE | Reglas Generales de Comercio Exterior 2026 (550 reglas + glosario) | DOF 27-12-2025 / minisitio SAT | 1a RM (DOF 14-05-2026) y 2a RM (DOF 22-09-2026) aplicadas |
| — | RGCE Anexo 1 (formatos y modelos: contenido + 60 formatos A1…M1.11) | DOF 08-01-2026 (PDF minisitio SAT) | 1a Modificación aplicada (DOF 22-09-2026: E15, F1, F3, I-a-3) |
| — | RGCE Anexo 2 (fichas de trámite: contenido + 150 fichas 1/LA…150/LA) | DOF 12-01-2026 (PDF minisitio SAT) | 1a Modificación aplicada (DOF 22-09-2026: 37 fichas, I-a-3) |
| — | RGCE Anexo 22 (instructivo del pedimento + 22 apéndices) | DOF 15-01-2026 | 1a Modificación (DOF 20-05-2026, clave AL) y 2a Modificación (DOF 22-09-2026: ap. 6, 8, 9, 13) aplicadas |
| — | RGCE Anexo 24 (control de inventarios IMMEX) | DOF 15-01-2026 | vigente |
| — | RGCE Anexo 30 (SCCCyG — control de créditos y garantías IVA/IEPS) | DOF 15-01-2026 | vigente |
| RCSE | Reglas y Criterios de Comercio Exterior SE (199 reglas) | Compilado SNICE al 02-04-2026 + Acuerdos DOF | Acuerdos SE DOF 28-05-2026 (2.2.4, 2.2.19 BIS; vigor condicionado), 29-05-2026 (1.2.1, 2.4.3, 2.4.6, 2.4.11) y 28-09-2026 (solo Anexo 2.4.1) aplicados |
| IMMEX | Decreto IMMEX completo (34 artículos + 6 Bis, transitorios y anexos I–IV) | Compilado SNICE | al 28-08-2025 (Anexos I BIS, I TER y III derogados, DOF 06-01-2016) |

Pendiente de publicación en el DOF (revisado el 22-10-2026): 3a RM RGCE 2026 (solo versión anticipada en el Portal del SAT, 30-09-2026; registrada en `fuentes\`, no aplicada). LA, RLA e IMMEX no tienen reformas en el DOF posteriores a su fecha de corte (revisión día por día en SIDOF y portada de LeyesBiblio, 22-10-2026).

Los anexos del Acuerdo SE (tablas de fracciones arancelarias: 2.2.1, 2.4.1, etc.) no se cargan en el visor; se consultan en el PDF compilado de SNICE.

## Estructura

```
fuentes/     Textos fuente (DOF .doc→.txt, PDF SNICE/SAT→.txt); REGISTRO_FUENTES_EXTERNAS.md
data/        JSON por ordenamiento + modificaciones.json (registro de resoluciones)
scripts/     Pipeline de generación
normativa.html   Visor autocontenido (datos embebidos, ~7.5 MB)
```

## Pipeline

```powershell
# Ley y Reglamento (LeyesBiblio, .doc convertido con Word COM)
python scripts/parse_ordenamiento.py

# RGCE: base DOF -> anexos 1/2/22/24/30 -> resoluciones de modificaciones (orden obligatorio)
# (los .txt de los PDF del SAT se generan con pdftotext; Anexo 1 en modo -layout)
python scripts/parse_rgce.py
python scripts/parse_anexos.py
python scripts/aplicar_modificaciones.py   # 1a RM y 2a RM, con historial

# Reglas SE e IMMEX (PDF compilados, texto extraído con pdfminer.six); Acuerdos SE posteriores al compilado
python scripts/parse_se.py
python scripts/aplicar_modificaciones_se.py   # Acuerdos SE DOF 28-05, 29-05 y 28-09-2026, con historial
python scripts/parse_immex.py

# Referencias cruzadas y visor
python scripts/extraer_referencias.py
python scripts/generar_indice.py
python scripts/build_html.py
python scripts/verificar.py      # compara con HEAD: ninguna entrada perdida, todo texto cambiado con historial
```

Todo lo anterior en un paso, en el orden obligatorio y con la verificación al final: `python scripts/actualizar.py`.

## Vigilancia (qué se publicó y qué falta aplicar)

```powershell
python scripts/vigilar_dof.py     # escribe vigilancia\ultimo_reporte.md; código 2 = hay algo por revisar
```

Revisa el DOF día por día (API pública de SIDOF) desde la `ultima_reforma` de cada ordenamiento de `data\index.json`,
los documentos del minisitio RGCE del SAT (versiones anticipadas y compilados nuevos desde la corrida anterior) y la
portada de los PDF de LeyesBiblio (LA y RLA). Lo ya revisado se anota en `vigilancia\atendidas.json` (codNota → estado)
y deja de salir como pendiente. También lista los archivos que OneDrive dejó solo en línea. Sin llaves ni servicios de pago.
Programada desde el 22-10-2026 con `scripts\programar_vigilancia.ps1`: tarea «normadu vigilancia DOF», lunes y jueves
a las 08:30 (Programador de tareas de Windows). La misma tarea hace antes `git pull --ff-only` del clon de solo lectura
`C:\Users\Jaime V. Rob\Dev\normadu` (clonado de GitHub, push deshabilitado), que usan los agentes de otros espacios de
trabajo. El clon refleja lo que está en GitHub: un merge local sin push no le llega hasta el siguiente push.

## Cómo actualizar cuando se publique una modificación

1. **RGCE (SAT)** — fuente de verdad: https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/index.html
   Descargar la resolución del DOF (`nota_to_doc.php?codnota=XXXX`), codificar los parches en
   `scripts/aplicar_modificaciones.py` (con anclas de texto y `historial`), y re-correr el pipeline RGCE.
2. **Reglas SE** — mientras SNICE no publique compilado nuevo: descargar el Acuerdo del DOF
   (`https://sidof.segob.gob.mx/notas/getDoc/<codNota>`, convertir con Word a texto), guardarlo como
   `fuentes/reglas_se_mod_dof_AAAAMMDD.doc/.txt` y codificar sus cambios en `scripts/aplicar_modificaciones_se.py`
   (anclas + `historial`). Cuando SNICE publique un compilado que ya incluya esos Acuerdos, reemplazar
   `fuentes/reglas_se_compilado.pdf`, re-correr `parse_se.py`, cotejar y quitar del script los Acuerdos ya incluidos.
3. **IMMEX / Ley / Reglamento** — igual: reemplazar la fuente compilada y re-parsear.
4. Siempre terminar con `python scripts/actualizar.py` (pipeline + `verificar.py`) y commit cuando el owner lo pida
   (el historial de git es el registro de versiones del sistema). Anotar la nota del DOF en `vigilancia\atendidas.json`.

Cada regla, ficha, formato o apéndice modificado conserva su texto anterior en `historial` (visible en el visor como
"Texto anterior") y cada resolución queda asentada en `data/modificaciones.json`. El Glosario y los Transitorios
de las RGCE, que son bloques de texto, guardan su texto anterior en `glosario_historial` y `transitorios_historial`
de `rgce.json`. Las entradas del Anexo 1 cuyo formato se publicó como imagen llevan `nota_fuente`.

Los textos nuevos de la 2a RM se leen de `fuentes/` (no se transcriben): reglas, Glosario, Transitorio y Anexo 22 de
`rgce2026_2rm_anexos_1_2_22_dof_20260922_celdas.txt` (el .doc del DOF, una celda por línea); fichas del Anexo 2 y
formatos del Anexo 1 de los PDF del SAT de cada modificación. Si un ancla no se encuentra, el script truena.

## Referencias cruzadas

- RGCE: tomadas de las **correlaciones oficiales del SAT** al pie de cada regla (4,400+ referencias).
- LA/RLA/RCSE/IMMEX: extraídas del texto por patrones ("artículo 36-A de la Ley", "regla 1.5.1.", etc.).
- En el visor: chips al inicio de cada artículo + citas clicables dentro del texto.
  Chips grises = ordenamientos aún no integrados (CFF, RMF, LIGIE, LCE…).

## Esquema JSON (por artículo/regla)

```json
{
  "id": "RGCE-1.5.1",
  "numero": "1.5.1",
  "epigrafe": "Manifestación de valor",
  "titulo": "1", "titulo_nombre": "…", "capitulo": "1.5", "capitulo_nombre": "…",
  "texto": "…",
  "correlaciones": "Ley 59, 59-A, … RGCE 6.2.1., Anexo 1",
  "referencias": [{"ord": "LA", "art": "59"}],
  "notas_reforma": ["… 1a RM RGCE 2026, DOF 14-05-2026"],
  "historial": [{"vigente_hasta": "14-05-2026", "texto": "…", "fuente_anterior": "…"}]
}
```

## Idioma

Español primero. La versión en inglés se agregará como campo `texto_en` por entrada sin cambiar la estructura.

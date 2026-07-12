# Normadu — Normativa Aduanera Mexicana

Directorio consultable de las disposiciones legales aplicables al comercio exterior mexicano, con referencias cruzadas entre ordenamientos. Visor 100% estático: abre `normativa.html` en el navegador, sin servidor ni dependencias.

## Ordenamientos

| Id | Ordenamiento | Fuente | Estado |
|----|--------------|--------|--------|
| LA | Ley Aduanera | Cámara de Diputados (LeyesBiblio) | ✅ integrado |
| RLA | Reglamento de la Ley Aduanera | Cámara de Diputados (LeyesBiblio) | ✅ integrado |
| RGCE | Reglas Generales de Comercio Exterior (SAT) | SAT / DOF | ⏳ fase 2 |
| RCSE | Reglas y Criterios de Comercio Exterior (Secretaría de Economía) | DOF / SNICE | ⏳ fase 2 |
| IMMEX | Decreto IMMEX (completo) | DOF | ⏳ fase 2 |
| — | RGCE Anexo 22 y Anexo 24 | SAT / DOF | ⏳ fase 2 |

## Estructura

```
fuentes/     Textos fuente descargados (.doc de LeyesBiblio + .txt convertidos)
data/        JSON estructurado por ordenamiento (artículo, jerarquía, texto, referencias)
scripts/     Pipeline de generación
normativa.html   Visor autocontenido (datos embebidos)
```

## Pipeline

```powershell
python scripts/parse_ordenamiento.py    # fuentes/*.txt -> data/*.json
python scripts/extraer_referencias.py   # detecta citas cruzadas y las escribe en data/
python scripts/build_html.py            # data/*.json -> normativa.html
```

La conversión `.doc → .txt` se hace una vez con Word (COM) al descargar una nueva versión del texto consolidado.

## Esquema JSON (por artículo)

```json
{
  "id": "LA-36-A",
  "numero": "36-A",
  "titulo": "Segundo", "titulo_nombre": "…",
  "capitulo": "III", "capitulo_nombre": "…",
  "seccion": null, "seccion_nombre": null,
  "texto": "…",
  "notas_reforma": ["Párrafo reformado DOF 19-11-2025"],
  "referencias": [{"ord": "LA", "art": "6"}, {"ord": "RGCE", "art": "1.9.19"}]
}
```

## Versionado

Cada JSON registra `ultima_reforma` y fecha de generación. Las RGCE y las Reglas de SE se modifican varias veces al año; el registro de resoluciones se lleva a partir del inicio del sistema para acumular histórico:

- RGCE: minisitio SAT — https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/index.html
- Reglas SE: SNICE / DOF

## Idioma

Español primero. La versión en inglés se agregará como campo `texto_en` por artículo sin cambiar la estructura.

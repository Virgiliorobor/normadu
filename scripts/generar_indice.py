# -*- coding: utf-8 -*-
"""Genera data/index.json: manifiesto para que agentes/LLMs descubran y consuman
los ordenamientos por URL raw sin navegar GitHub. Correr al final del pipeline."""
import json
import sys
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
RAW = "https://raw.githubusercontent.com/Virgiliorobor/normadu/main/data/"

ARCHIVOS = ["ley_aduanera.json", "reglamento_la.json", "rgce.json", "reglas_se.json", "immex.json"]


def main():
    ordenamientos = []
    for nombre in ARCHIVOS:
        f = DATA / nombre
        if not f.exists():
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        ordenamientos.append({
            "id": d["id"],
            "nombre": d["nombre"],
            "tipo": d["tipo"],
            "archivo": nombre,
            "url_raw": RAW + nombre,
            "publicacion_original": d.get("publicacion_original"),
            "ultima_reforma": d.get("ultima_reforma"),
            "total_articulos": d.get("total_articulos"),
            "fuente_oficial": d.get("fuente_url"),
        })
    manifiesto = {
        "proyecto": "normadu — Normativa Aduanera Mexicana en JSON estructurado",
        "descripcion": "Textos vigentes de la normativa de comercio exterior de México, un JSON por ordenamiento. Cada entrada de 'articulos' tiene: id, numero, epigrafe, jerarquía (titulo/capitulo/seccion), texto, referencias [{ord, art}], notas_reforma e historial (textos anteriores a cada reforma).",
        "actualizado": date.today().isoformat(),
        "esquema_referencias": "ord = id del ordenamiento destino (LA, RLA, RGCE, RCSE, IMMEX) o externo (CFF, RMF, LIVA, LIEPS, LISR, LFD, LCE, RLCE, LIGIE); art = número de artículo/regla, o 'anexo-N'.",
        "registro_modificaciones": RAW + "modificaciones.json",
        "visor_html": "https://github.com/Virgiliorobor/normadu/blob/main/normativa.html (autocontenido; descargar y abrir)",
        "ordenamientos": ordenamientos,
    }
    (DATA / "index.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"index.json: {len(ordenamientos)} ordenamientos")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

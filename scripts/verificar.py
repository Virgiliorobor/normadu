# -*- coding: utf-8 -*-
"""Verificaciones del corpus después del pipeline. Compara data/ con una versión de git
(por omisión HEAD) para comprobar que ninguna reforma se perdió sin historial.

Falla (código 1) si:
- un JSON no carga, o hay ids repetidos;
- desaparece una entrada que existía en la versión base;
- cambió el texto de una entrada y no se agregó una entrada nueva a su `historial`;
- se acortó o reescribió un `historial` existente;
- una referencia a un ordenamiento del corpus tiene `art` vacío;
- `ultima_reforma` de index.json no coincide con la del JSON;
- normativa.html no contiene la `ultima_reforma` de cada ordenamiento.
Avisa (sin fallar) de referencias a artículos que no existen en el corpus.

Uso: python scripts/verificar.py [--base REF]
"""
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
ARCHIVOS = ["ley_aduanera.json", "reglamento_la.json", "rgce.json", "reglas_se.json", "immex.json"]
CORPUS = {"LA", "RLA", "RGCE", "RCSE", "IMMEX"}


def de_git(ref, ruta):
    r = subprocess.run(["git", "-C", str(BASE), "show", f"{ref}:{ruta}"], capture_output=True)
    return json.loads(r.stdout.decode("utf-8")) if r.returncode == 0 else None


def main():
    ref = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else "HEAD"
    errores, avisos, resumen = [], [], []
    ids_por_ord, datos = {}, {}
    for nombre in ARCHIVOS:
        d = json.loads((DATA / nombre).read_text(encoding="utf-8"))
        datos[nombre] = d
        ids = [a["id"] for a in d["articulos"]]
        if len(ids) != len(set(ids)):
            errores.append(f"{nombre}: ids repetidos {sorted({i for i in ids if ids.count(i) > 1})}")
        ids_por_ord[d["id"]] = set(ids)

    for nombre, d in datos.items():
        previo = de_git(ref, f"data/{nombre}")
        cambiadas = nuevas = 0
        if previo:
            ahora = {a["id"]: a for a in d["articulos"]}
            for a in previo["articulos"]:
                b = ahora.get(a["id"])
                if b is None:
                    errores.append(f"{nombre}: desapareció {a['id']}")
                    continue
                ha, hb = a.get("historial", []), b.get("historial", [])
                if hb[:len(ha)] != ha:
                    errores.append(f"{nombre}: {a['id']}: el historial existente cambió o se acortó")
                if a["texto"] != b["texto"]:
                    cambiadas += 1
                    if len(hb) <= len(ha) or hb[-1].get("texto") != a["texto"]:
                        errores.append(f"{nombre}: {a['id']}: cambió el texto sin guardar el anterior en historial")
            nuevas = len(set(ahora) - {a["id"] for a in previo["articulos"]})
            for campo in ("glosario_historial", "transitorios_historial"):
                if d.get(campo, [])[:len(previo.get(campo, []))] != previo.get(campo, []):
                    errores.append(f"{nombre}: {campo} existente cambió o se acortó")
        resumen.append(f"{d['id']}: {len(d['articulos'])} entradas, última reforma {d.get('ultima_reforma')}; "
                       f"respecto de {ref}: {cambiadas} reformadas, {nuevas} nuevas")

        for a in d["articulos"]:
            for r in a.get("referencias", []):
                if r["ord"] in CORPUS and not r.get("art"):
                    errores.append(f"{nombre}: {a['id']}: referencia a {r['ord']} sin artículo")
                elif r["ord"] in CORPUS and f"{r['ord']}-{r['art']}" not in ids_por_ord.get(r["ord"], ()):
                    avisos.append(f"{a['id']} -> {r['ord']}-{r['art']}")

    index = json.loads((DATA / "index.json").read_text(encoding="utf-8"))
    html = (BASE / "normativa.html").read_text(encoding="utf-8")
    for o in index["ordenamientos"]:
        d = datos[o["archivo"]]
        if o["ultima_reforma"] != d.get("ultima_reforma"):
            errores.append(f"index.json: {o['id']} ultima_reforma {o['ultima_reforma']} ≠ {d.get('ultima_reforma')}")
        if f'"ultima_reforma": "{d.get("ultima_reforma")}"' not in html and d.get("ultima_reforma") not in html:
            errores.append(f"normativa.html: no contiene la última reforma de {o['id']} ({d.get('ultima_reforma')})")

    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(resumen))
    print(f"Referencias a artículos inexistentes en el corpus (aviso): {len(avisos)}")
    for x in avisos[:15]:
        print("  ", x)
    if errores:
        print(f"\nVERIFICACIÓN FALLIDA ({len(errores)}):")
        print("\n".join("  " + e for e in errores))
        return 1
    print("\nVerificación correcta.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

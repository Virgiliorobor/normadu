# -*- coding: utf-8 -*-
"""Extrae referencias cruzadas entre ordenamientos y las escribe en los JSON de data/.

Detecta:
  - "artículo(s) N[, N y N] ... de la Ley / de esta Ley"        -> LA
  - "artículo(s) N ... de este Reglamento / del Reglamento"     -> RLA
  - "artículo(s) N ... del Código Fiscal de la Federación"      -> CFF (externo)
  - "regla(s) N.N.N."                                           -> RGCE
"""
import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

NUM = r"\d+o?\.?(?:-[A-Z])?(?:\s+(?:bis|ter|qu[áa]ter)(?:\s+\d+)?)?"
# "artículos 36, 36-A y 37-A, fracción I, de la Ley" — captura la lista de números
# y el ordenamiento destino tras "de/del".
REF_ART = re.compile(
    rf"art[íi]culos?\s+((?:{NUM})(?:\s*(?:,|y|o|e)\s*(?:{NUM}))*)"
    r"[^;\.]{0,90}?\s+de\s+(la\s+Ley\b(?!\s+(?:de[l]?|Federal|General|del?\s|Aduanera\s+de))|esta\s+Ley\b|"
    r"la\s+Ley\s+Aduanera\b|este\s+Reglamento\b|el\s+Reglamento\b|del?\s+C[óo]digo\s+Fiscal\s+de\s+la\s+Federaci[óo]n)",
    re.IGNORECASE,
)
REF_REGLA = re.compile(r"reglas?\s+((?:\d+\.\d+\.\d+\.?)(?:\s*(?:,|y|o)\s*\d+\.\d+\.\d+\.?)*)", re.IGNORECASE)
NUM_TOKEN = re.compile(NUM)


def destino(frase, ord_actual):
    f = re.sub(r"\s+", " ", frase.lower())
    if "código fiscal" in f or "codigo fiscal" in f:
        return "CFF"
    if "reglamento" in f:
        return "RLA"
    return "LA"


def clave_articulo(tok):
    disp = re.sub(r"\s+", " ", tok.strip().rstrip("."))
    clave = disp[:-1] if disp.endswith("o") else disp
    return re.sub(r"\s+", "-", clave.lower()) if " " in clave else clave


def extrae(texto, ord_actual):
    refs = []
    vistos = set()

    def agrega(ord_dest, art):
        k = (ord_dest, art)
        if k not in vistos:
            vistos.add(k)
            refs.append({"ord": ord_dest, "art": art})

    for m in REF_ART.finditer(texto):
        ord_dest = destino(m.group(2), ord_actual)
        for t in NUM_TOKEN.findall(m.group(1)):
            agrega(ord_dest, clave_articulo(t))
    for m in REF_REGLA.finditer(texto):
        for r in re.findall(r"\d+\.\d+\.\d+", m.group(1)):
            agrega("RGCE", r)
    return refs


def main():
    total = {}
    for archivo in sorted(DATA.glob("*.json")):
        d = json.loads(archivo.read_text(encoding="utf-8"))
        n = 0
        for a in d.get("articulos", []):
            a["referencias"] = extrae(a["texto"], d["id"])
            n += len(a["referencias"])
        archivo.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        total[d["id"]] = n
        print(f"{d['nombre']}: {n} referencias extraidas")
    return total


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

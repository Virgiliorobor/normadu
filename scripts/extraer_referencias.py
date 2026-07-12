# -*- coding: utf-8 -*-
"""Extrae referencias cruzadas entre ordenamientos y las escribe en los JSON de data/.

- LA/RLA/RCSE/IMMEX: referencias detectadas en el texto de cada artículo/regla.
- RGCE: conserva las referencias derivadas de las correlaciones oficiales del SAT
  (generadas por parse_rgce.py); no se sobreescriben.
- Entradas con formato "pre" (anexos) no se procesan.
"""
import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

NUM = r"\d+o?\.?(?:-[A-Z])?(?:\s+(?:bis|ter|qu[áa]ter)(?:\s+\d+)?)?"
LISTA_NUM = rf"(?:{NUM})(?:\s*(?:,|y|o|e)\s*(?:{NUM}))*"

REF_ART = re.compile(
    rf"art[íi]culos?\s+({LISTA_NUM})"
    r"[^;\.]{0,90}?\s+de(?:l)?\s+"
    r"(la\s+Ley\s+Aduanera\b|la\s+Ley\b(?!\s+(?:de[l]?\s|Federal|General|Aduanera))|esta\s+Ley\b|"
    r"este\s+Reglamento\b|el\s+Reglamento\b|presente\s+Decreto\b|Decreto\s+IMMEX\b|"
    r"C[óo]digo\s+Fiscal\s+de\s+la\s+Federaci[óo]n|presente\s+(?:Acuerdo|ordenamiento)\b|LCE\b|RLCE\b)",
    re.IGNORECASE,
)
REF_REGLA = re.compile(
    r"reglas?\s+((?:\d+\.\d+\.\d+\.?)(?:\s*(?:,|y|o)\s*\d+\.\d+\.\d+\.?)*)"
    r"(\s+de\s+las\s+RGCE|\s+de\s+la\s+RMF)?",
    re.IGNORECASE,
)
REF_ANEXO = re.compile(r"Anexo\s+(22|24)\b(?!\s*\.\d)", re.IGNORECASE)
NUM_TOKEN = re.compile(NUM)


def destino_articulo(frase, ord_actual):
    f = re.sub(r"\s+", " ", frase.lower())
    if "código fiscal" in f or "codigo fiscal" in f:
        return "CFF"
    if "decreto immex" in f or "presente decreto" in f and ord_actual == "IMMEX":
        return "IMMEX"
    if "presente decreto" in f:
        return "IMMEX" if ord_actual == "IMMEX" else None
    if "presente acuerdo" in f or "presente ordenamiento" in f:
        return ord_actual if ord_actual == "RCSE" else None
    if f == "lce":
        return "LCE"
    if f == "rlce":
        return "RLCE"
    if "reglamento" in f:
        # en RCSE "el Reglamento" suele ser el RLCE; en LA/RLA/RGCE es el RLA
        return "RLCE" if ord_actual == "RCSE" else "RLA"
    if "ley aduanera" in f:
        return "LA"
    if "esta ley" in f or "la ley" in f:
        # en RCSE "la Ley" es la LCE; en LA/RLA/RGCE/IMMEX es la Ley Aduanera
        return "LCE" if ord_actual == "RCSE" else "LA"
    return None


def clave_articulo(tok):
    disp = re.sub(r"\s+", " ", tok.strip().rstrip("."))
    clave = disp[:-1] if disp.endswith("o") else disp
    return re.sub(r"\s+", "-", clave.lower()) if " " in clave else clave


def extrae(texto, ord_actual):
    refs, vistos = [], set()

    def agrega(ord_dest, art):
        k = (ord_dest, art)
        if ord_dest and k not in vistos:
            vistos.add(k)
            refs.append({"ord": ord_dest, "art": art})

    for m in REF_ART.finditer(texto):
        ord_dest = destino_articulo(m.group(2), ord_actual)
        for t in NUM_TOKEN.findall(m.group(1)):
            agrega(ord_dest, clave_articulo(t))
    for m in REF_REGLA.finditer(texto):
        suf = (m.group(2) or "").lower()
        if "rmf" in suf:
            ord_dest = "RMF"
        elif "rgce" in suf:
            ord_dest = "RGCE"
        else:
            ord_dest = "RCSE" if ord_actual == "RCSE" else "RGCE"
        for r in re.findall(r"\d+\.\d+\.\d+", m.group(1)):
            agrega(ord_dest, r)
    if ord_actual in ("LA", "RLA", "IMMEX"):
        for m in REF_ANEXO.finditer(texto):
            agrega("RGCE", f"anexo-{m.group(1)}")
    return refs


def main():
    for archivo in sorted(DATA.glob("*.json")):
        d = json.loads(archivo.read_text(encoding="utf-8"))
        if not isinstance(d, dict) or "articulos" not in d:
            continue
        n = conservadas = 0
        for a in d["articulos"]:
            if a.get("formato") == "pre":
                continue
            if d["id"] == "RGCE" and a.get("referencias"):
                conservadas += len(a["referencias"])
                continue
            a["referencias"] = extrae(a["texto"], d["id"])
            n += len(a["referencias"])
        archivo.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        extra = f" (+{conservadas} de correlaciones SAT)" if conservadas else ""
        print(f"{d['nombre']}: {n} referencias extraidas{extra}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

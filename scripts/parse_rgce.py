# -*- coding: utf-8 -*-
"""Parsea las RGCE (texto DOF convertido a .txt) a data/rgce.json.

Estructura fuente: Glosario -> Título N. -> Capítulo N.N. -> reglas "N.N.N.<TAB>texto".
Cada regla suele cerrar con una línea de correlaciones ("Ley 68, 162, CFF 49 Bis, ...")
y la línea previa a cada número de regla es su epígrafe.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FUENTES = BASE / "fuentes"
DATA = BASE / "data"

REGLA_RE = re.compile(r"^(\d+\.\d+\.\d+\.)\s*\t(.*)$")
TITULO_RE = re.compile(r"^T[íi]tulo\s+(\d+)\.\s*(.+)$")
CAPITULO_RE = re.compile(r"^Cap[íi]tulo\s+(\d+\.\d+)\.\s*(.+)$")
TRANSITORIOS_RE = re.compile(r"^\s*Transitorios\s*$")
ANEXO_RE = re.compile(r"^\s*ANEXO\s+\d+")

# Ordenamientos que aparecen en las líneas de correlaciones del SAT
TOKENS_ORD = {
    "Ley": "LA", "Reglamento": "RLA", "CFF": "CFF", "RGCE": "RGCE", "RMF": "RMF",
    "LIGIE": "LIGIE", "LIVA": "LIVA", "LIEPS": "LIEPS", "LFD": "LFD", "LISR": "LISR",
    "LISAN": "LISAN", "CPEUM": "CPEUM", "LFDC": "LFDC", "LFPCA": "LFPCA", "LCE": "LCE",
}
CORRELACION_FUERTE_RE = re.compile(
    r"^(Ley|Reglamento|CFF|RGCE|RMF|LIGIE|LIVA|LIEPS|LFD|LISR|LISAN|CPEUM|LFDC|LFPCA|LCE)\b[\s\d]"
)
CORRELACION_DEBIL_RE = re.compile(r"^(Anexos?|Decreto|Acuerdo|Resoluci[óo]n|Tratados)\b")


LEYES_NOMBRADAS = [
    (r"\bIVA\b", "LIVA"), (r"\bIEPS\b", "LIEPS"),
    (r"\bISR\b|Impuesto sobre la Renta", "LISR"),
    (r"Federal de Derechos", "LFD"), (r"Comercio Exterior", "LCE"),
    (r"Impuestos Generales", "LIGIE"), (r"\bISAN\b|Autom[óo]viles Nuevos", "LISAN"),
]


def _num_norm(a):
    a = a.strip().rstrip(".")
    a = a[:-1] if a.endswith("o") else a
    return re.sub(r"\s+", "-", a.lower()) if " " in a else a


def parse_correlaciones(texto):
    """'Ley 68, CFF 49 Bis, Ley del IVA 28-A, RGCE 1.9.16., Anexo 1' -> refs estructuradas."""
    refs = []
    ord_actual = None
    for p in re.split(r",", texto):
        p = p.strip().rstrip(".")
        if not p:
            continue
        # "Ley del IVA 28-A", "Ley Federal de Derechos 40": ley nombrada, NO es la Ley Aduanera
        m = re.match(r"^Ley\s+(del?\s|de\s+la\s|de\s+los\s|Federal\s|General\s)(.+)$", p, re.I)
        if m:
            ord_actual = next((o for pat, o in LEYES_NOMBRADAS if re.search(pat, p, re.I)), None)
            if ord_actual is None:
                refs.append({"ord": "EXT", "art": "", "nombre": p[:80]})
                ord_actual = "NOMBRADO"
                continue
            nums = re.findall(r"\d+[oO]?\.?(?:-[A-Z])?(?:\s+(?:Bis|bis|Ter|ter)(?:\s+\d+)?)?$", p)
            for a in nums:
                refs.append({"ord": ord_actual, "art": _num_norm(a)})
            continue
        # "Anexo 1", "Anexos 1 y 30", "RGCE Anexo 22", "Decreto IMMEX Anexo II"
        m = re.match(r"^(?:(RGCE)\s+)?Anexos?\s+(.+)$", p, re.I)
        if m:
            for n in re.findall(r"\d+[A-Za-z\-]*|[IVX]+(?:\s+(?:Bis|Ter))?", m.group(2)):
                refs.append({"ord": "RGCE", "art": f"anexo-{_num_norm(n)}"})
            ord_actual = "ANEXO"
            continue
        m = re.match(r"^(Decreto|Acuerdo|Resoluci[óo]n|Tratados)\b(.*)$", p, re.I)
        if m:
            if re.search(r"IMMEX", p, re.I):
                ma = re.search(r"Anexos?\s+([IVX]+(?:\s+(?:Bis|Ter))?|\d+)", p, re.I)
                refs.append({"ord": "IMMEX", "art": f"anexo-{_num_norm(ma.group(1)).lower()}" if ma else ""})
            else:
                refs.append({"ord": "EXT", "art": "", "nombre": p[:80]})
            ord_actual = "NOMBRADO"
            continue
        m = re.match(r"^([A-Z]{2,6}|Ley|Reglamento)\s+(.+)$", p)
        if m and m.group(1) in TOKENS_ORD:
            ord_actual = TOKENS_ORD[m.group(1)]
            p = m.group(2)
        if ord_actual in (None, "NOMBRADO"):
            continue
        if ord_actual == "ANEXO":
            if re.match(r"^\d+[A-Za-z\-]*$", p):
                refs.append({"ord": "RGCE", "art": f"anexo-{p}"})
            continue
        # "Anexo 22" tras un ordenamiento: "RGCE 1.9.16., Anexo 22"
        ma = re.match(r"^Anexos?\s+(.+)$", p, re.I)
        if ma:
            for n in re.findall(r"\d+[A-Za-z\-]*", ma.group(1)):
                refs.append({"ord": "RGCE", "art": f"anexo-{n}"})
            continue
        arts = re.findall(r"\d+\.\d+\.\d+|\d+[oO]?(?:-[A-Z])?(?:\s+(?:Bis|Ter|bis|ter)(?:\s+\d+)?)?", p)
        for a in arts:
            refs.append({"ord": ord_actual, "art": _num_norm(a)})
    # dedup
    vistos, unicos = set(), []
    for r in refs:
        k = (r["ord"], r["art"], r.get("nombre", ""))
        if k not in vistos:
            vistos.add(k)
            unicos.append(r)
    return unicos


def es_correlacion(linea):
    s = linea.strip()
    if s.endswith(":"):
        return False
    if CORRELACION_FUERTE_RE.match(s):
        return True
    # "Anexo 22" / "Decreto IMMEX 5" sí; "Acuerdo conclusivo en PAMA" (epígrafe) no
    return bool(CORRELACION_DEBIL_RE.match(s)) and bool(re.search(r"\d", s))


def main():
    texto = (FUENTES / "rgce2026_dof.txt").read_text(encoding="cp1252")
    lines = texto.splitlines()

    # localizar inicio del cuerpo (primer 'Título 1.' fuera del índice) y del glosario
    inicio = next(i for i, l in enumerate(lines) if TITULO_RE.match(l.strip()) and l.strip().startswith("Título 1"))
    try:
        glos_ini = next(i for i, l in enumerate(lines[:inicio]) if l.strip() == "Glosario" and i > 20)
    except StopIteration:
        glos_ini = None
    glosario = "\n".join(l.strip() for l in lines[glos_ini:inicio] if l.strip()) if glos_ini else ""

    reglas = []
    titulo = titulo_nombre = capitulo = capitulo_nombre = None
    actual = None
    epigrafe_pendiente = []
    transitorios = []
    posterior = []
    estado = "cuerpo"

    def cierra():
        nonlocal actual, epigrafe_pendiente
        if actual is None:
            return
        actual.pop("_tras_correl", None)
        cuerpo = actual.pop("_lineas")

        def poda_blancos():
            while cuerpo and not cuerpo[-1].strip():
                cuerpo.pop()

        # al final de una regla vienen: [texto..., correlaciones..., epígrafe de la siguiente]
        poda_blancos()
        candidato = []
        while (cuerpo and cuerpo[-1].strip() and not es_correlacion(cuerpo[-1])
               and len(candidato) < 3 and len(cuerpo[-1]) < 200
               and not cuerpo[-1].rstrip().endswith((".", ":", ";"))
               and (not cuerpo[-1].rstrip().endswith(")") or "(" in cuerpo[-1])):
            candidato.insert(0, cuerpo.pop())
            poda_blancos()
        correl = []
        while cuerpo and es_correlacion(cuerpo[-1]):
            correl.insert(0, cuerpo.pop())
            poda_blancos()
        sig_epigrafe = candidato
        actual["texto"] = "\n".join(cuerpo).strip()
        actual["correlaciones"] = " ".join(correl).strip()
        actual["referencias"] = parse_correlaciones(", ".join(correl)) if correl else []
        reglas.append(actual)
        actual = None
        if sig_epigrafe:
            epigrafe_pendiente = sig_epigrafe

    i = inicio
    while i < len(lines):
        raw = lines[i]
        s = raw.strip()
        i += 1

        if estado == "posterior":
            posterior.append(raw)
            continue
        if estado == "transitorios":
            if ANEXO_RE.match(s):
                estado = "posterior"
                posterior.append(raw)
            else:
                transitorios.append(s)
            continue
        if TRANSITORIOS_RE.match(s):
            cierra()
            estado = "transitorios"
            continue

        m = TITULO_RE.match(s)
        if m and not raw.startswith("\t"):
            cierra()
            titulo, titulo_nombre = m.group(1), m.group(2).strip()
            capitulo = capitulo_nombre = None
            epigrafe_pendiente = []
            continue
        m = CAPITULO_RE.match(s)
        if m and not raw.startswith("\t"):
            cierra()
            capitulo, capitulo_nombre = m.group(1), m.group(2).strip()
            epigrafe_pendiente = []
            continue

        m = REGLA_RE.match(raw)
        if m:
            cierra()
            num = m.group(1).rstrip(".")
            actual = {
                "id": f"RGCE-{num}",
                "numero": num,
                "epigrafe": " ".join(x.strip() for x in epigrafe_pendiente).strip(),
                "titulo": titulo,
                "titulo_nombre": titulo_nombre,
                "capitulo": capitulo,
                "capitulo_nombre": capitulo_nombre,
                "seccion": None,
                "seccion_nombre": None,
                "notas_reforma": [],
                "historial": [],
                "_lineas": [f"{m.group(1)} {m.group(2).strip()}"],
            }
            epigrafe_pendiente = []
            continue

        if actual is not None:
            if not s:
                actual["_lineas"].append("")
            elif es_correlacion(s):
                actual["_lineas"].append(s)
                actual["_tras_correl"] = True
            elif actual.get("_tras_correl"):
                # tras la línea de correlaciones solo puede venir el epígrafe de la siguiente regla
                epigrafe_pendiente.append(s)
            else:
                actual["_lineas"].append(s)
        elif s:
            epigrafe_pendiente.append(s)

    cierra()

    out = {
        "id": "RGCE",
        "nombre": "Reglas Generales de Comercio Exterior 2026",
        "tipo": "reglas",
        "fuente_url": "https://www.dof.gob.mx/nota_detalle.php?codigo=5777199&fecha=27/12/2025",
        "publicacion_original": "DOF 27-12-2025",
        "vigencia": "01-01-2026 al 31-12-2026",
        "ultima_reforma": None,
        "generado": date.today().isoformat(),
        "glosario": glosario,
        "total_articulos": len(reglas),
        "articulos": reglas,
        "transitorios": "\n".join(transitorios).strip(),
        "material_posterior": "\n".join(posterior).strip(),
    }
    DATA.mkdir(exist_ok=True)
    (DATA / "rgce.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    nums = [r["numero"] for r in reglas]
    dups = sorted({n for n in nums if nums.count(n) > 1})
    con_epigrafe = sum(1 for r in reglas if r["epigrafe"])
    con_refs = sum(1 for r in reglas if r["referencias"])
    print(f"RGCE: {len(reglas)} reglas | duplicadas: {dups if dups else 'ninguna'} | "
          f"con epígrafe: {con_epigrafe} | con correlaciones: {con_refs} | glosario: {len(glosario)} chars")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

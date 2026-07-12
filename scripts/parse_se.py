# -*- coding: utf-8 -*-
"""Parsea el Acuerdo de Reglas y Criterios de Comercio Exterior de la SE
(compilado SNICE en PDF -> texto pdfminer) a data/reglas_se.json."""
import json
import re
import sys
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FUENTES = BASE / "fuentes"
DATA = BASE / "data"

REGLA_RE = re.compile(r"^(\d{1,2}\.\d{1,2}\.\d{1,3}(?:\s+(?:BIS|TER))?)\.?\s+([A-ZÁÉÍÓÚÑ\"«(].*)$")
TITULO_RE = re.compile(r"^T[ÍI]TULO\s+(\d+)\.?\s*(.*)$")
CAPITULO_RE = re.compile(r"^Cap[íi]tulo\s+(\d+\.\d+)\.?\s*(.*)$")
ANEXO_RE = re.compile(r"^ANEXO\s+[\d\.]+")
PAGINA_RE = re.compile(r"^\s*\d+\s*$")
MARCADOR_RE = re.compile(r"^([IVXL]+\.|[a-z]\)|[A-Z]\)|\d+\)|[A-Z]\.\s)")


def limpia(s):
    return re.sub(r"\s+", " ", s).strip()


def parrafos(lineas):
    """Reconstruye párrafos de texto PDF con líneas envueltas."""
    out, buf = [], []
    for l in lineas:
        s = l.strip()
        if not s:
            if buf:
                out.append(limpia(" ".join(buf)))
                buf = []
            continue
        if MARCADOR_RE.match(s) and buf:
            out.append(limpia(" ".join(buf)))
            buf = []
        buf.append(s)
    if buf:
        out.append(limpia(" ".join(buf)))
    return "\n".join(out)


def main():
    lines = (FUENTES / "reglas_se.txt").read_text(encoding="utf-8").splitlines()

    modificaciones = [limpia(l).strip("() ") for l in lines[:30]
                      if re.search(r"(Publicaci[óo]n|Modificaci[óo]n),?\s*DOF", l)]

    # cuerpo: del TITULO 1 posterior al índice hasta el primer ANEXO
    tit1 = [i for i, l in enumerate(lines) if re.match(r"^\s*TITULO\s+1", l.strip())]
    inicio = next(i for i in tit1 if i > 250)
    fin = next(i for i, l in enumerate(lines) if ANEXO_RE.match(l.strip()) and i > inicio)

    reglas = []
    titulo = titulo_nombre = capitulo = capitulo_nombre = None
    actual = None
    pend_nombre = None  # continuación de nombre de título/capítulo en la línea siguiente
    resto = []

    def cierra():
        nonlocal actual
        if actual is not None:
            actual["texto"] = f"{actual['numero']} " + parrafos(actual.pop("_lineas"))
            reglas.append(actual)
            actual = None

    i = inicio
    while i < fin:
        raw = lines[i]
        s = raw.strip()
        i += 1
        if PAGINA_RE.match(s) or "DOCUMENTO REFERENCIAL" in s:
            continue

        m = TITULO_RE.match(s)
        if m:
            cierra()
            titulo, titulo_nombre = m.group(1), limpia(m.group(2))
            capitulo = capitulo_nombre = None
            pend_nombre = "titulo"
            continue
        m = CAPITULO_RE.match(s)
        if m:
            cierra()
            capitulo, capitulo_nombre = m.group(1), limpia(m.group(2))
            pend_nombre = "capitulo"
            continue
        m = REGLA_RE.match(s)
        if m:
            cierra()
            pend_nombre = None
            num = limpia(m.group(1))
            actual = {
                "id": f"RCSE-{num.lower().replace(' ', '-')}",
                "numero": num,
                "epigrafe": "",
                "titulo": titulo,
                "titulo_nombre": titulo_nombre,
                "capitulo": capitulo,
                "capitulo_nombre": capitulo_nombre,
                "seccion": None,
                "seccion_nombre": None,
                "notas_reforma": [],
                "historial": [],
                "referencias": [],
                "_lineas": [m.group(2)],
            }
            continue

        # continuación de nombres de título/capítulo en mayúsculas o líneas siguientes cortas
        if pend_nombre and s and actual is None:
            if pend_nombre == "titulo" and (s.isupper() or not titulo_nombre):
                titulo_nombre = limpia((titulo_nombre + " " + s))
                continue
            if pend_nombre == "capitulo" and not REGLA_RE.match(s) and len(s) < 90 and not s.isupper():
                # nombres de capítulo pueden continuar una línea
                if capitulo_nombre and (s[0].islower() or capitulo_nombre.endswith(("de", "la", "y", "del", "en"))):
                    capitulo_nombre = limpia(capitulo_nombre + " " + s)
                    continue
            pend_nombre = None

        if actual is not None:
            # notas de reforma estilo "(Regla reformada DOF ...)" o "Regla adicionada DOF..."
            if re.match(r"^\(?(Regla|P[áa]rrafo|Fracci[óo]n|Inciso|Numeral|Cap[íi]tulo|T[íi]tulo)\s.*(reformad|adicionad|derogad|modificad)", s, re.I):
                actual["notas_reforma"].append(limpia(s).strip("()"))
            else:
                actual["_lineas"].append(raw)
        elif s:
            resto.append(s)

    cierra()

    # anexos disponibles (solo se registran, el contenido son tablas de fracciones)
    anexos = []
    for j in range(fin, len(lines)):
        s = lines[j].strip()
        if ANEXO_RE.match(s) and len(s) < 40:
            anexos.append(s)

    out = {
        "id": "RCSE",
        "nombre": "Reglas y Criterios de Comercio Exterior (SE)",
        "tipo": "reglas",
        "fuente_url": "https://www.snice.gob.mx/~oracle/SNICE_DOCS/ACUERDO-REGLAS-SE-02ABRIL2026-BIBLIOTECA_20260520-20260520.pdf",
        "publicacion_original": "DOF 09-05-2022",
        "ultima_reforma": "02-04-2026",
        "modificaciones": modificaciones,
        "generado": date.today().isoformat(),
        "total_articulos": len(reglas),
        "articulos": reglas,
        "transitorios": "",
        "material_posterior": "",
        "anexos_disponibles": anexos,
        "nota_anexos": "Los anexos del Acuerdo SE (listas de fracciones arancelarias) no se cargan en el visor; consultar el PDF compilado de SNICE.",
    }
    DATA.mkdir(exist_ok=True)
    (DATA / "reglas_se.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    nums = [r["numero"] for r in reglas]
    dups = sorted({n for n in nums if nums.count(n) > 1})
    print(f"RCSE: {len(reglas)} reglas | duplicadas: {dups if dups else 'ninguna'} | "
          f"modificaciones registradas: {len(modificaciones)} | anexos detectados: {len(anexos)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

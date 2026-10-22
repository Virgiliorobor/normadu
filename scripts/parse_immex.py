# -*- coding: utf-8 -*-
"""Parsea el Decreto IMMEX (compilado SNICE en PDF -> texto pdfminer) a data/immex.json."""
import json
import re
import sys
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FUENTES = BASE / "fuentes"
DATA = BASE / "data"

ART_RE = re.compile(r"^ART[ÍI]CULO\s+(\d+(?:\s+(?:BIS|TER))?)(?!\.?\d)\s*\.\s*-\s*(.*)$", re.I)
CAPITULO_RE = re.compile(r"^Cap[íi]tulo\s+([IVX]+)\s*$")
TRANS_RE = re.compile(r"^TRANSITORIOS?\s+(?:DEL?\s+)?(.+)$")
ANEXO_RE = re.compile(r"^ANEXO\s+([IVX]+(?:\s+(?:BIS|TER))?)\s*$")
PAGINA_RE = re.compile(r"^\s*\d+\s*$")
NOTA_RE = re.compile(
    r"^\(?(Art[íi]culo|P[áa]rrafo|Fracci[óo]n|Inciso|Cap[íi]tulo|Denominaci[óo]n|Anexo)\s.*"
    r"(reformad|adicionad|derogad|modificad)\w*\s.*DOF", re.I)
MARCADOR_RE = re.compile(r"^([IVXL]+\.|[a-z]\)|[A-Z]\)|\d+\)|[IVXL]+\.-|[a-z]\.-)")


def limpia(s):
    return re.sub(r"\s+", " ", s).strip()


def parrafos(lineas):
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


# En el texto pdfminer del compilado SNICE, los "Se deroga." de los Anexos I BIS, I TER, III y IV
# quedan al final de los Anexos I y II, y la nota "Anexo reformado DOF 01-01-2016" (que en el PDF
# está bajo el Anexo III) queda en el Anexo II. Se corrige aquí con el orden del PDF (pdftotext
# -layout). La derogación de los Anexos I BIS, I TER y III es del Decreto publicado en el DOF el
# 06-01-2016, Artículo SEGUNDO (fuentes/immex_dof_20160106.doc); el compilado SNICE la anota como
# "DOF 01-01-2016".
DEROGA_2016 = ("Anexo derogado por el Decreto por el que se modifica el diverso para el Fomento de la Industria "
               "Manufacturera, Maquiladora y de Servicios de Exportación, DOF 06-01-2016, Artículo SEGUNDO "
               "(en vigor a los 30 días naturales siguientes a su publicación)")
ANEXOS_DEROGADOS = {
    "IMMEX-anexo-i-bis": [DEROGA_2016],
    "IMMEX-anexo-i-ter": [DEROGA_2016],
    "IMMEX-anexo-iii": [DEROGA_2016, "El compilado SNICE anota: Anexo reformado DOF 01-01-2016"],
    "IMMEX-anexo-iv": ["El compilado SNICE no consigna el decreto que derogó este anexo"],
}


def corrige_anexos_derogados(articulos):
    por_id = {a["id"]: a for a in articulos}
    for id_ in ("IMMEX-anexo-i", "IMMEX-anexo-ii"):
        a = por_id[id_]
        assert a["texto"].endswith("\nSe deroga.\nSe deroga."), f"{id_}: 'Se deroga.' desplazados no encontrados"
        a["texto"] = a["texto"][:-len("\nSe deroga.\nSe deroga.")]
    ii = por_id["IMMEX-anexo-ii"]
    assert "Anexo reformado DOF 01-01-2016" in ii["notas_reforma"]
    ii["notas_reforma"].remove("Anexo reformado DOF 01-01-2016")
    for id_, notas in ANEXOS_DEROGADOS.items():
        a = por_id[id_]
        assert a["texto"].strip() == a["numero"], f"{id_}: se esperaba vacío"
        a["texto"] = a["numero"] + " Se deroga."
        a["notas_reforma"] = notas


def main():
    lines = (FUENTES / "decreto_immex.txt").read_text(encoding="utf-8").splitlines()

    articulos = []
    capitulo = capitulo_nombre = None
    actual = None
    espera_nombre_cap = False
    transitorios = []
    estado = "cuerpo"
    anexo_actual = None

    def cierra():
        nonlocal actual
        if actual is not None:
            pref = actual["numero"] if actual["numero"].startswith("Anexo") else f"ARTÍCULO {actual['numero']}.-"
            actual["texto"] = f"{pref} " + parrafos(actual.pop("_lineas"))
            articulos.append(actual)
            actual = None

    for raw in lines:
        s = raw.strip()
        if PAGINA_RE.match(s) or "DOCUMENTO REFERENCIAL" in s.upper():
            continue

        m = TRANS_RE.match(s)
        if m and len(s) < 60:
            cierra()
            estado = "transitorios"
            transitorios.append("")
            transitorios.append(f"TRANSITORIOS {m.group(1)}")
            continue
        m = ANEXO_RE.match(s)
        if m:
            cierra()
            estado = "anexo"
            num = m.group(1)
            actual = {
                "id": f"IMMEX-anexo-{num.lower().replace(' ', '-')}",
                "numero": f"Anexo {num}",
                "epigrafe": "",
                "titulo": None, "titulo_nombre": None,
                "capitulo": None, "capitulo_nombre": "Anexos del Decreto",
                "seccion": None, "seccion_nombre": None,
                "notas_reforma": [], "historial": [], "referencias": [],
                "_lineas": [],
            }
            continue

        if estado == "transitorios":
            if s:
                transitorios.append(s)
            continue

        m = CAPITULO_RE.match(s)
        if m and estado == "cuerpo":
            cierra()
            capitulo, capitulo_nombre = m.group(1), None
            espera_nombre_cap = True
            continue
        if espera_nombre_cap and s:
            capitulo_nombre = limpia(s)
            espera_nombre_cap = False
            continue

        m = ART_RE.match(s)
        if m and estado == "cuerpo":
            cierra()
            num = limpia(m.group(1)).upper().replace("  ", " ")
            num_disp = num.replace("BIS", "Bis").replace("TER", "Ter")
            clave = num_disp.lower().replace(" ", "-")
            actual = {
                "id": f"IMMEX-{clave}",
                "numero": num_disp,
                "epigrafe": "",
                "titulo": None, "titulo_nombre": None,
                "capitulo": capitulo, "capitulo_nombre": capitulo_nombre,
                "seccion": None, "seccion_nombre": None,
                "notas_reforma": [], "historial": [], "referencias": [],
                "_lineas": [m.group(2)],
            }
            continue

        if actual is not None:
            if NOTA_RE.match(s):
                actual["notas_reforma"].append(limpia(s).strip("()"))
            else:
                actual["_lineas"].append(raw)

    cierra()
    corrige_anexos_derogados(articulos)

    out = {
        "id": "IMMEX",
        "nombre": "Decreto IMMEX",
        "tipo": "decreto",
        "fuente_url": "https://www.snice.gob.mx/~oracle/SNICE_DOCS/DECRETO-IMMEX-BIBLIOTECA_20250925-20250925.08.2025).pdf",
        "publicacion_original": "DOF 01-11-2006",
        "ultima_reforma": "28-08-2025",
        "generado": date.today().isoformat(),
        "total_articulos": len(articulos),
        "articulos": articulos,
        "transitorios": "\n".join(transitorios).strip(),
        "material_posterior": "",
    }
    DATA.mkdir(exist_ok=True)
    (DATA / "immex.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    nums = [a["numero"] for a in articulos]
    dups = sorted({n for n in nums if nums.count(n) > 1})
    anexos = [n for n in nums if n.startswith("Anexo")]
    print(f"IMMEX: {len(articulos)} entradas ({len(nums)-len(anexos)} artículos + {len(anexos)} anexos: {anexos}) | "
          f"duplicados: {dups if dups else 'ninguno'} | transitorios: {len(out['transitorios'])} chars")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

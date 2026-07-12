# -*- coding: utf-8 -*-
"""Parsea textos consolidados de LeyesBiblio (Camara de Diputados) a JSON estructurado.

Uso: python parse_ordenamiento.py
Genera data/ley_aduanera.json y data/reglamento_la.json
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FUENTES = BASE / "fuentes"
DATA = BASE / "data"

ORDENAMIENTOS = [
    {
        "id": "LA",
        "nombre": "Ley Aduanera",
        "tipo": "ley",
        "archivo": "LAdua.txt",
        "salida": "ley_aduanera.json",
        "fuente_url": "https://www.diputados.gob.mx/LeyesBiblio/doc/LAdua.doc",
    },
    {
        "id": "RLA",
        "nombre": "Reglamento de la Ley Aduanera",
        "tipo": "reglamento",
        "archivo": "Reg_LAdua.txt",
        "salida": "reglamento_la.json",
        "fuente_url": "https://www.diputados.gob.mx/LeyesBiblio/regley/Reg_LAdua.doc",
    },
]

ART_RE = re.compile(
    r"^\s*ART[ÍI]CULO\.?\s+(\d+o?\.?(?:-[A-Z])?(?:\s+(?:bis|ter|qu[áa]ter)(?:\s+\d+)?)?)\s*[\.\-]",
    re.IGNORECASE,
)
TITULO_RE = re.compile(r"^\s*T[ÍI]TULO\s+([A-ZÁÉÍÓÚa-záéíóú]+)\s*$", re.IGNORECASE)
CAPITULO_RE = re.compile(r"^\s*CAP[ÍI]TULO\s+([IVXL]+|[ÚU]nico|[ÚU]NICO)\s*$", re.IGNORECASE)
SECCION_RE = re.compile(r"^\s*SECCI[ÓO]N\s+([A-ZÁÉÍÓÚa-záéíóú]+)\s*$", re.IGNORECASE)
TRANSITORIOS_RE = re.compile(r"^\s*TRANSITORIOS?\s*$")
# Notas del editor de LeyesBiblio: "Párrafo reformado DOF ...", "Fracción adicionada DOF ..."
NOTA_RE = re.compile(
    r"^\s*(P[áa]rrafo|Fracci[óo]n|Art[íi]culo|Inciso|Denominaci[óo]n|Secci[óo]n|Cap[íi]tulo|Ep[íi]grafe|Rubro|Tabla|Apartado)s?\s.*"
    r"(reformad|adicionad|derogad|recorrid|reubicad)\w*\s.*DOF",
    re.IGNORECASE,
)
NOTA_SIMPLE_RE = re.compile(r"^\s*(Reforma|Fe de erratas)\s+DOF", re.IGNORECASE)


def normaliza_numero(raw):
    """'1o.' -> ('1o.', '1') ; '14-A.' -> ('14-A', '14-A')"""
    disp = re.sub(r"\s+", " ", raw.strip().rstrip("."))
    clave = disp[:-1] if disp.endswith("o") else disp
    clave = re.sub(r"\s+", "-", clave.lower()) if " " in clave else clave
    return disp, clave


def parse_header(lines):
    meta = {}
    for l in lines[:15]:
        s = l.strip()
        m = re.search(r"publicad[oa] en el Diario Oficial de la Federaci[óo]n el (.+)$", s)
        if m and "publicacion_original" not in meta:
            meta["publicacion_original"] = m.group(1).strip()
        m = re.search(r"[ÚU]ltima reforma publicada DOF\s+([\d\-]+)", s)
        if m:
            meta["ultima_reforma"] = m.group(1)
        m = re.search(r"Cantidades actualizadas por .*DOF\s+([\d\-]+)", s)
        if m:
            meta["cantidades_actualizadas"] = m.group(1)
    return meta


def es_encabezado_nombre(line):
    """Linea corta que nombra un titulo/capitulo/seccion (sigue al encabezado)."""
    s = line.strip()
    return 0 < len(s) < 120 and not ART_RE.match(line) and not NOTA_RE.match(line)


def parse_body(lines, ord_id):
    articulos = []
    titulo = capitulo = seccion = None
    titulo_nombre = capitulo_nombre = seccion_nombre = None
    actual = None  # articulo en construccion
    pendiente_nombre = None  # 'titulo' | 'capitulo' | 'seccion'
    transitorios = []
    resto = []
    estado = "cuerpo"

    def cierra():
        nonlocal actual
        if actual is not None:
            actual["texto"] = "\n".join(actual["_lineas"]).strip()
            del actual["_lineas"]
            articulos.append(actual)
            actual = None

    for line in lines:
        s = line.rstrip()
        stripped = s.strip()

        if estado == "posterior":
            resto.append(s)
            continue
        if estado == "transitorios":
            # Un encabezado mayor (REGLAS..., DECRETO..., ANEXO...) inicia material posterior
            if re.match(r"^(REGLAS |DECRETO |ANEXO |ACUERDO )", stripped):
                estado = "posterior"
                resto.append(s)
            else:
                transitorios.append(s)
            continue

        if TRANSITORIOS_RE.match(stripped):
            cierra()
            estado = "transitorios"
            transitorios.append(stripped)
            continue

        m = TITULO_RE.match(stripped)
        if m and len(stripped) < 40:
            cierra()
            titulo, pendiente_nombre = m.group(1).title(), "titulo"
            capitulo = capitulo_nombre = seccion = seccion_nombre = None
            continue
        m = CAPITULO_RE.match(stripped)
        if m and len(stripped) < 40:
            cierra()
            capitulo, pendiente_nombre = m.group(1).upper() if m.group(1).lower() != "único" else "Único", "capitulo"
            seccion = seccion_nombre = None
            continue
        m = SECCION_RE.match(stripped)
        if m and len(stripped) < 40:
            cierra()
            seccion, pendiente_nombre = m.group(1).title(), "seccion"
            continue

        if pendiente_nombre and stripped and es_encabezado_nombre(s):
            if pendiente_nombre == "titulo":
                titulo_nombre = stripped
            elif pendiente_nombre == "capitulo":
                capitulo_nombre = stripped
            else:
                seccion_nombre = stripped
            pendiente_nombre = None
            continue
        if pendiente_nombre and (NOTA_RE.match(s) or not stripped):
            if NOTA_RE.match(s):
                pendiente_nombre = None
            continue

        m = ART_RE.match(s)
        if m:
            cierra()
            disp, clave = normaliza_numero(m.group(1))
            actual = {
                "id": f"{ord_id}-{clave}",
                "numero": disp,
                "titulo": titulo,
                "titulo_nombre": titulo_nombre,
                "capitulo": capitulo,
                "capitulo_nombre": capitulo_nombre,
                "seccion": seccion,
                "seccion_nombre": seccion_nombre,
                "notas_reforma": [],
                "referencias": [],
                "_lineas": [stripped],
            }
            continue

        if actual is not None:
            if NOTA_RE.match(s) or NOTA_SIMPLE_RE.match(s):
                actual["notas_reforma"].append(stripped)
            elif stripped:
                actual["_lineas"].append(stripped)
            else:
                actual["_lineas"].append("")

    cierra()
    return articulos, "\n".join(transitorios).strip(), "\n".join(resto).strip()


def main():
    DATA.mkdir(exist_ok=True)
    for cfg in ORDENAMIENTOS:
        texto = (FUENTES / cfg["archivo"]).read_text(encoding="cp1252")
        lines = texto.splitlines()
        meta = parse_header(lines)
        articulos, transitorios, posterior = parse_body(lines, cfg["id"])
        out = {
            "id": cfg["id"],
            "nombre": cfg["nombre"],
            "tipo": cfg["tipo"],
            "fuente_url": cfg["fuente_url"],
            "generado": date.today().isoformat(),
            **meta,
            "total_articulos": len(articulos),
            "articulos": articulos,
            "transitorios": transitorios,
            "material_posterior": posterior,
        }
        destino = DATA / cfg["salida"]
        destino.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        ids = [a["id"] for a in articulos]
        dups = {i for i in ids if ids.count(i) > 1}
        print(f"{cfg['nombre']}: {len(articulos)} articulos -> {destino.name}"
              f" | ultima_reforma={meta.get('ultima_reforma')} | duplicados={sorted(dups) if dups else 'ninguno'}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
